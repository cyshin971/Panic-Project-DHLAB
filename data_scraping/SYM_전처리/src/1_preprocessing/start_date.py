import pandas as pd
import numpy as np
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids
from functools import reduce
import datetime


# ——— 파일 경로 & 시트명 설정 ———
paths = [
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM2.xlsx',
]
start_date = load_raw_file(paths, sheet_name="연구 참여자 기본 정보")

start_date = start_date.rename(columns={'비식별키': 'ID', '연구_동의일': 'start_date'})
start_date = start_date[['ID', 'start_date']]
start_date['start_date'] = pd.to_datetime(start_date['start_date'], errors='coerce').dt.date
start_date.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/start_date.csv")
