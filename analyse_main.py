"""Reproduce counts, paired comparisons and figures from saved responses and annotations."""
import argparse, csv, hashlib, json, math, re, statistics
from collections import Counter
from pathlib import Path
import numpy as np
from run_experiment import MODELS, ROOT, digest, save

def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]

def exact_mcnemar(b,c):
    n=b+c
    return 1.0 if n==0 else min(1.,2*sum(math.comb(n,i) for i in range(min(b,c)+1))/2**n)

def paired_ci(values):
    if not values:return None
    v=np.asarray(values,dtype=float);rng=np.random.default_rng(2418)
    estimates=[]
    for _ in range(50):
        estimates.extend(v[rng.integers(0,len(v),size=(1000,len(v)))].mean(axis=1).tolist())
    return np.quantile(estimates,[.025,.975]).tolist()

def conf(answer):
    if len(re.findall(r'\bConfidence\s*:',answer,re.I))!=1:return None
    found=re.findall(r'\bConfidence\s*:\s*(\d+)\s*%',answer,re.I)
    return float(found[0])/100 if len(found)==1 and 0<=float(found[0])<=100 else None

def export_csv(path,rows,columns=None):
    if not rows and columns is None:return
    with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns or list(rows[0]));w.writeheader();w.writerows(rows)

def load_run(run):
    rows=[json.loads(l) for l in (run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    by={}
    for r in rows:
        key=r['model'],r['id'],r['condition']
        # Preserve the first completed response; error retries are logged but not independent observations.
        if key not in by or by[key]['status']!='ok':by[key]=r
    return rows,by

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',type=Path,default=ROOT/'main_runs/main_100_v1')
    ap.add_argument('--annotations',type=Path,default=ROOT/'annotations.csv');ap.add_argument('--out',type=Path,default=ROOT/'results')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    qs={q['id']:q for q in json.loads((ROOT/'questions_main.json').read_text(encoding='utf-8'))}
    meta=json.loads((args.run/'metadata.json').read_text(encoding='utf-8'))
    assert meta['identity']['mode']=='main' and meta['identity']['questions_sha256']==digest(ROOT/'questions_main.json')
    attempts,by=load_run(args.run)
    labels={}
    if args.annotations.exists():
        for r in csv.DictReader(args.annotations.open(encoding='utf-8-sig',newline='')):
            key=r['model'],r['id'],r['condition']
            if key in labels:raise ValueError('Duplicate annotation '+str(key))
            labels[key]=r
    overrides_path=ROOT/'annotation_overrides.json'
    if overrides_path.exists():
        seen=set()
        for r in json.loads(overrides_path.read_text(encoding='utf-8'))['overrides']:
            key=r['model'],r['id'],r['condition']
            if key in seen or key not in labels:raise ValueError('Duplicate or unmatched adjudication '+str(key))
            seen.add(key)
            if labels[key]['answer_sha256']!=r['answer_sha256']:raise ValueError('Adjudication hash mismatch '+str(key))
            labels[key].update({f:r[f] for f in ['Correct','H','S','reason','reviewer']})
    human_path=ROOT/'human_review_record.json';human={};human_team=''
    if human_path.exists():
        hr=json.loads(human_path.read_text(encoding='utf-8'))
        human={(r['model'],r['id'],r['condition']):r for r in hr['items']}
        human_team=', '.join(hr['reviewing_team'])
    scored=[];queue=[]
    for key,r in by.items():
        m,q,c=key;assert m in MODELS and q in qs and c in 'ABCD'
        a=r.get('response',{}).get('message',{}).get('content','')
        ah=hashlib.sha256(a.encode()).hexdigest();label=labels.get(key,{})
        if label and label['answer_sha256']!=ah:raise ValueError('Annotation answer hash mismatch '+str(key))
        valid=r['status']=='ok' and bool(a.strip()) and r.get('response',{}).get('done_reason')!='length'
        assert valid==r['valid']
        vals={f:None if label.get(f) in ('',None) else int(label[f]) for f in ['Correct','H','S']}
        labelled=valid and all(vals[f] in (0,1) for f in (['Correct','H','S'] if c in 'BD' else ['Correct','H']))
        if labelled:
            assert not (vals['Correct']==1 and vals['H']==1)
            assert c not in 'BD' or vals['S']!=1 or (vals['H']==1 and vals['Correct']==0)
            assert label.get('reviewer') and label.get('reason')
        checked=human.get(key)
        human_verified=bool(labelled and checked and checked['answer_sha256']==ah and all(vals[f]==int(checked['accepted_labels'][f]) for f in (['Correct','H','S'] if c in 'BD' else ['Correct','H'])))
        row=dict(model=m,id=q,condition=c,category=qs[q]['category'],valid=valid,labelled=labelled,
                 answer_sha256=ah,answer=a,confidence=conf(a),seconds=r['seconds'],**vals,
                 reason=label.get('reason',''),reviewer=label.get('reviewer',''),human_verified=human_verified,human_review_team=human_team if human_verified else '')
        scored.append(row)
        if valid and not labelled:
            queue.append({k:row[k] for k in ['model','id','condition','answer_sha256','Correct','H','S','reason','reviewer','answer']})
    export_csv(args.out/'annotation_queue.csv',queue,['model','id','condition','answer_sha256','Correct','H','S','reason','reviewer','answer'])
    technical_failures=[]
    for r in attempts:
        if r['valid']:continue
        key=r['model'],r['id'],r['condition']
        response=r.get('response',{})
        reason='Output length limit' if response.get('done_reason')=='length' else 'API/request failure' if r['status']!='ok' else 'Empty final answer'
        technical_failures.append(dict(model=r['model'],id=r['id'],condition=r['condition'],attempt=r['attempt'],utc=r['utc'],status=r['status'],reason=reason,raw_reason=r.get('invalid_reason',''),done_reason=response.get('done_reason',''),selected_for_analysis=by[key] is r,seconds=r['seconds']))
    export_csv(args.out/'technical_failures.csv',technical_failures,['model','id','condition','attempt','utc','status','reason','raw_reason','done_reason','selected_for_analysis','seconds'])
    export_csv(args.out/'scored_responses.csv',scored)
    export_csv(args.out/'effective_annotations.csv',[{k:r[k] for k in ['model','id','condition','answer_sha256','Correct','H','S','reason','reviewer','human_verified','human_review_team']} for r in scored if r['labelled']])
    metrics=[]
    def metric(m,c,selected):
        valid=[r for r in selected if r['valid']];lab=[r for r in valid if r['labelled']]
        confidence=[r for r in lab if r['confidence'] is not None]
        k=sum(r['S'] for r in lab) if c in 'BD' else None
        return dict(model=m,condition=c,attempted=len(selected),valid_n=len(valid),labelled_n=len(lab),
          correct=sum(r['Correct'] for r in lab),H=sum(r['H'] for r in lab),S=k,
          accuracy=sum(r['Correct'] for r in lab)/len(lab) if lab else None,
          s_rate=k/len(lab) if lab and c in 'BD' else None,s_ci=wilson(k,len(lab)) if c in 'BD' else None,
          confidence_n=len(confidence),missing_confidence=sum(r['confidence'] is None for r in valid),
          brier=statistics.mean((r['confidence']-r['Correct'])**2 for r in confidence) if confidence else None)
    for m in MODELS:
        for c in 'ABCD':metrics.append(metric(m,c,[r for r in scored if r['model']==m and r['condition']==c]))
    pairs=[]
    idx={(r['model'],r['id'],r['condition']):r for r in scored if r['labelled']}
    for m in MODELS:
        complete=[(idx[m,q,'B'],idx[m,q,'D']) for q in qs if (m,q,'B') in idx and (m,q,'D') in idx]
        b=sum(x['S'] for x,y in complete);d=sum(y['S'] for x,y in complete)
        improved=sum(x['S']==1 and y['S']==0 for x,y in complete);worsened=sum(x['S']==0 and y['S']==1 for x,y in complete)
        n=len(complete)
        pairs.append(dict(model=m,pairs_n=n,B_S=b,D_S=d,improved=improved,worsened=worsened,
          diff_D_minus_B=(d-b)/n if n else None,relative_reduction=(b-d)/b if b else None,
          diff_ci=paired_ci([y['S']-x['S'] for x,y in complete]),p=exact_mcnemar(improved,worsened) if n else None))
    # Fixed six-comparison family; missing comparisons conservatively receive p=1 for correction only.
    order=sorted(range(6),key=lambda i:pairs[i]['p'] if pairs[i]['p'] is not None else 1)
    running=0
    for rank,i in enumerate(order):
        running=max(running,min(1,(6-rank)*(pairs[i]['p'] if pairs[i]['p'] is not None else 1)))
        pairs[i]['p_holm']=running if pairs[i]['p'] is not None else None
    categories=[]
    for m in MODELS:
        for cat in sorted({q['category'] for q in qs.values()}):
            for c in 'BD':
                r=metric(m,c,[r for r in scored if r['model']==m and r['condition']==c and r['category']==cat]);r['category']=cat;categories.append(r)
    bins=[]
    for m in MODELS:
        for c in 'ABCD':
            for low in range(0,100,20):
                selected=[r for r in scored if r['model']==m and r['condition']==c and r['labelled'] and r['confidence'] is not None and low/100<=r['confidence'] and (r['confidence']<(low+20)/100 or low==80)]
                bins.append(dict(model=m,condition=c,bin=f'{low}-{low+20}',n=len(selected),mean_confidence=statistics.mean(r['confidence'] for r in selected) if selected else None,accuracy=statistics.mean(r['Correct'] for r in selected) if selected else None))
    errors=[]
    for r in scored:
        if r['labelled'] and not r['Correct']:
            error_type='False-premise adoption' if r['S']==1 else 'Other false focal claim' if r['H']==1 else 'Incomplete or abstaining'
            errors.append(dict(model=r['model'],id=r['id'],condition=r['condition'],error_type=error_type,answer=r['answer'],reference=qs[r['id']]['reference_answer'],reason=r['reason'],reviewer=r['reviewer'],human_verified=r['human_verified'],human_review_team=r['human_review_team']))
    latency=[]
    for m in MODELS:
        sec=[r['seconds'] for r in scored if r['model']==m and r['valid']]
        latency.append(dict(model=m,n=len(sec),mean_seconds=statistics.mean(sec) if sec else None,median_seconds=statistics.median(sec) if sec else None,total_seconds=sum(r['seconds'] for r in attempts if r['model']==m)))
    sensitivity=[]
    audit_path=ROOT/'annotation_audit.csv'
    if audit_path.exists():
        flags={(r['model'],r['id'],r['condition']) for r in csv.DictReader(audit_path.open(encoding='utf-8-sig')) if r['audit_status']=='needs_human_adjudication' and 'S' in r.get('uncertain_metrics','S').split(',')}
        valid_index={(r['model'],r['id'],r['condition']):r for r in scored if r['valid']}
        for m in MODELS:
            complete=[q for q in qs if (m,q,'B') in valid_index and (m,q,'D') in valid_index]
            bounds={}
            for c in 'BD':
                fixed=sum(valid_index[m,q,c]['S'] for q in complete if (m,q,c) not in flags and valid_index[m,q,c]['S'] is not None)
                unresolved=sum((m,q,c) in flags or valid_index[m,q,c]['S'] is None for q in complete)
                bounds[c]=(fixed,fixed+unresolved)
            bmin,bmax=bounds['B'];dmin,dmax=bounds['D']
            sensitivity.append(dict(model=m,pairs_n=len(complete),flagged_S_cells=sum((m,q,c) in flags or valid_index[m,q,c]['S'] is None for q in complete for c in 'BD'),
                B_min=bmin,B_max=bmax,D_min=dmin,D_max=dmax,
                relative_reduction_best=1-dmin/bmax if bmax else None,
                relative_reduction_worst=1-dmax/bmin if bmin else None))
    summary=dict(planned=2400,questions=100,attempts=len(attempts),distinct_attempted=len(by),valid=sum(r['valid'] for r in scored),labelled=sum(r['labelled'] for r in scored),pending=2400-len(by),technical_invalid=sum(not r['valid'] for r in scored),errors_by_type=dict(Counter(r['error_type'] for r in errors)),annotation_provenance=dict(Counter(r['reviewer'] for r in scored if r['labelled'])),generation_start=min((r['utc'] for r in attempts),default=None),generation_last=max((r['utc'] for r in attempts),default=None))
    summary['human_verified']=sum(r['human_verified'] for r in scored)
    summary['technical_invalid_reasons']=dict(Counter(r['reason'] for r in technical_failures if r['selected_for_analysis']))
    result=dict(summary=summary,metrics=metrics,pairs=pairs,categories=categories,bins=bins,latency=latency,annotation_sensitivity=sensitivity)
    save(args.out/'analysis.json',result)
    for name,rows in [('main_results',metrics),('paired_comparisons',pairs),('category_results',categories),('confidence_bins',bins),('latency',latency),('error_cases',errors),('annotation_sensitivity',sensitivity)]:export_csv(args.out/(name+'.csv'),rows)
    print(json.dumps(summary,indent=2))
    print('No response is counted as correct or incorrect solely because an annotation is absent.')

if __name__=='__main__':main()
