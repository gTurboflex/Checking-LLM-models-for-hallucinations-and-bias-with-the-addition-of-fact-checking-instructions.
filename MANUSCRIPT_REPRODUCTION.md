# Reproducing the final manuscript

Manuscript: `manuscript/Final_Manuscript_Information_Yergun_Danial_Diyar.docx`
(target journal: *Information*, MDPI).

Every table, figure and number in the Results section is regenerated offline from the
saved responses and annotations. No model is contacted.

## Commands

Run these from the package root (Python 3.12, `pip install -r requirements.txt`):

```
python validate_package.py                              # provenance and coverage checks
python analyse_main.py                                  # results/*.csv and results/analysis.json
python make_figures.py                                  # figures/ (220 dpi, as in Assignment 4)
python make_figures.py --dpi 600 --out figures/manuscript   # figures exported for the manuscript
python manuscript_extra_analysis.py                     # results/manuscript_extra.csv
```

On Windows, `Reproduce_Results.cmd` runs the main analysis.

## Where each result comes from

| Manuscript item | Output file | Columns / keys |
|---|---|---|
| Section 4.1 (2400 / 2391 / 2374 / 17 / 9, 1373 correct, 876 H, 30 missing confidence) | `results/analysis.json` → `summary`; `results/main_results.csv` | `valid`, `labelled`, `technical_invalid`; sums of `correct`, `H`, `missing_confidence` |
| Table 3 (G / H / n per model and condition) | `results/main_results.csv` | `correct`, `H`, `labelled_n` |
| Table 4 (primary B–D test) | `results/paired_comparisons.csv` | `pairs_n`, `B_S`, `D_S`, `improved`, `worsened`, `diff_D_minus_B`, `diff_ci`, `relative_reduction`, `p`, `p_holm` |
| Figure 1 | `figures/manuscript/figure1_agreement.png` | from `analysis.json` → `metrics` (`s_rate`, `s_ci`) |
| Figure 2 | `figures/manuscript/figure2_factual_errors.png` | from `analysis.json` → `metrics` (`H`, `labelled_n`) |
| Section 4.2 (A→B changes 42/2, 39/1, 46/2, 18/5, 5/2, 1/1; exploratory *p*) | `results/manuscript_extra.csv` | `AB_*` columns |
| Section 4.4 (B→D correctness changes 5/0, 30/1, 31/0, 7/0) | `results/manuscript_extra.csv` | `BD_*` columns |
| Table 5, Brier A–D and missing confidence | `results/main_results.csv` | `brier`, `missing_confidence` |
| Table 5, answers ≥80% confidence and their accuracy | `results/manuscript_extra.csv` (cross-check: `results/confidence_bins.csv`, bin `80-100`) | `high_conf_n`, `confidence_n`, `high_conf_share_pct`, `high_conf_accuracy_pct` |
| Table 6 (556 / 320 / 125; reviewed subset 16 / 11 / 3) | `results/analysis.json` → `summary.errors_by_type`; `human_review_record.json`, `human_review_selection.json` | — |
| Section 4.6 sensitivity bounds | `results/annotation_sensitivity.csv` | — |
| Section 4.6 latency | `results/latency.csv` | — |
| Appendix A (hashes, times) | `protocol_freeze.json`; `results/analysis.json` → `summary.generation_start`, `summary.generation_last` | — |
| Appendix B (example errors) | `results/error_cases.csv` | filter by model, id and condition |

## Notes

* `manuscript_extra_analysis.py` was added for the final manuscript. It reads only
  `results/scored_responses.csv` and does not change any earlier output.
* `make_figures.py` gained two optional arguments (`--dpi`, `--out`). With no arguments
  it behaves exactly as before. The manuscript figures use the same data at 600 dpi.
* PNG files can differ byte-for-byte between machines with different font or
  matplotlib builds; the plotted values do not change.
