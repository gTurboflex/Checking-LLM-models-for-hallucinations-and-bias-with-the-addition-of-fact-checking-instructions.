"""Display saved main results and inspect one question. No network/inference."""
import csv,json
from pathlib import Path
from run_experiment import ROOT,MODELS

def main():
    path=ROOT/'results/analysis.json'
    if not path.exists():raise SystemExit('Run analyse_main.py first. No inference was started.')
    d=json.loads(path.read_text(encoding='utf-8'));s=d['summary']
    print('SAVED MAIN RESULTS — no new model requests')
    print('100 TruthfulQA questions; 4 conditions; 6 models.')
    print('Planned:',s['planned'],'Attempted:',s['distinct_attempted'],'Valid:',s['valid'],'Labelled:',s['labelled'],'Pending:',s['pending'])
    print('Human-verified selected cases:',s.get('human_verified',0))
    print('\nModel                      C   n   G   H   S   Brier  nConf')
    for r in d['metrics']:
        ss='NA' if r['S'] is None else str(r['S']);b='NA' if r['brier'] is None else f"{r['brier']:.3f}"
        print(f"{r['model']:<26} {r['condition']} {r['labelled_n']:>3} {r['correct']:>3} {r['H']:>3} {ss:>3} {b:>7} {r['confidence_n']:>5}")
    print('n = labelled answers; G = correct; H = false focal claim; S = adopted false premise (B/D only).')
    print('Exact labels and review status: results/effective_annotations.csv. Missing values are not zeros.')
    try:qid=input('\nQuestion ID to inspect (for example TQA640), or Enter to close: ').strip().upper()
    except EOFError:return
    if not qid:return
    qs={q['id']:q for q in json.loads((ROOT/'questions_main.json').read_text(encoding='utf-8'))}
    if qid not in qs:raise SystemExit('Unknown question ID. See questions_main.json.')
    q=qs[qid];print('\nQUESTION:',q['neutral']);print('REFERENCE:',q['reference_answer']);print('FALSE PREMISE:',q['false_premise'])
    rows=[json.loads(l) for l in (ROOT/'main_runs/main_100_v1/responses.jsonl').read_text(encoding='utf-8').splitlines()]
    for r in sorted([r for r in rows if r['id']==qid],key=lambda r:(MODELS.index(r['model']),r['condition'],r['attempt'])):
        print('\n',r['model'],r['condition'],'attempt',r['attempt'],r['status'])
        print(r.get('response',{}).get('message',{}).get('content',r.get('error','')))
    try:input('\nPress Enter to close.')
    except EOFError:pass

if __name__=='__main__':main()
