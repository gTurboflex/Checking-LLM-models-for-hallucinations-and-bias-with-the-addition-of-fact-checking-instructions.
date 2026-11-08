"""Check provenance, request identity and complete coverage without any model calls."""
import argparse,csv,datetime,json
from collections import Counter
from pathlib import Path
from run_experiment import ROOT,MODELS,request,verify_freeze,digest

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--allow-incomplete',action='store_true');args=ap.parse_args()
    freeze=verify_freeze()
    qs=json.loads((ROOT/'questions_main.json').read_text(encoding='utf-8'))
    source=list(csv.DictReader((ROOT/'source/TruthfulQA.csv').open(encoding='utf-8-sig')))
    assert len(qs)==100 and len({q['id'] for q in qs})==100 and len({q['original_question'] for q in qs})==100
    for q in qs:
        s=source[q['source_row']]
        assert q['original_question']==s['Question'] and q['reference_answer']==s['Best Answer'] and q['false_premise']==s['Best Incorrect Answer']
    old=json.loads((ROOT/'historical_pilot/questions.json').read_text(encoding='utf-8'))
    assert not {q['source_question'] for q in old}&{q['original_question'] for q in qs}
    idx={q['id']:q for q in qs};run=ROOT/'main_runs/main_100_v1'
    plan=json.loads((run/'plan.json').read_text(encoding='utf-8'))
    expected={(m,q['id'],c) for m in MODELS for q in qs for c in 'ABCD'}
    assert len(plan)==2400 and {(r['model'],r['id'],r['condition']) for r in plan}==expected
    rows=[json.loads(l) for l in (run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    seen=Counter()
    for r in rows:
        key=r['model'],r['id'],r['condition'];assert key in expected
        assert r['request']==request(r['model'],idx[r['id']],r['condition'])
        seen[key]+=1;assert r['attempt']==seen[key]
        assert datetime.datetime.fromisoformat(r['utc'])>=datetime.datetime.fromisoformat(freeze['created_utc'])
        answer=r.get('response',{}).get('message',{}).get('content','')
        valid=r['status']=='ok' and bool(answer.strip()) and r.get('response',{}).get('done_reason')!='length'
        assert valid==r['valid']
        if r['status']=='ok':assert r['response'].get('done') is True
    if not args.allow_incomplete:
        assert set(seen)==expected,'Main coverage is incomplete.'
        result=json.loads((ROOT/'results/analysis.json').read_text(encoding='utf-8'))
        assert result['summary']['pending']==0
        assert result['summary']['labelled']<=result['summary']['valid']
        print('Unresolved valid responses retained in annotation queue:',result['summary']['valid']-result['summary']['labelled'])
        assert len(result['metrics'])==24 and len(result['pairs'])==6
        assert all(x['valid_n']<=100 and x['labelled_n']<=x['valid_n'] for x in result['metrics'])
    print(json.dumps(dict(source_rows=len(source),main_questions=len(qs),categories=dict(Counter(q['category'] for q in qs)),
        planned_slots=2400,distinct_attempted=len(seen),attempts=len(rows),frozen_files_verified=True,
        all_requests_match_protocol=True,pilot_overlap=0,complete=len(seen)==2400),indent=2))

if __name__=='__main__':main()
