from utils_for_preprocessing import read_all_data
import pandas as pd
import datetime as dt

BASE_PASSIVE_DIR = '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox/pixelpanic_raw_data.zip'

step = read_all_data('Step', BASE_PASSIVE_DIR, exclude_keywords=['resting', 'variability'])

# Convert obtained_at to datetime then split into date and time
step['started_at'] = pd.to_datetime(step['started_at'])
step['date'] = step['started_at'].dt.date.astype(str)
step['time'] = step['started_at'].dt.time.astype(str)


# Drop unneeded columns and reset index
step = step.drop(columns=['started_at', 'ended_at', 'obtained_at']).reset_index(drop=True)
step.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/step.csv", index=False)