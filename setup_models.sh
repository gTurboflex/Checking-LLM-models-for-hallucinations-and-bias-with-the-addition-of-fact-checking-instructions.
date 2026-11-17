#!/usr/bin/env bash
# Level 2 preparation: download the study models with Ollama.
set -euo pipefail
cd "$(dirname "$0")"
command -v ollama >/dev/null || { echo "Install Ollama from https://ollama.com/download first."; exit 1; }
ollama --version
echo "Downloading the four local models (about 14 GB in total)..."
for m in qwen3:1.7b qwen3:4b-q4_K_M qwen3:8b gemma4:e2b; do echo "--- $m"; ollama pull "$m"; done
read -r -p "Also set up the two cloud models (needs a free ollama.com account)? [y/N] " cloud
if [ "$cloud" = "y" ] || [ "$cloud" = "Y" ]; then
  ollama signin
  ollama pull beam:cloud
  ollama pull gemma4:31b-cloud
fi
python3 -X utf8 check_ollama_models.py
