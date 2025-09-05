---
title: "NLHI v1.0: Newfoundland and Labrador Health Index — a desktop application for domain-specific as well as composite population‑health monitoring"
tags:
  - public health
  - epidemiology
  - health metrics
  - index
  - PyQt5
  - matplotlib
  - numpy
authors:
  - name: Mirza Niaz Zaman Elin
    affiliation: 1
affiliations:
  - name: AMAL Youth & Family Centre, St. John’s, NL, Canada
    index: 1
date: 2025-09-04
bibliography: paper.bib
---

# Summary
NLHI (Newfoundland and Labrador Health Index) is a Python desktop application that calculates and visualizes a composite measure of population‑health burden across domains and regions. The software implements the following indices: **Domain‑Specific Total Life‑Years Affected (DSTLYA)**, **Domain‑Specific Affect Value (DSAV)**, and the **NLHI composite**. Domains are user‑defined, enabling analysis for pediatrics, adults, geriatrics, or whole‑population configurations. Regions are also configurable. The application stores entries per region/date and renders NLHI trends and DSAV heatmaps to support longitudinal monitoring and policy evaluation.

# Statement of need
Health planners and researchers often require a lightweight, offline, and domain‑flexible tool to summarize burden beyond conventional hospitalization counts [@Mehta2011; @Palen2014]. NLHI provides a transparent formulation that combines domain‑specific inpatient burden and premature‑mortality burden into total life‑years affected, normalized by population size and mean age for cross‑domain comparability. The tool bridges methodological clarity with operational usability through a GUI that persists data and produces informative visualizations.

# State of the field
Summary indicators such as YLD and DALY are widely adopted for burden estimation and are reported by global initiatives [@Grosse2009; @Beresniak2025; @Solberg2020]. NLHI offers a locally configurable variant tailored for Newfoundland and Labrador workflows and adaptable to other jurisdictions. The approach complements existing dashboards by emphasizing domain‑specific configurability and a compact desktop deployment.

# Mathematical definitions
Let \(d\) index health domains and let parameters be collected per region/date.
- **DSTLYA** (Domain‑Specific Total Life‑Years Affected):
\\[
DSTLYA_d = TLIPHS_d^{(years)} + Mortality_d \times (LE - \bar{A}),
\\]
where \(TLIPHS_d^{(years)}\) converts inpatient days/weeks/months/years to years, \(Mortality_d\) is total mortality attributed to domain \(d\), \(LE\) is average life expectancy, and \(\bar{A}\) is mean age of the population.
- **DSAV** (Domain‑Specific Affect Value):
\\[
DSAV_d = \frac{DSTLYA_d \times 100}{\bar{A} \times P},
\\]
where \(P\) is population size.
- **NLHI** (Composite across \(N\) domains):
\\[
NLHI = \frac{\sum_{d=1}^{N} DSAV_d}{N}.
\\]

# Implementation
The application is written in Python and built with PyQt5 for the GUI and matplotlib for plotting. Data are stored in JSON files per machine‑local workspace. Key features include:
- Dynamic domains: add/remove domains; per‑domain inputs for TLIPHS value, unit, and domain‑specific mortality.
- Region management: add/remove regions; entries stored by date.
- Parameter inputs: mean age, population size, and average life expectancy.
- Visual analytics: NLHI line plots over time and DSAV heatmaps (domains × time).

# Quality control
Deterministic formulas are exercised through manual examples and cross‑checks of unit conversions (days, weeks, months, years to years). The GUI prevents division by zero and flags cases where life expectancy is less than or equal to mean age. JSON persistence allows regression checks by re‑loading prior entries to compare computed NLHI values.

# Availability
- **Operating system**: Windows, macOS, Linux
- **Programming language**: Python (≥3.9)
- **Dependencies**: PyQt5, numpy, matplotlib
- **Repository**: Public Git repository hosting the application source, paper, tests, and packaging metadata.
- **License**: GPL‑3.0‑only

# Author contributions
Mirza Niaz Zaman Elin: concept, methodology, software, testing, documentation, visualization, and project administration.

# Conflict of interest
No conflicts of interest to declare.

# References
