#!/usr/bin/env bash
set -euo pipefail

# Run from project root: /ihome/hpark/ssk143/ccdg/new_genotype_qc

bash 01_plink_qc.sh
bash 02_plink_pca_relatedness.sh
python3 03_python_reports_and_plots.py

echo "All steps complete."
