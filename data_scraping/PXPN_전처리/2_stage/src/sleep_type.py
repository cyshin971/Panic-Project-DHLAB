from utils_for_preprocessing import read_all_data
import pandas as pd

BASE_PASSIVE_DIR = '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox/pixelpanic_raw_data.zip'

sleep = read_all_data('Sleep', BASE_PASSIVE_DIR, exclude_keywords=['resting', 'variability'])

# Map various sleep type labels into standardized SLT codes
sleep['type'] = sleep['type'].replace({
    'SLT1': 'SLT3',
    'SLT0': 'SLT2',
    'asleepCore': 'SLT4',
    'asleepDeep': 'SLT5',
    'asleepREM': 'SLT6',
    'asleepUnspecified': 'SLT2',
    'awake': 'SLT1'
})

# Ensure datetime types for start and end
sleep['started_at'] = pd.to_datetime(sleep['started_at'])
sleep['ended_at'] = pd.to_datetime(sleep['ended_at'])

# Calculate session duration
sleep['duration'] = sleep['ended_at'] - sleep['started_at']

# Extract date for grouping
sleep['date'] = sleep['started_at'].dt.date

# Pivot to sum durations per SLT type
sleep_summary = sleep.pivot_table(
    index=['ID', 'date'],
    columns='type',
    values='duration',
    aggfunc='sum',
    fill_value=pd.Timedelta(0)
)

# Ensure all SLT1–SLT6 columns exist
for slt in ['SLT1', 'SLT2', 'SLT3', 'SLT4', 'SLT5', 'SLT6']:
    if slt not in sleep_summary.columns:
        sleep_summary[slt] = pd.Timedelta(0)

# Compute total sleep as sum of all SLT durations
sleep_summary['total_sleep'] = sleep_summary[['SLT1', 'SLT2', 'SLT3', 'SLT4', 'SLT5', 'SLT6']].sum(axis=1)

# Convert SLT and total_sleep durations from Timedelta to hours (float)
for col in ['SLT1', 'SLT2', 'SLT3', 'SLT4', 'SLT5', 'SLT6', 'total_sleep']:
    sleep_summary[col] = sleep_summary[col] / pd.Timedelta(hours=1)

# Convert index back to columns
sleep_summary = sleep_summary.reset_index()

# Overwrite sleep with the summary table
sleep = sleep_summary


sleep.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/sleep_type.csv", index=False)
