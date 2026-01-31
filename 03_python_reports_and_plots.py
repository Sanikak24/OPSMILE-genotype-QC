import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = "/ihome/hpark/ssk143/ccdg/new_genotype_qc"
QC_DIR = f"{ROOT}/qc"
PLOT_DIR = f"{ROOT}/qc_plots"
PCA_DIR = f"{QC_DIR}/pca"

os.makedirs(PLOT_DIR, exist_ok=True)

MANIFEST = f"{ROOT}/sample_number_barcode_well.csv"
ENVIRO_XLSX = f"{ROOT}/LACGWAS_envirodata_pitt_updated_04.2025.xlsx"
ENVIRO_SHEET = "Enviro Data of Samples"

SEX_FILE = f"{QC_DIR}/opsmile_sexcheck.sexcheck"

# 1) Build IID -> Sample_ID and Sample_ID -> Country mapping
manifest = pd.read_csv(MANIFEST)
manifest["Sample_ID"] = pd.to_numeric(manifest["Sample_ID"], errors="coerce").astype("Int64")

manifest["IID"] = manifest["SentrixBarcode_A"].astype(str) + "_" + manifest["SentrixPosition_A"].astype(str)
iid_to_sample = manifest.set_index("IID")["Sample_ID"]

manifest["sa_nr"] = pd.to_numeric(manifest["Sample_Name"], errors="coerce")

env = pd.read_excel(ENVIRO_XLSX, sheet_name=ENVIRO_SHEET)
env.columns = env.columns.astype(str).str.strip()
env_small = env[["sa_nr", "CountryandYear"]].copy()
env_small["sa_nr"] = pd.to_numeric(env_small["sa_nr"], errors="coerce")

sample_country = (
    manifest[["Sample_ID", "sa_nr"]]
    .merge(env_small, on="sa_nr", how="left")[["Sample_ID", "CountryandYear"]]
    .drop_duplicates(subset=["Sample_ID"])  # critical
)

# 2) Load sexcheck and merge Country
sex = pd.read_csv(SEX_FILE, delim_whitespace=True)
sex["Sample_ID"] = pd.to_numeric(sex["IID"].map(iid_to_sample), errors="coerce").astype("Int64")

assert sex["Sample_ID"].isna().sum() == 0
sex = sex.merge(sample_country, on="Sample_ID", how="left")

assert sex["CountryandYear"].isna().sum() == 0

total_problem = (sex["STATUS"] == "PROBLEM").sum()
print("Total PROBLEM:", total_problem)

# 3) Sexcheck error rate by country (bar plot with % + counts)
sex_country = (
    sex.assign(is_problem=sex["STATUS"].eq("PROBLEM"))
       .groupby("CountryandYear")
       .agg(n_total=("Sample_ID", "count"),
            n_problem=("is_problem", "sum"))
       .reset_index()
)

sex_country["problem_pct"] = 100.0 * sex_country["n_problem"] / sex_country["n_total"]

# sanity: must equal 67
assert sex_country["n_problem"].sum() == total_problem

sex_country = sex_country.sort_values("problem_pct", ascending=False)

sex_country.to_excel(f"{QC_DIR}/sexcheck_problem_rate_by_country.xlsx", index=False)

plt.figure(figsize=(10, 5))
plt.bar(sex_country["CountryandYear"].astype(str), sex_country["problem_pct"])
plt.ylabel("Sex check PROBLEM rate (%)")
plt.xlabel("CountryandYear")
plt.title(f"PLINK Sex Check Error Rate by Country (Total PROBLEM={total_problem})")

# annotate counts on each bar
for i, r in sex_country.reset_index(drop=True).iterrows():
    plt.text(i, r["problem_pct"] + 0.3, f"{int(r['n_problem'])}/{int(r['n_total'])}",
             ha="center", va="bottom", fontsize=8, rotation=90)

plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/sexcheck_error_rate_by_country.png", dpi=200)
plt.close()

# 4) Scatter plot grid by country (male/female mismatch visualization)
np.random.seed(1)
sex["PEDSEX_jitter"] = sex["PEDSEX"] + np.random.uniform(-0.08, 0.08, size=len(sex))
colors = {"OK": "forestgreen", "PROBLEM": "orange"}

country_order = (
    sex.groupby("CountryandYear")["STATUS"]
       .apply(lambda x: (x == "PROBLEM").sum())
       .sort_values(ascending=False)
       .index.tolist()
)

n = len(country_order)
ncols = 3
nrows = int(np.ceil(n / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 3*nrows), sharey=True)
axes = np.array(axes).reshape(-1)

for ax, ctry in zip(axes, country_order):
    d = sex[sex["CountryandYear"] == ctry]
    for status, dd in d.groupby("STATUS"):
        ax.scatter(dd["PEDSEX_jitter"], dd["F"],
                   c=colors.get(status, "gray"),
                   alpha=0.7, edgecolor="k", linewidth=0.2,
                   label=status if ctry == country_order[0] else None)

    ax.axhline(0.2, linestyle="--", color="red", linewidth=0.8)
    ax.axhline(0.8, linestyle="--", color="red", linewidth=0.8)
    ax.set_xticks([1,2])
    ax.set_xticklabels(["Male", "Female"])
    ax.set_title(f"{ctry} (PROBLEM={(d['STATUS']=='PROBLEM').sum()})")

# turn off extras
for ax in axes[len(country_order):]:
    ax.axis("off")

fig.suptitle("Sexcheck by Country: Reported Sex vs F-statistic", y=1.02, fontsize=14)
fig.tight_layout()

handles, labels = axes[0].get_legend_handles_labels()
if handles:
    fig.legend(handles, labels, title="Status", bbox_to_anchor=(1.02, 0.98), loc="upper left")

plt.savefig(f"{PLOT_DIR}/sexcheck_scatter_by_country_grid.png", dpi=200, bbox_inches="tight")
plt.close()

# 5) Parent-offspring "child-child only" pairs Excel
pairs = pd.DataFrame({
    "Sample_ID_1": [320398, 320377, 32112136, 53927, 320401, 320108, 320399, 320139, 320374, 50711, 320388, 50565, 53567, 55809],
    "Sample_ID_2": [320385, 320336, 320391, 320139, 32112503, 32112162, 32112216, 32112171, 50540, 52650, 53430, 320386, 320191, 54631],
})

pairs.to_excel(f"{QC_DIR}/PO_child_child_only.xlsx", index=False)
print("Saved:", f"{QC_DIR}/PO_child_child_only.xlsx")

print("DONE. Plots written to:", PLOT_DIR)
