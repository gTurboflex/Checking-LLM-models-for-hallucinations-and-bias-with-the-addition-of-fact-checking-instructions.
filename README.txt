RMT 100 QUESTIONS AND QUICK DEFENCE
Yergun, Danial, Diyar — SE-2418

This package separates the new main study from the classroom demonstration and the historical pilot.
MAIN: 100 TruthfulQA-derived questions x 4 conditions x 6 models = 2400 planned responses.
DEMO: 1 or 2 older questions x 4 conditions x all 6 models = 24 or 48 responses.
Do not describe demo outputs or old pilot outputs as new main-study evidence.

FAST START ON WINDOWS
1. Open Ollama. Sign in for the two cloud models and make sure access/quota is available.
2. Double-click Start_Defence_1_Question.cmd (24 responses) or Start_Defence_2_Questions.cmd (48 responses).
3. Answers appear in the console and are saved in a new demo_runs folder. Cloud failures are displayed, not replaced by cached answers. Use Ctrl+C to stop; saved rows remain.
4. For the 2400-response study, Start_Main_100.cmd starts a NEW timestamped run. It can take well over an hour. Do not start another full run merely to view existing results. Use the saved results and review commands below.
The prepared report and the reproduction button always refer to main_runs/main_100_v1. A newly generated main run is a separate raw dataset requiring its own annotation and analysis; do not reuse labels from old answer texts or pool runs silently.

Four conditions: A neutral; B leading with false premise; C neutral + fact-check instruction; D leading + that instruction. All models receive the same four variants. A live demonstration is illustrative and its order is not randomized. The main run uses a seeded shuffle within each model. Local models run one at a time and are unloaded between series. RAM and GPU memory are required; close unnecessary applications yourself if needed. This package does not close applications, buy credits, install model weights, or change subscriptions.

MODELS
qwen3:1.7b; qwen3:4b-q4_K_M; qwen3:8b; gemma4:e2b; beam:cloud; gemma4:31b-cloud.
The four local models must already be installed. Cloud access is through Ollama at http://localhost:11434. No API keys belong in this folder. Use the exact tags; a substituted model is a separately documented experiment.

COMMAND LINE (Python 3.12.14 was used for package development)
python run_experiment.py --mode main --dry-run
python run_experiment.py --mode demo --questions 1
python run_experiment.py --mode demo --questions 2
python run_experiment.py --mode main --out main_runs/my_run
python run_experiment.py --mode main --out main_runs/my_run --resume
python run_experiment.py --mode main --out main_runs/my_run --resume --retry-errors
The last command explicitly retries technical errors, retaining previous attempts. Completed responses are not rerun. Keep the same model list, dataset, runner, Ollama version and model metadata on resume. Changed versions require a separately reported run. A truncated response is retained, not silently regenerated.

VIEW AN EXISTING ANSWER WITHOUT INFERENCE
Double-click Show_Main_Results.cmd for the saved main table and an optional question lookup.
python review_run.py main_runs/main_100_v1 --id TQA640
python review_run.py demo_runs/NAME
The viewer clearly says SAVED LOG REPLAY. It displays the reference beside the response. It never claims to be a live generation.

REPRODUCE RESULTS OFFLINE
Double-click Reproduce_Results.cmd, or use the commands below. The first environment setup downloads pinned Python libraries; computation then uses saved data and makes no model calls.
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python analyse_main.py
.venv\Scripts\python make_figures.py
.venv\Scripts\python validate_package.py
Default input: main_runs/main_100_v1/responses.jsonl plus annotations.csv and any documented semantic corrections in annotation_overrides.json. Original judge labels remain unchanged; results/effective_annotations.csv contains the labels actually analysed. annotation_audit.csv records assistant review and unresolved wording. These are not independent human reviews.
All numbers come from logs and hash-linked annotations. Missing labels stay unknown. If annotations.csv is absent or partial, the program exports results/annotation_queue.csv and reports limited coverage; it does not invent final scores. Copy completed, verified labels to annotations.csv with the documented fields. A report is complete only when coverage and validation are disclosed.

SCORING
Read SCORING.txt. Correct, H and S are separate. S only applies to B/D. Missing confidence is not zero; invalid technical responses are not hallucinations. Reference matching requires semantic judgement, including negation and quoted misconceptions. AI-assisted annotations are provisional and their provenance must stay visible. The team confirmed review of the 30 selected errors in human_review_record.json. Danial and Diyar each reported SUCCESS for Reproduce_Results.cmd; teammate_reproduction_record.json preserves that user confirmation. This is saved-data reproduction, not a new inference experiment. Full independent human annotation was not completed.

FILES
questions_main.json — 100 selected items, original wording, category, source, references, false premise and variants.
questions_demo.json — two old pilot items, excluded from the main study.
source/TruthfulQA.csv — exact downloaded 790-row source snapshot; current file differs from the original published 817-item benchmark.
source/TruthfulQA_LICENSE.txt — upstream Apache 2.0 licence.
PROTOCOL.txt, SCORING.txt, protocol_freeze.json — pre-run local decisions, timestamp and hashes.
main_runs/ — full main raw requests/responses, metadata, plan and completion status.
demo_runs/ — separate live demonstration checks.
historical_pilot/ — original 12-question evidence, if included; never pooled.
results/ — reproducible CSV tables, annotation queue, error cases, JSON analysis.
figures/ — plots generated from analysis.json.
reports/ — A3 and A4 document copies.
manuscript/ — final manuscript for the journal Information (MDPI): Word file and PDF preview.
manuscript_extra_analysis.py, results/manuscript_extra.csv — supplementary manuscript numbers (A–B and B–D paired correctness changes, high-confidence accuracy).
MANUSCRIPT_REPRODUCTION.md — maps every table, figure and number in the manuscript to its command and output file.
REPRODUCE_INDEPENDENTLY.md — step-by-step guide for outside reproducers: models, downloads, three reproduction levels.
REPRODUCTION_REPORT_TEMPLATE.md — form for an independent reproducer to report the outcome.
reproduce_offline.cmd/.sh, verify_reproduction.py — offline recomputation and SHA-256 comparison with reproduction_record.json.
setup_models.cmd/.sh, check_ollama_models.py — download the six models with Ollama and check their digests.
run_live_demo.cmd/.sh, run_full_rerun.cmd/.sh, compare_rerun.py — live demo, full rerun into a new folder, comparison with the saved run.

LIMITS AND SUBMISSION STEPS
This is a purposive English factual-question experiment, not the official TruthfulQA benchmark score. The independent item count is 100, not 2400. Repeated conditions are paired. Qwen 8B and cloud models are supplementary to the original 1B–7B scope. One generation per cell does not quantify seed variance. Cloud hardware/order effects are not isolated. The protocol JSON is a local freeze, not evidence of uploading it to Moodle. No pre-run Moodle upload evidence was supplied. Public repository: https://github.com/gTurboflex/Checking-LLM-models-for-hallucinations-and-bias-with-the-addition-of-fact-checking-instructions. (tags assignment-4 and, after final approval, final). Full independent human annotation is not claimed; teammate reproduction is recorded only to the extent confirmed by the user. The study includes no-intervention prompt controls and larger model references; it does not execute a separate multi-stage mitigation such as CoVe. Confidence intervals describe item uncertainty, not a three-seed experiment.

DATA SOURCE
https://github.com/sylinrl/TruthfulQA
Downloaded from https://raw.githubusercontent.com/sylinrl/TruthfulQA/main/TruthfulQA.csv on 8 November 2026. See protocol_freeze.json for the exact hash. Question selection and drafting were AI-assisted. Original reference material remains attributed to its authors.

FINAL EXECUTION STATUS
The main run is finished: 2400 distinct planned slots attempted, 2391 technically valid answers, 9 length-truncated outputs retained, 2374 fully labelled valid answers and 17 unresolved cases. All 12 exported data files and both figures were reproduced byte-for-byte in a separately created environment (reproduction_record.json). The one-question live demo completed 24/24 valid responses in demo_runs/defence_validation_1_question. The two-question option plans 48 responses; it is not claimed as a completed 48-response validation.

FINAL MANUSCRIPT
The final project manuscript is in manuscript/. To regenerate everything it reports, run:
python analyse_main.py
python make_figures.py --dpi 600 --out figures/manuscript
python manuscript_extra_analysis.py
MANUSCRIPT_REPRODUCTION.md lists where each table, figure and number comes from. No model is contacted.

INDEPENDENT REPRODUCTION (FOR PEOPLE OUTSIDE THE TEAM)
Read REPRODUCE_INDEPENDENTLY.md. Short version: Windows users double-click reproduce_offline.cmd; Linux/macOS users run bash reproduce_offline.sh. The script installs pinned packages, recomputes every table and ends with SUCCESS when all tables match the recorded hashes. To call the models yourself, install Ollama, run setup_models.cmd (or .sh), then run_live_demo.cmd (or .sh). Report the outcome with REPRODUCTION_REPORT_TEMPLATE.md.
