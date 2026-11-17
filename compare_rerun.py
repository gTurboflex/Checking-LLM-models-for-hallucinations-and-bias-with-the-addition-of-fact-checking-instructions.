"""Compare a new live run with the saved main run (main_runs/main_100_v1).

Usage:  python compare_rerun.py main_runs/<your_new_run_folder>
        python compare_rerun.py --latest      (newest folder in main_runs)
Prints, per model, how many answers are byte-identical to the saved answers.
Standard library only. Labels (correct / hallucination / sycophancy) are NOT
recomputed here: new answers must be annotated with SCORING.txt first.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / 'main_runs' / 'main_100_v1'


def load(folder):
    latest = {}
    for line in (folder / 'responses.jsonl').read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        latest[r['model'], r['id'], r['condition']] = r
    return latest


def text(r):
    return (r.get('response') or {}).get('message', {}).get('content', '').strip() if r.get('valid') else None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == '--latest':
        runs = [d for d in (ROOT / 'main_runs').iterdir()
                if d.is_dir() and d.name != ORIGINAL.name and (d / 'responses.jsonl').exists()]
        if not runs:
            sys.exit('No new run found in main_runs. Run run_experiment.py --mode main first.')
        new_dir = max(runs, key=lambda d: d.stat().st_mtime)
    else:
        new_dir = Path(sys.argv[1])
    print('New run:', new_dir)
    old, new = load(ORIGINAL), load(new_dir)
    old_meta = json.loads((ORIGINAL / 'metadata.json').read_text(encoding='utf-8'))
    new_meta = json.loads((new_dir / 'metadata.json').read_text(encoding='utf-8'))
    print('Ollama version  saved run:', old_meta['ollama'].get('version'), '| new run:', new_meta['ollama'].get('version'))
    stats = defaultdict(lambda: [0, 0, 0])  # compared, identical, new_invalid
    for key, r in new.items():
        if key not in old or text(old[key]) is None:
            continue
        s = stats[key[0]]
        s[0] += 1
        t = text(r)
        if t is None:
            s[2] += 1
        elif t == text(old[key]):
            s[1] += 1
    print(f'\n{"model":20} {"compared":>9} {"identical":>10} {"share":>7} {"new invalid":>12}')
    for model, (n, same, bad) in stats.items():
        print(f'{model:20} {n:9d} {same:10d} {100*same/max(n,1):6.1f}% {bad:12d}')
    print('\nLocal models use temperature 0 and seed 2418, so identical builds usually give identical text.')
    print('Cloud models get no seed and can change on the provider side, so lower agreement is expected.')


if __name__ == '__main__':
    main()
