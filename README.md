# NLHI — Newfoundland and Labrador Health Index

NLHI is a Python desktop application for computing and visualizing a composite health‑burden index across configurable domains and regions.

## Features
- Dynamic domains: add/remove domains; per‑domain TLIPHS value, time unit, and domain‑specific mortality.
- Region management: add/remove regions.
- Parameters: mean age, population size, and average life expectancy.
- Visualizations: NLHI over time and DSAV heatmaps.
- Local JSON persistence; no external network dependency for computation.

## Mathematical definitions
- **DSTLYA**: \( DSTLYA_d = TLIPHS_d^{(years)} + Mortality_d (LE - \bar{A}) \)
- **DSAV**: \( DSAV_d = 100 \times DSTLYA_d / (\bar{A} \times P) \)
- **NLHI**: \( NLHI = (\sum_{d=1}^N DSAV_d)/N \)

Units use: 1 year = 365.25 days; 1 year = 52.1429 weeks; 1 year = 12 months.

## Installation
Python ≥ 3.9 recommended.
```bash
pip install PyQt5 numpy matplotlib
```

## Usage
Run the application script:
```bash
python NLHI_v1.0.py
```
Create or select a region, enter mean age, population size, life expectancy, and add domain rows with TLIPHS and mortality. Save and open the dashboard to inspect NLHI trends and DSAV heatmaps.

## Data files
- `nlhi_data.json`: persisted entries per region/date
- `regions.json`: list of regions
- `credentials.json`: local authentication store

## Citation
See `CITATION.cff` and the JOSS paper (to appear).

## License
GPL‑3.0‑only. See `LICENSE`.
