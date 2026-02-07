# OPSMILE-genotype-QC
Genotype QC Pipeline: Sex Check + Relatedness (PLINK)

This repository contains a reproducible QC workflow for a multi-country genotyping dataset (array-based genotype data).  
The pipeline focuses on:

- **Sex check** using PLINK `--check-sex`
- **Relatedness / IBD** using PLINK `--genome`
- **Country-level summaries** by mapping genotype IDs to study site/country metadata
- **Exporting review tables** for flagged parent/offspring-like pairs and mismatch patterns
- **PCA** using LD-pruned SNPs (included as a standard population QC step)

> **Note:** Raw genotype files are not included in this repo (privacy + size). The repo is designed to run on an HPC/Linux environment.

---

## Project Goals

1. Identify potential **sample identity issues**:
   - Sex mismatches (reported vs inferred)
   - Unexpected close relatives (duplicates/twins, parent/offspring-like, full siblings)
2. Support downstream analyses by providing:
   - Country/site-level QC summaries
   - Review-ready spreadsheets of flagged pairs
   - Clear plots for visual QC inspection

---

## Inputs (expected)

### Genotype data (PLINK binary)
- `opsmile_geno_allchroms.bed`
- `opsmile_geno_allchroms.bim`
- `opsmile_geno_allchroms.fam`

### Metadata
- `sample_number_barcode_well.csv`  
  Used to build `IID = SentrixBarcode_A + "_" + SentrixPosition_A` and map IID → Sample_ID.
- `LACGWAS_envirodata_pitt_updated_04.2025.xlsx`  
  Sheet: `Enviro Data of Samples`  
  Used to map Sample_ID → CountryandYear via `sa_nr` linkage.

---

## Outputs (key)

### Sex check
- `qc/opsmile_sexcheck.sexcheck`
- `qc/sexcheck_problem_rate_by_country.xlsx`
- Plot: `qc_plots/sexcheck_error_rate_by_country.png`
- Plot: `qc_plots/sexcheck_scatter_by_country_grid.png`

### Relatedness / IBD
- `qc/opsmile_ibd.genome`
- Candidate tables (e.g., parent/full-sib like pairs) and review exports

### PCA
- `qc/pca/opsmile_pca.eigenvec`
- `qc/pca/opsmile_pca.eigenval`

---
Raw genotype files (.bed/.bim/.fam) and protected metadata are **not** included in this repository.

Expected inputs:
- PLINK binary files: opsmile_geno_allchroms.*
- manifest: sample_number_barcode_well.csv
- enviro metadata: LACGWAS_envirodata_pitt_updated_04.2025.xlsx
