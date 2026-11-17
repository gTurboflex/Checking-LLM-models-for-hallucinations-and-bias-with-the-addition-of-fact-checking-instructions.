#!/usr/bin/env bash
# Level 1: recompute every table from the saved answers. No models and no GPU needed.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
echo "[1/5] Checking frozen inputs and coverage...";   .venv/bin/python -X utf8 validate_package.py
echo "[2/5] Recomputing statistics...";                 .venv/bin/python -X utf8 analyse_main.py
echo "[3/5] Redrawing figures...";                      .venv/bin/python -X utf8 make_figures.py
echo "[4/5] Recomputing manuscript extra table...";     .venv/bin/python -X utf8 manuscript_extra_analysis.py
echo "[5/5] Comparing with recorded hashes...";         .venv/bin/python -X utf8 verify_reproduction.py
echo "DONE. Fill in REPRODUCTION_REPORT_TEMPLATE.md with what you saw."
