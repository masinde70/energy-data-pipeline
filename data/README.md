# ENTSO-E Data Download Guide

This guide explains how to download electricity load data from the ENTSO-E Transparency Platform.

## Steps to Download ENTSO-E Data

1. **Visit the ENTSO-E Transparency Platform**:
   - Go to [https://transparency.entsoe.eu/](https://transparency.entsoe.eu/)
   - You may need to create a free account to download data

2. **Navigate to the Load Domain**:
   - From the main menu, select "Load" 
   - Then select "Total Load - Day Ahead / Actual"

3. **Set your filters**:
   - Select "Finland" as the Country/Bidding Zone
   - Set the date range to a period in 2024 that gives you approximately 1000 rows
   - Typically this would be about 1-2 months of hourly data

4. **Export the data**:
   - Click on "Export" button
   - Select "CSV" as the format
   - Download the file

5. **Save the file**:
   - Save the downloaded file as `entsoe_load.csv` in the `data` directory of this project

## Expected Data Format

The downloaded CSV file should have columns similar to:
- Area/Country
- DateTime (timestamp)
- Total Load Forecast (load_mw)
- Resolution

You may need to rename or restructure the columns to match:
- `timestamp` - The date and time of the measurement
- `load_mw` - The forecasted or actual load in megawatts
- `region` - The region or country (e.g., "Finland")

## Sample Data

If you're unable to download the data immediately, a placeholder CSV has been created with the expected structure for testing the exploration script.
