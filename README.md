# MSc Data Science — AM41PR Research Project
## Student Satisfaction and Graduate Outcomes in UK Universities: A Multi-Dimensional Analysis of Public Data (2019–2024)

---

## Repository Structure

```
repo/
│
├── README.md                      ← this file
│
├── code/
│   └── analysis.py                ← main Python analysis script
│
├── data/
│   ├── nss_2024_summary.csv       ← NSS 2024 provider-level data (England)
│   ├── hesa_go_2223_subject.csv   ← HESA Graduate Outcomes 2022/23 by subject
│   ├── hesa_go_2223_gender.csv    ← HESA Graduate Outcomes 2022/23 by gender
│   └── nss_trends_2019_2024.csv   ← NSS theme trend data 2019 to 2024
│
└── figures/
    ├── fig1_nss_themes.jpg                  ← NSS 2024 sector theme scores
    ├── fig2_rg_vs_nrg.jpg                   ← Russell Group vs Non-RG comparison
    ├── fig3_salary_subject.jpg              ← Graduate salary by discipline
    ├── fig4_employment_breakdown.jpg        ← Employment activity breakdown
    ├── fig5_nss_trends.jpg                  ← NSS trend lines 2019–2024
    ├── fig6_gender_pay_gap.jpg              ← Gender pay gap by skill level
    └── fig7_scatter_teaching_employment.jpg ← Teaching score vs employment rate
```

---

## How to Run the Analysis

### 1. Requirements

Python 3.11 or later. Install dependencies:

```bash
pip install pandas numpy scipy matplotlib
```

### 2. Data

The `data/` folder contains processed CSV files derived from:

- **NSS 2024**: Office for Students  
  Full dataset: https://www.officeforstudents.org.uk/data-and-analysis/national-student-survey-data/download-the-nss-data/

- **HESA Graduate Outcomes 2022/23**: Higher Education Statistics Agency  
  Full dataset: https://www.hesa.ac.uk/data-and-analysis/graduates/releases

The CSVs in this repository are structured subsets of those datasets used for the analysis in this dissertation. Column names match the original OfS and HESA data dictionaries.

### 3. Running

```bash
cd code/
python analysis.py
```

Figures are saved to the `figures/` directory. A correlation results CSV is also exported there.

---

## Data Sources and Citations

| Dataset | Publisher | Year | URL |
|---|---|---|---|
| NSS 2024 Full Results | Office for Students | 2024 | https://www.officeforstudents.org.uk/data-and-analysis/national-student-survey-data/download-the-nss-data/ |
| Graduate Outcomes 2022/23 Open Data | HESA / Jisc | 2025 | https://www.hesa.ac.uk/data-and-analysis/graduates/releases |
| HE Student Statistics 2023/24 | HESA / data.gov.uk | 2026 | https://www.data.gov.uk/dataset/7813790e-0b5a-4d5a-b0ef-d76510bcb308 |
| LEO Graduate Outcomes 2022–23 | Dept for Education | 2024 | https://explore-education-statistics.service.gov.uk/find-statistics/leo-graduate-and-postgraduate-outcomes |

---

## Key Confirmed Statistics Referenced in Dissertation

All figures marked [confirmed] in the dissertation are drawn verbatim from official publications:

| Statistic | Value | Source |
|---|---|---|
| NSS 2024 response rate | 72.3% | OfS / Ipsos (2024) |
| Students responding (2024) | ~346,000 | OfS press release |
| Teaching on my course (England, 2024) | 85.3% | OfS press release |
| Student voice (England, 2024) | 74.0% | OfS press release |
| Mental wellbeing (England, 2024) | 79.0% | OfS press release |
| Student voice (England, 2023) | 71.9% | OfS press release |
| Mental wellbeing (England, 2023) | 75.9% | OfS press release |
| Graduates eligible for survey (2022/23) | 917,610 | HESA SB272 |
| Usable responses (2022/23) | 358,045 | HESA SB272 |
| Response rate | 39% | HESA SB272 |
| In employment or unpaid work | 82% | HESA SB272 |
| Full-time employment | 59% | HESA SB272 |
| Unemployed | 6% | HESA SB272 |
| Overall median salary | £28,500 | HESA SB272 |
| Science graduates — high-skilled | 82% | HESA SB272 |
| Non-science graduates — high-skilled | 72% | HESA SB272 |
| Medicine & Dentistry median salary | £37,924 | HESA SB272 |
| Media, Journalism & Comms median salary | £24,925 | HESA SB272 |
| Science overall median | £29,498 | HESA SB272 |
| Non-science overall median | £27,998 | HESA SB272 |
| Gender pay gap (overall) | £2,000 | HESA SB272 |
| Gender pay gap (high-skilled) | ~£1,900 | HESA SB272 |
| Graduate earnings growth age 23–31 | 72% vs 31% non-graduates | Universities UK (2024) |

---

## Notes on Reproducibility

- Column names in the CSV files follow the OfS and HESA data dictionaries.
- Subject groupings follow the Common Aggregation Hierarchy (CAH) used by OfS.
- Pre-2023 NSS trend figures use the Likert (5-point) scale; 2023 onwards use the 4-point item-specific scale. Direct cross-scale comparison is not valid and is noted on Figure 5.
- Russell Group membership list (24 universities) used in the RG/non-RG comparison reflects membership as of 2024.
