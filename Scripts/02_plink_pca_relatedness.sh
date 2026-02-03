#!/usr/bin/env bash
set -euo pipefail

ROOT="/ihome/hpark/ssk143/ccdg/new_genotype_qc"
QC_PREFIX="${ROOT}/qc/opsmile_qc"
PCA_DIR="${ROOT}/qc/pca"

mkdir -p "${PCA_DIR}"

# 1) LD prune
# Common: 200 50 0.2
plink --bfile "${QC_PREFIX}" \
  --indep-pairwise 200 50 0.2 \
  --out "${PCA_DIR}/opsmile_prune"

# 2) PCA on pruned SNPs
plink --bfile "${QC_PREFIX}" \
  --extract "${PCA_DIR}/opsmile_prune.prune.in" \
  --pca 20 \
  --out "${PCA_DIR}/opsmile_pca"

# 3) Relatedness / IBD on pruned SNPs
plink --bfile "${QC_PREFIX}" \
  --extract "${PCA_DIR}/opsmile_prune.prune.in" \
  --genome full \
  --out "${QC_DIR}/opsmile_ibd"

echo "PCA + relatedness complete."
echo "PCA eigenvec: ${PCA_DIR}/opsmile_pca.eigenvec"
echo "IBD genome:   ${ROOT}/qc/opsmile_ibd.genome"
