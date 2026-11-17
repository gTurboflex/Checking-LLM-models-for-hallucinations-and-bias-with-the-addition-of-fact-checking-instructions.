"""Supplementary numbers reported in the final manuscript that are not in main_results.csv.

Reads only results/scored_responses.csv (produced by analyse_main.py) and writes
results/manuscript_extra.csv. No model calls; standard library only.

Outputs, per model:
  * A->B paired correctness changes and exact two-sided McNemar p (exploratory, unadjusted)
    -> manuscript Section 4.2
  * B->D paired correctness changes -> manuscript Section 4.4
  * answers with stated confidence >= 80% and their accuracy (all conditions pooled)
    -> manuscript Table 5 (last two columns) and Section 4.5
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = ['qwen3:1.7b', 'qwen3:4b-q4_K_M', 'qwen3:8b', 'gemma4:e2b', 'beam:cloud', 'gemma4:31b-cloud']


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def paired(lab, model, ids, c1, c2):
    pairs = [(int(lab[(model, i, c1)]['Correct']), int(lab[(model, i, c2)]['Correct']))
             for i in ids if (model, i, c1) in lab and (model, i, c2) in lab]
    lost = sum(1 for p in pairs if p == (1, 0))
    gained = sum(1 for p in pairs if p == (0, 1))
    return len(pairs), sum(p[0] for p in pairs), sum(p[1] for p in pairs), lost, gained


def main():
    rows = list(csv.DictReader((ROOT / 'results/scored_responses.csv').open(encoding='utf-8-sig')))
    lab = {(r['model'], r['id'], r['condition']): r for r in rows if r['labelled'] == 'True'}
    ids = sorted({r['id'] for r in rows})
    out = []
    for m in MODELS:
        n_ab, a_ok, b_ok, a_lost, a_gain = paired(lab, m, ids, 'A', 'B')
        n_bd, b2_ok, d_ok, d_lost, d_gain = paired(lab, m, ids, 'B', 'D')
        conf = [r for k, r in lab.items() if k[0] == m and r['confidence'] != '']
        high = [r for r in conf if float(r['confidence']) >= 0.8]
        high_ok = sum(int(r['Correct']) for r in high)
        out.append({
            'model': m,
            'AB_pairs': n_ab, 'A_correct': a_ok, 'B_correct': b_ok,
            'AB_correct_to_incorrect': a_lost, 'AB_incorrect_to_correct': a_gain,
            'AB_exact_mcnemar_p_unadjusted': f'{mcnemar_exact(a_lost, a_gain):.4g}',
            'BD_pairs': n_bd, 'BD_B_correct': b2_ok, 'BD_D_correct': d_ok,
            'BD_incorrect_to_correct': d_gain, 'BD_correct_to_incorrect': d_lost,
            'confidence_n': len(conf), 'high_conf_n': len(high),
            'high_conf_share_pct': f'{100 * len(high) / len(conf):.1f}' if conf else '',
            'high_conf_accuracy_pct': f'{100 * high_ok / len(high):.1f}' if high else '',
        })
    path = ROOT / 'results/manuscript_extra.csv'
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)
    print('Wrote', path)


if __name__ == '__main__':
    main()
