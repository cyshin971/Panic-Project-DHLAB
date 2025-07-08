from utils_for_preprocessing import read_all_data
import pandas as pd

BASE_PASSIVE_DIR = '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox/pixelpanic_raw_data.zip'

sleep = read_all_data('Sleep', BASE_PASSIVE_DIR, exclude_keywords=['resting', 'variability'])

sleep = sleep.drop(columns='type')
sleep.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/sleep_log.csv")

