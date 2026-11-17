#!/usr/bin/env bash
# Level 2: one live question x 4 conditions on the local models (a few minutes).
set -euo pipefail
cd "$(dirname "$0")"
python3 -X utf8 run_experiment.py --mode demo --questions 1 --models qwen3:1.7b qwen3:4b-q4_K_M qwen3:8b gemma4:e2b
python3 -X utf8 analyse_demo.py --latest
