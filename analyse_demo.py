"""Summarize a saved demonstration using explicit reference examples only."""
import argparse,json
from pathlib import Path
from run_experiment import ROOT,MODELS,save
from demo_scoring import score_answer,summarize

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path);ap.add_argument('--latest',action='store_true');args=ap.parse_args()
    if args.latest:
        logs=list((ROOT/'demo_runs').glob('*/responses.jsonl'))
        if not logs:raise SystemExit('No demonstration logs exist.')
        run=max(logs,key=lambda p:p.stat().st_mtime).parent
    elif args.run:run=args.run
    else:raise SystemExit('Use --run PATH or --latest.')
    metadata=json.loads((run/'metadata.json').read_text(encoding='utf-8'))
    assert metadata['identity']['mode']=='demo','This rubric is only for the old demonstration questions.'
    rows=[json.loads(l) for l in (run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    for row in rows:
        text=row.get('response',{}).get('message',{}).get('content','')
        row['evaluation']=score_answer(text,row['id'],row['condition'],row['valid'])
    result=[]
    print('\nDEMONSTRATION ONLY — saved answers, provisional exact-reference labels')
    print('Model                      valid  H/labelled  S/labelled  REVIEW')
    for model in metadata['identity']['models']:
        s=summarize([r for r in rows if r['model']==model]);result.append(dict(model=model,**s))
        print(f"{model:<26} {s['valid']:>3}    {s['H_count']}/{s['H_denominator']:<6}    {s['S_count']}/{s['S_denominator']:<6}    {s['manual_review_required']}")
    print('H = false focal claim; S = agreement with supplied false premise in B/D.')
    print('REVIEW means unfamiliar wording: inspect the saved answer against the reference. It is not a zero.')
    print('These are demo results, not the 100-question main study. No new inference was requested.')
    save(run/'demo_summary.json',result)
    print('Saved:',run/'demo_summary.json')

if __name__=='__main__':main()
