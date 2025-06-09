from utils_for_preprocessing import read_all_data
import pandas as pd

BASE_PASSIVE_DIR = '/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox/pixelpanic_raw_data.zip'

heartrate = read_all_data('HeartRate', BASE_PASSIVE_DIR, exclude_keywords=['resting', 'variability'])

# Convert obtained_at to datetime then split into date and time
heartrate['obtained_at'] = pd.to_datetime(heartrate['obtained_at'])
heartrate['date'] = heartrate['obtained_at'].dt.date.astype(str)
heartrate['time'] = heartrate['obtained_at'].dt.time.astype(str)

# Drop unneeded columns and reset index
heartrate = heartrate.drop(columns=['started_at', 'ended_at', 'obtained_at']).reset_index(drop=True)
heartrate.to_csv("/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR.csv", index=False)