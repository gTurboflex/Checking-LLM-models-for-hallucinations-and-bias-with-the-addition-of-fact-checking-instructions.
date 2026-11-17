# Independent reproduction guide

This guide is for anyone outside the author team who wants to check the results of
"Does a Fact-Checking System Instruction Reduce False-Premise Sycophancy? A Paired
Evaluation of Six LLMs". You need no contact with the authors. Everything below is in this repository.

There are three levels. Level 1 is enough to check every number in the manuscript.
Levels 2 and 3 repeat the model calls themselves.

| Level | What it checks | Needs | Time |
|---|---|---|---|
| 1. Offline recomputation | Every table, statistic and figure is recomputed from the saved answers and labels | Python 3.12, internet for `pip` | ~2 min |
| 2. Live demo | The pipeline really calls the models: 1 question x 4 conditions | Ollama + local models (GPU with 8 GB VRAM recommended) | ~5 min |
| 3. Full rerun | All 2400 requests again, compared with the saved answers | Ollama, all 6 models, Ollama cloud account | ~2 h |

Windows: double-click the `.cmd` files. Linux/macOS: run the `.sh` files with `bash <file>.sh`.

---

## 1. Offline recomputation (recommended)

1. Install Python 3.12 (3.10+ works; 3.12 matches the original environment) from https://www.python.org/downloads/.
2. Clone the repository at the tag used in the manuscript:
   ```
   git clone --branch final https://github.com/gTurboflex/Checking-LLM-models-for-hallucinations-and-bias-with-the-addition-of-fact-checking-instructions.
   ```
   (The repository name ends with a full stop.) Or open the repository on GitHub, choose Tags → `final` and download the ZIP.
3. Run `reproduce_offline.cmd` (Windows) or `bash reproduce_offline.sh` (Linux/macOS).

The script creates a private `.venv`, installs the pinned packages from `requirements.txt`, then runs:

| Step | Script | Output |
|---|---|---|
| 1 | `validate_package.py` | Checks frozen inputs (SHA-256 in `protocol_freeze.json`), that every saved request matches the frozen prompt, and that all 2400 planned slots exist |
| 2 | `analyse_main.py` | `results/*.csv`, `results/analysis.json` (McNemar, Holm, bootstrap, Wilson, Brier) |
| 3 | `make_figures.py` | `figures/figure1_agreement.png`, `figures/figure2_factual_errors.png` |
| 4 | `manuscript_extra_analysis.py` | `results/manuscript_extra.csv` (extra numbers quoted in the manuscript) |
| 5 | `verify_reproduction.py` | Compares every regenerated table with the SHA-256 recorded in `reproduction_record.json` |

**Expected result:** `SUCCESS: every input and result table matches the recorded SHA-256 hashes.`
On Linux/macOS `analysis.json` is reported as "same content; only line endings differ"; that is a pass.
Figure PNG files may differ byte-wise because of system fonts; compare them visually with the committed figures.
`MANUSCRIPT_REPRODUCTION.md` maps each table and number in the manuscript to its output file and column.

This level does not call any model. It checks the analysis, not the generation.

---

## 2. Models used and how to download them

All models were run through **Ollama 0.40.15** (https://ollama.com/download) on 8 November 2026,
on Windows 11 with an Intel i7-13650HX, 32 GB RAM and an NVIDIA RTX 4070 Laptop GPU (8 GB VRAM)
(`hardware_snapshot.json`). Larger open-weight models did not fit in 8 GB VRAM, which is why two
Ollama cloud models were added.

| Model tag (exact) | Where it runs | Size | Params / quant. | Digest recorded in the study (first 12) |
|---|---|---|---|---|
| `qwen3:1.7b` | local | 1.36 GB | 2.0B, Q4_K_M | `8f68893c685c` |
| `qwen3:4b-q4_K_M` | local | 2.62 GB | 4.0B, Q4_K_M | `2bfd38a7daaf` |
| `qwen3:8b` | local | 5.23 GB | 8.2B, Q4_K_M | `500a1f067a9f` |
| `gemma4:e2b` | local | 4.59 GB | 4.6B, Q4_K_M | `b37049369ade` |
| `beam:cloud` | Ollama cloud | - | not disclosed | - |
| `gemma4:31b-cloud` | Ollama cloud | - | 31B | - |

Full digests and the complete `/api/show` output of every model are stored in
`main_runs/main_100_v1/metadata.json`.

To download them, install and start Ollama, then run `setup_models.cmd` / `bash setup_models.sh`,
or type the commands yourself:

```
ollama pull qwen3:1.7b
ollama pull qwen3:4b-q4_K_M
ollama pull qwen3:8b
ollama pull gemma4:e2b
ollama signin                 # cloud models only: needs a free ollama.com account
ollama pull beam:cloud
ollama pull gemma4:31b-cloud
```

`python check_ollama_models.py` then reports which models are present and whether each local model
has the same digest as in the study (`OK`) or a newer build (`OK*`).

**Generation settings** (fixed in `run_experiment.py`, hash-frozen in `protocol_freeze.json`):
temperature 0, `num_predict` 512, thinking disabled. Local models also use seed 2418, `num_ctx` 4096,
`top_k` 20, `top_p` 0.95, `repeat_penalty` 1. Cloud models accept no seed. Requests are sent one
model at a time; the 400 jobs per model are shuffled with seed 2418.
The exact system prompts (`COMMON` and the fact-checking `GUARD`) are at the top of `run_experiment.py`.

---

## 3. Live demo (Level 2)

Start Ollama, then run `run_live_demo.cmd` / `bash run_live_demo.sh`.
It sends one question in the four conditions A-D to the four local models and prints the answers
(`demo_runs/<timestamp>/`). This shows the pipeline works on your machine; one question is not
evidence for or against the hypotheses.

---

## 4. Full rerun (Level 3)

Run `run_full_rerun.cmd` / `bash run_full_rerun.sh`. It calls

```
python run_experiment.py --mode main          # writes main_runs/<timestamp>/, never overwrites main_100_v1
python compare_rerun.py --latest              # share of answers identical to the saved run, per model
```

If the run stops (cloud quota, network), continue it with
`python run_experiment.py --mode main --out main_runs/<timestamp> --resume --retry-errors`.

What to expect:
* Local models with the same digest and Ollama version should give mostly identical text.
* A different Ollama version, GPU or model build can change answers slightly.
* Cloud models get no seed and can be updated by the provider, so lower agreement is expected.

New answers have no labels yet. To compare accuracy, label them with the rules in `SCORING.txt`
(the original labels were AI-assisted with `annotate_assisted.py` and partly human-checked;
see `human_review_record.json`) and run
`python analyse_main.py --run main_runs/<timestamp> --annotations <your_labels.csv> --out results_rerun`.

---

## 5. Report what you found

Copy `REPRODUCTION_REPORT_TEMPLATE.md`, fill it in and send it to the corresponding author
(240168@astanait.edu.kz) or open a GitHub issue. Report failures as well as successes.
