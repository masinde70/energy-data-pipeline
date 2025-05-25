# Data Processing Scripts

This directory contains Python scripts for data ingestion, processing, and exploration.

## Scripts

### explore.py

This script explores the ENTSO-E electricity load data. It performs basic exploratory data analysis including:
- Data overview and shape
- First few rows inspection
- Data types
- Summary statistics
- Null value checks
- Time range analysis
- Basic visualization of electricity load over time

#### Usage

```bash
python explore.py
```

#### Requirements
- pandas
- matplotlib
- Python 3.6+

The script expects the ENTSO-E data to be available at `../data/entsoe_load.csv`.
