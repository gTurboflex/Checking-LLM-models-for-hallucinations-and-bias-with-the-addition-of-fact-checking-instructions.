#!/usr/bin/env bash
# Level 3: repeat all 2400 requests into a NEW folder, then compare with the saved run.
# Takes about 2 hours on an RTX 4070 Laptop GPU. The saved run is never overwritten.
set -euo pipefail
cd "$(dirname "$0")"
read -r -p "This sends 2400 requests (4 local + 2 cloud models). Continue? [y/N] " ok
[ "$ok" = "y" ] || [ "$ok" = "Y" ] || exit 0
python3 -X utf8 run_experiment.py --mode main || true
python3 -X utf8 compare_rerun.py --latest
