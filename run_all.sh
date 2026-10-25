#!/usr/bin/env bash
# Run from the repository root:
#   ./run_all.sh
#
# The scripts use paths relative to the repository root and must be run in
# numeric order, because each one reads the tables the previous one wrote.
set -euo pipefail

python3 code/02_build_tables.py
python3 code/03_match_parents.py
python3 code/04_aggregate_children.py
python3 code/05_estimate_ige.py
python3 code/06_lifecycle_bias.py
python3 code/07_make_figures.py
