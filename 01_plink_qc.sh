#!/usr/bin/env bash
set -euo pipefail

# ============================
# PATHS (match your structure)
# ============================
ROOT="/ihome/hpark/ssk143/ccdg/new_genotype_qc"
IN_PREFIX="${ROOT}/opsmile_geno_allchroms"
QC_DIR="${ROOT}/qc"
PLOT_DIR="${ROOT}/qc_plots"

mkdir -p "${QC_DIR}" "${PLOT_DIR}"

echo "Input prefix: ${IN_PREFIX}"
echo "QC dir: ${QC_DIR}"

# ----------------------------
# 1) Initial missingness report (before filtering)
# ----------------------------
plink --bfile "${IN_PREFIX}" \
  --missing \
  --out "${ROOT}/qc_report_initial"

# ----------------------------
# 2) Sample missingness filter (mind)
#    YOU USED 0.20 in your filenames -> keep it consistent
# ----------------------------
plink --bfile "${IN_PREFIX}" \
  --mind 0.20 \
  --make-bed \
  --out "${ROOT}/step1_0.20_mind"

# ----------------------------
# 3) SNP missingness filter (geno)
# ----------------------------
plink --bfile "${ROOT}/step1_0.20_mind" \
  --geno 0.20 \
  --make-bed \
  --out "${ROOT}/step2_0.20_geno"

# ----------------------------
# 4) MAF filter (0.05)  (matches your maf05 files)
# ----------------------------
plink --bfile "${ROOT}/step2_0.20_geno" \
  --maf 0.05 \
  --make-bed \
  --out "${ROOT}/step3_maf05"

# ----------------------------
# 5) HWE filter (example threshold)
#    change threshold if your lab uses different
# ----------------------------
plink --bfile "${ROOT}/step3_maf05" \
  --hwe 1e-6 midp \
  --make-bed \
  --out "${ROOT}/step4_maf05_hwe"

# ----------------------------
# 6) Save final QC set into qc/opsmile_qc.*
# ----------------------------
plink --bfile "${ROOT}/step4_maf05_hwe" \
  --make-bed \
  --out "${QC_DIR}/opsmile_qc"

# ----------------------------
# 7) Sex check on final QC set
# ----------------------------
plink --bfile "${QC_DIR}/opsmile_qc" \
  --check-sex \
  --out "${QC_DIR}/opsmile_sexcheck"

echo "QC + sexcheck complete."
echo "Final QC dataset: ${QC_DIR}/opsmile_qc.*"
echo "Sexcheck: ${QC_DIR}/opsmile_sexcheck.sexcheck"
