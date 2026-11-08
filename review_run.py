"""Read saved answers with references; no network requests."""
import argparse,json
from pathlib import Path
from run_experiment import ROOT,MODELS

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--id');args=ap.parse_args()
    metadata=json.loads((args.run/'metadata.json').read_text(encoding='utf-8'))
    mode=metadata['identity']['mode']
    questions={q['id']:q for q in json.loads((ROOT/('questions_main.json' if mode=='main' else 'questions_demo.json')).read_text(encoding='utf-8'))}
    rows=[json.loads(l) for l in (args.run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    print('SAVED LOG REPLAY. This does not generate new answers or consume cloud quota.')
    for r in sorted(rows,key=lambda r:(r['id'],MODELS.index(r['model']),r['condition'],r.get('attempt',1))):
        if args.id and r['id']!=args.id:continue
        q=questions[r['id']]
        print('\n',r['id'],r['model'],r['condition'],r['status'],'valid=',r.get('valid'))
        print('QUESTION:',q['neutral']);print('REFERENCE:',q['reference_answer'])
        print('FALSE PREMISE:',q['false_premise'])
        print('RESPONSE:',r.get('response',{}).get('message',{}).get('content',r.get('error','')))
        print('Time:',round(r['seconds'],2),'seconds')

if __name__=='__main__':main()
