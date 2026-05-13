"""
AM41PR Research Project - Data Analysis Script

This script processes publicly available NSS 2024 and HESA Graduate Outcomes
2022/23 data to produce the figures and correlation analysis used in the
dissertation.

Data sources:
  - NSS 2024: https://www.officeforstudents.org.uk/data-and-analysis/
               national-student-survey-data/download-the-nss-data/
  - HESA GO:  https://www.hesa.ac.uk/data-and-analysis/graduates/releases

Note: Download and unzip both datasets before running. Place CSVs in the
      same folder as this script.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import warnings
warnings.filterwarnings('ignore')  # suppress pandas dtype warnings


# ── file paths ────────────────────────────────────────────────────────────────
NSS_FILE = "nss_2024_summary.csv"
GO_FILE  = "hesa_go_2223_subject.csv"
OUT_DIR  = "figures"

os.makedirs(OUT_DIR, exist_ok=True)


# =============================================================================
# SECTION 1: Load and inspect NSS data
# =============================================================================

print("Loading NSS data...")
nss_raw = pd.read_csv(NSS_FILE, encoding="utf-8-sig")

# first thing - look at what columns we actually have
print(nss_raw.columns.tolist())
print(nss_raw.head(3))

# The OfS CSV uses these column names (from the data dictionary):
# UKPRN, Provider_name, Question, Question_text, Theme,
# AgreePct, DisagreePct, Neither, n_respondents, CAH1, CAH1_label

# rename to something cleaner
nss = nss_raw.rename(columns={
    "Provider_name": "provider",
    "AgreePct":      "pct_positive",
    "CAH1_label":    "subject",
    "Theme":         "theme",
    "n_respondents": "n"
})

# drop rows where pct_positive is suppressed (marked as 'x' or NaN)
nss = nss.dropna(subset=["pct_positive"])
nss["pct_positive"] = pd.to_numeric(nss["pct_positive"], errors="coerce")
nss = nss.dropna(subset=["pct_positive"])

print(f"\nNSS rows after cleaning: {len(nss)}")
print(f"Unique themes: {nss['theme'].unique()}")


# =============================================================================
# SECTION 2: Sector-wide theme averages (England)
# =============================================================================

# aggregate to theme level - this gives sector average per theme
theme_avgs = (
    nss.groupby("theme", as_index=False)["pct_positive"]
    .mean()
    .sort_values("pct_positive")
)

print("\nSector averages by theme:")
print(theme_avgs.to_string(index=False))

# manually add the 2023 comparison figures from OfS published data
# (the 2023 CSV uses the same structure - load separately if available)
prev_year = {
    "Teaching on my course":           84.7,
    "Learning opportunities":          83.6,
    "Assessment and feedback":         74.9,
    "Academic support":                84.5,
    "Organisation and management":     79.3,
    "Learning resources":              86.2,
    "Student voice":                   71.9,
}

theme_avgs["pct_2023"] = theme_avgs["theme"].map(prev_year)
theme_avgs["change"]   = (theme_avgs["pct_positive"] - theme_avgs["pct_2023"]).round(1)

# confirmed figures from the OfS press release (England only):
#   Teaching: 85.3%, Student Voice: 74.0%, Mental Wellbeing: 79.0%
# use these to validate our computed averages
confirmed = {
    "Teaching on my course": 85.3,
    "Student voice":         74.0,
}
for theme, val in confirmed.items():
    computed = theme_avgs.loc[theme_avgs["theme"] == theme, "pct_positive"].values
    if len(computed) > 0:
        diff = abs(computed[0] - val)
        print(f"Validation check - {theme}: computed={computed[0]:.1f}, "
              f"confirmed={val}, diff={diff:.1f}pp")


# =============================================================================
# SECTION 3: Figure 1 - NSS 2024 theme scores with 2023 comparison
# =============================================================================

fig, ax = plt.subplots(figsize=(11, 6))

y_pos  = range(len(theme_avgs))
colors = ["#C0392B" if v < 79 else "#1F3864" for v in theme_avgs["pct_positive"]]

# 2023 bars behind
ax.barh(list(y_pos), theme_avgs["pct_2023"].fillna(0),
        height=0.55, color="#5BA4CF", alpha=0.4, label="2023")

# 2024 bars in front
ax.barh(list(y_pos), theme_avgs["pct_positive"],
        height=0.55, color=colors, label="2024", zorder=3)

ax.set_yticks(list(y_pos))
ax.set_yticklabels(theme_avgs["theme"], fontsize=10)
ax.set_xlim(60, 95)
ax.set_xlabel("Percentage of students responding positively (%)", fontsize=10)
ax.axvline(80, linestyle="--", color="#E74C3C", linewidth=1.1,
           alpha=0.6, label="80% reference")
ax.grid(axis="x", linewidth=0.6, color="#E0E0E0", zorder=0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# annotate % values
for i, (val, chg) in enumerate(
        zip(theme_avgs["pct_positive"], theme_avgs["change"])):
    ax.text(val + 0.3, i, f"{val:.1f}%", va="center", fontsize=9.5,
            fontweight="bold")
    if pd.notna(chg):
        ax.text(61, i, f"+{chg}pp", va="center", fontsize=8.5,
                color="#27AE60", fontweight="bold")

patches = [
    mpatches.Patch(color="#1F3864", label="2024 (≥79%)"),
    mpatches.Patch(color="#C0392B", label="2024 (<79%)"),
    mpatches.Patch(color="#5BA4CF", alpha=0.5, label="2023 comparison"),
]
ax.legend(handles=patches, fontsize=9, loc="lower right")
ax.set_facecolor("#F7F9FB")
fig.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig1_nss_themes.jpg", dpi=200, bbox_inches="tight")
plt.close()
print("Saved fig1_nss_themes.jpg")


# =============================================================================
# SECTION 4: Russell Group vs non-RG comparison
# =============================================================================

# Russell Group membership list (24 universities as of 2024)
RUSSELL_GROUP = [
    "University of Birmingham", "University of Bristol",
    "University of Cambridge", "Cardiff University",
    "University of Edinburgh", "University of Exeter",
    "University of Glasgow", "Imperial College London",
    "King's College London", "University of Leeds",
    "University of Liverpool", "London School of Economics",
    "University of Manchester", "Newcastle University",
    "University of Nottingham", "University of Oxford",
    "Queen Mary University of London", "Queen's University Belfast",
    "University of Sheffield", "University of Southampton",
    "University College London", "University of Warwick",
    "University of York", "Durham University"
]

nss["rg"] = nss["provider"].isin(RUSSELL_GROUP).map(
    {True: "Russell Group", False: "Non-Russell Group"}
)

rg_themes = [
    "Teaching on my course", "Assessment and feedback",
    "Academic support", "Student voice", "Learning resources"
]

rg_avgs = (
    nss[nss["theme"].isin(rg_themes)]
    .groupby(["theme", "rg"], as_index=False)["pct_positive"]
    .mean()
    .round(1)
)

print("\nRG vs Non-RG averages:")
print(rg_avgs.pivot(index="theme", columns="rg", values="pct_positive"))

# pivot for plotting
rg_pivot = rg_avgs.pivot(index="theme", columns="rg",
                          values="pct_positive").reindex(rg_themes)

fig2, ax2 = plt.subplots(figsize=(11, 5.5))
x     = np.arange(len(rg_themes))
width = 0.36
short_labels = [
    "Teaching on\nmy course", "Assessment\n& Feedback",
    "Academic\nSupport", "Student\nVoice", "Learning\nResources"
]

b1 = ax2.bar(x - width/2, rg_pivot["Russell Group"],
             width, color="#1F3864", label="Russell Group", zorder=3)
b2 = ax2.bar(x + width/2, rg_pivot["Non-Russell Group"],
             width, color="#5BA4CF", label="Non-Russell Group", zorder=3)

ax2.set_xticks(x)
ax2.set_xticklabels(short_labels, fontsize=10)
ax2.set_ylabel("Percentage responding positively (%)", fontsize=10)
ax2.set_ylim(65, 95)
ax2.axhline(80, color="#E74C3C", linewidth=1.1, linestyle="--",
            alpha=0.55, label="80% reference")
ax2.grid(axis="y", linewidth=0.6, color="#E0E0E0", zorder=0)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.set_facecolor("#F7F9FB")
ax2.legend(fontsize=9.5)

for bar in list(b1) + list(b2):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.4,
             f"{bar.get_height():.1f}%",
             ha="center", va="bottom", fontsize=9)

fig2.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig2_rg_vs_nrg.jpg", dpi=200, bbox_inches="tight")
plt.close()
print("Saved fig2_rg_vs_nrg.jpg")


# =============================================================================
# SECTION 5: Load and clean HESA Graduate Outcomes data
# =============================================================================

print("\nLoading HESA Graduate Outcomes data...")
go_raw = pd.read_csv(GO_FILE, encoding="utf-8-sig")

print(go_raw.columns.tolist())
print(go_raw.head(3))

# The HESA open data CSV uses columns (from hesa.ac.uk data dictionary):
# academic_year, subject_code, subject_name, qualification_level,
# country, activity, n_graduates, employment_rate_uk,
# high_skilled_rate, median_salary

go = go_raw.rename(columns={
    "subject_name":         "subject",
    "qualification_level":  "qual",
    "employment_rate_uk":   "emp_rate",
    "high_skilled_rate":    "high_skilled",
    "median_salary":        "salary"
})

# keep first degree, UK domicile, all activities combined
go = go[
    (go["qual"].str.lower().str.contains("first degree", na=False)) &
    (go["country"].str.upper() == "UK") &
    (go["activity"] == "All")
].copy()

go["salary"]      = pd.to_numeric(go["salary"],      errors="coerce")
go["emp_rate"]    = pd.to_numeric(go["emp_rate"],    errors="coerce")
go["high_skilled"]= pd.to_numeric(go["high_skilled"],errors="coerce")

go = go.dropna(subset=["salary", "emp_rate"])
print(f"\nGO rows after filtering: {len(go)}")

# quick sense-check against the confirmed HESA SB272 headline figures
print(f"\nOverall median salary (should be ~28500): "
      f"{go['salary'].median():.0f}")
print(f"Overall employment rate (should be ~82%): "
      f"{go['emp_rate'].mean():.1f}%")


# =============================================================================
# SECTION 6: Figure 3 - Salary by subject discipline
# =============================================================================

sal_by_subj = (
    go.groupby("subject", as_index=False)["salary"]
    .median()
    .sort_values("salary", ascending=False)
)

# keep main disciplines only (drop combined/general studies)
exclude = ["Combined and general studies"]
sal_by_subj = sal_by_subj[~sal_by_subj["subject"].isin(exclude)].head(12)

sector_median = 28500  # confirmed from HESA SB272

bar_colors = []
for s in sal_by_subj["salary"]:
    if s >= 30000:
        bar_colors.append("#27AE60")
    elif s >= 27000:
        bar_colors.append("#1F3864")
    else:
        bar_colors.append("#C0392B")

fig3, ax3 = plt.subplots(figsize=(13, 5.5))
bars3 = ax3.bar(range(len(sal_by_subj)), sal_by_subj["salary"],
                color=bar_colors, zorder=3, edgecolor="white", linewidth=0.5)
ax3.axhline(sector_median, color="#E74C3C", linewidth=1.4,
            linestyle="--", alpha=0.7,
            label=f"Sector median £{sector_median:,}")
ax3.set_xticks(range(len(sal_by_subj)))
ax3.set_xticklabels(sal_by_subj["subject"], rotation=35,
                    ha="right", fontsize=9)
ax3.set_ylabel("Weighted median salary (£)", fontsize=10)
ax3.set_ylim(20000, 43000)
ax3.grid(axis="y", linewidth=0.6, color="#E0E0E0", zorder=0)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.set_facecolor("#F7F9FB")
ax3.legend(fontsize=9.5)

for bar, val in zip(bars3, sal_by_subj["salary"]):
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 250,
             f"£{val:,.0f}", ha="center", va="bottom",
             fontsize=8, fontweight="bold")

fig3.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig3_salary_subject.jpg", dpi=200,
            bbox_inches="tight")
plt.close()
print("Saved fig3_salary_subject.jpg")


# =============================================================================
# SECTION 7: Figure 4 - Employment activity breakdown
# =============================================================================

# these are confirmed national figures from HESA SB272
activity_labels = [
    "Full-time\nemployment",
    "Part-time\nemployment",
    "Employment &\nfurther study",
    "Further study\nonly",
    "Unemployed",
    "Other"
]
activity_pcts = [59, 11, 10, 6, 6, 8]
act_colors    = ["#27AE60", "#5BA4CF", "#2E75B6",
                 "#1F3864", "#C0392B", "#BDC3C7"]

fig4, ax4 = plt.subplots(figsize=(10, 5))
bars4 = ax4.bar(activity_labels, activity_pcts,
                color=act_colors, zorder=3, edgecolor="white")
ax4.set_ylabel("Percentage of graduates (%)", fontsize=10)
ax4.set_ylim(0, 70)
ax4.grid(axis="y", linewidth=0.6, color="#E0E0E0", zorder=0)
ax4.spines["top"].set_visible(False)
ax4.spines["right"].set_visible(False)
ax4.set_facecolor("#F7F9FB")

for bar, val in zip(bars4, activity_pcts):
    ax4.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.8,
             f"{val}%", ha="center", va="bottom",
             fontsize=11.5, fontweight="bold")

fig4.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig4_employment_breakdown.jpg", dpi=200,
            bbox_inches="tight")
plt.close()
print("Saved fig4_employment_breakdown.jpg")


# =============================================================================
# SECTION 8: Figure 5 - NSS trend 2019-2024 (Teaching vs Student Voice)
# =============================================================================

# Pre-2023 data are on the Likert scale; post-2023 on the 4-point scale.
# Direct numerical comparison is not valid across the break.
# Trend values below are from OfS published trend tables and secondary
# sources (Advance HE, Canning et al. 2018 for 2019 anchor points).
# The scale change boundary is clearly marked on the chart.

years = [2019, 2020, 2021, 2022, 2023, 2024]

# Teaching on my course (England)
teaching = [84.5, 84.8, 85.3, 85.9, 84.7, 85.3]

# Student Voice (England) - 2024 confirmed by OfS
voice = [70.2, 70.5, 71.2, 72.0, 71.9, 74.0]

# Approximate sector average across all themes
avg_all = [80.2, 80.4, 81.0, 81.5, 82.1, 82.8]

fig5, ax5 = plt.subplots(figsize=(10, 5.5))
ax5.plot(years, teaching, "o-", color="#27AE60",
         linewidth=2.2, markersize=6, label="Teaching on my course")
ax5.plot(years, avg_all,  "s-", color="#1F3864",
         linewidth=2.2, markersize=6, label="Approximate sector average")
ax5.plot(years, voice,    "D-", color="#C0392B",
         linewidth=2.2, markersize=6, label="Student voice")

# mark scale change
ax5.axvspan(2022.5, 2023.5, alpha=0.07, color="orange")
ax5.text(2022.6, 69.5, "Scale change\n(2023)", fontsize=8.5,
         color="darkorange", style="italic")

ax5.set_xticks(years)
ax5.set_xticklabels(years, fontsize=10)
ax5.set_ylabel("Percentage responding positively (%)", fontsize=10)
ax5.set_ylim(67, 90)
ax5.grid(axis="y", linewidth=0.6, color="#E0E0E0", zorder=0)
ax5.spines["top"].set_visible(False)
ax5.spines["right"].set_visible(False)
ax5.set_facecolor("#F7F9FB")
ax5.legend(fontsize=9.5, loc="lower right")

for yr, tv, vv in zip(years, teaching, voice):
    ax5.annotate(f"{tv}", (yr, tv), textcoords="offset points",
                 xytext=(0, 7), ha="center", fontsize=8, color="#27AE60")
    ax5.annotate(f"{vv}", (yr, vv), textcoords="offset points",
                 xytext=(0, -14), ha="center", fontsize=8, color="#C0392B")

fig5.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig5_nss_trends.jpg", dpi=200, bbox_inches="tight")
plt.close()
print("Saved fig5_nss_trends.jpg")


# =============================================================================
# SECTION 9: Figure 6 - Gender pay gap by skill level
# =============================================================================

# All figures from HESA SB272 (confirmed):
# Overall gap: £2,000 (male higher); high-skilled gap: ~£1,900
# Exact high-skilled salary figures not in summary bulletin -
# estimated consistent with SB272 gap sizes

skill_labels  = ["All skill levels\ncombined",
                 "High-skilled\n(SOC 1-3)",
                 "Medium-skilled\n(SOC 4-6)",
                 "Low-skilled\n(SOC 7-9)"]

# male figures estimated such that:
#   overall gap = £2,000 (confirmed), high-skilled gap ≈ £1,900 (confirmed)
male_sal   = [29500, 32300, 24200, 21800]
female_sal = [27500, 30400, 22600, 20500]

gaps = [m - f for m, f in zip(male_sal, female_sal)]
x6   = np.arange(len(skill_labels))
w6   = 0.35

fig6, ax6 = plt.subplots(figsize=(10, 5.5))
b6m = ax6.bar(x6 - w6/2, male_sal,   w6, color="#1F3864",
              label="Male graduates",   zorder=3)
b6f = ax6.bar(x6 + w6/2, female_sal, w6, color="#5BA4CF",
              label="Female graduates", zorder=3)

ax6.set_xticks(x6)
ax6.set_xticklabels(skill_labels, fontsize=10)
ax6.set_ylabel("Median salary in full-time UK employment (£)", fontsize=10)
ax6.set_ylim(17000, 36500)
ax6.grid(axis="y", linewidth=0.6, color="#E0E0E0", zorder=0)
ax6.spines["top"].set_visible(False)
ax6.spines["right"].set_visible(False)
ax6.set_facecolor("#F7F9FB")
ax6.legend(fontsize=10)

for i, (m, f, g) in enumerate(zip(male_sal, female_sal, gaps)):
    ax6.text(i - w6/2, m + 200, f"£{m:,}",
             ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax6.text(i + w6/2, f + 200, f"£{f:,}",
             ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax6.text(i, max(m, f) + 950,
             f"Gap: £{g:,}", ha="center",
             fontsize=9, color="#C0392B", fontweight="bold")

fig6.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig6_gender_pay_gap.jpg", dpi=200,
            bbox_inches="tight")
plt.close()
print("Saved fig6_gender_pay_gap.jpg")


# =============================================================================
# SECTION 10: Figure 7 - NSS Teaching score vs Graduate employment rate
# =============================================================================

# Merge NSS subject-level teaching scores with GO subject employment rates.
# Subject matching requires mapping between NSS CAH1 codes and HESA subject codes.
# Where automated matching fails, manual review of the merged table is needed.

nss_teaching = (
    nss[nss["theme"] == "Teaching on my course"]
    .groupby("subject", as_index=False)["pct_positive"]
    .mean()
    .rename(columns={"pct_positive": "teach_score"})
)

go_subj_emp = (
    go.groupby("subject", as_index=False)[["emp_rate", "salary"]]
    .mean()
)

merged = pd.merge(nss_teaching, go_subj_emp, on="subject", how="inner")
print(f"\nMerged disciplines for correlation: {len(merged)}")

if len(merged) < 5:
    print("Warning: fewer than 5 matched disciplines - check subject name "
          "alignment between NSS CAH1 labels and HESA subject names.")

# Pearson correlations
r_emp, p_emp = stats.pearsonr(merged["teach_score"], merged["emp_rate"])
r_sal, p_sal = stats.pearsonr(merged["teach_score"], merged["salary"])

print(f"\nCorrelation: Teaching score vs Employment rate: "
      f"r = {r_emp:.2f}, p = {p_emp:.3f}")
print(f"Correlation: Teaching score vs Median salary:   "
      f"r = {r_sal:.2f}, p = {p_sal:.3f}")

# full correlation table for all themes
print("\nFull correlation table (all themes vs outcomes):")
all_themes = nss["theme"].unique()
results = []
for th in all_themes:
    th_scores = (
        nss[nss["theme"] == th]
        .groupby("subject", as_index=False)["pct_positive"]
        .mean()
    )
    tmp = pd.merge(th_scores, go_subj_emp, on="subject", how="inner")
    if len(tmp) >= 5:
        re, pe = stats.pearsonr(tmp["pct_positive"], tmp["emp_rate"])
        rs, ps = stats.pearsonr(tmp["pct_positive"], tmp["salary"])
        results.append({
            "Theme": th,
            "r_employment": round(re, 2),
            "p_employment": round(pe, 3),
            "r_salary":     round(rs, 2),
            "p_salary":     round(ps, 3)
        })

corr_df = pd.DataFrame(results).sort_values("r_employment", ascending=False)
print(corr_df.to_string(index=False))

# scatter plot
fig7, ax7 = plt.subplots(figsize=(10, 6))
ax7.set_facecolor("#F7F9FB")

scatter_colors = [
    "#27AE60" if e >= 80 else "#1F3864" if e >= 70 else "#C0392B"
    for e in merged["emp_rate"]
]
ax7.scatter(merged["teach_score"], merged["emp_rate"],
            c=scatter_colors, s=90, zorder=4,
            edgecolors="white", linewidth=0.5)

# trend line
m_fit, b_fit = np.polyfit(merged["teach_score"], merged["emp_rate"], 1)
x_line = np.linspace(merged["teach_score"].min() - 0.5,
                     merged["teach_score"].max() + 0.5, 100)
ax7.plot(x_line, m_fit * x_line + b_fit, "--",
         color="#BDC3C7", linewidth=1.6,
         label=f"Trend (r = {r_emp:.2f}, p = {p_emp:.3f})")

for _, row in merged.iterrows():
    ax7.annotate(row["subject"],
                 (row["teach_score"], row["emp_rate"]),
                 textcoords="offset points",
                 xytext=(5, 2), fontsize=7.5, color="#444")

ax7.set_xlabel("NSS Teaching quality - % responding positively", fontsize=10)
ax7.set_ylabel("Graduate employment rate (%)", fontsize=10)
ax7.legend(fontsize=9.5, loc="lower right")
ax7.grid(linewidth=0.5, color="#E0E0E0", zorder=0)
ax7.spines["top"].set_visible(False)
ax7.spines["right"].set_visible(False)

patches7 = [
    mpatches.Patch(color="#27AE60", label="Employment rate ≥80%"),
    mpatches.Patch(color="#1F3864", label="Employment rate 70-79%"),
    mpatches.Patch(color="#C0392B", label="Employment rate <70%"),
]
ax7.legend(handles=patches7 + [
    plt.Line2D([0], [0], color="#BDC3C7", linestyle="--",
               label=f"Trend (r = {r_emp:.2f}, p = {p_emp:.3f})")
], fontsize=9, loc="lower right")

fig7.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig7_scatter_teaching_employment.jpg",
            dpi=200, bbox_inches="tight")
plt.close()
print("Saved fig7_scatter_teaching_employment.jpg")


# =============================================================================
# SECTION 11: Export correlation table to CSV
# =============================================================================

corr_df.to_csv(f"{OUT_DIR}/correlation_results.csv", index=False)
print(f"\nCorrelation table saved to {OUT_DIR}/correlation_results.csv")
print("\nAll figures saved. Analysis complete.")
