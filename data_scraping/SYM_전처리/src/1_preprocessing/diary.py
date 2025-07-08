import pandas as pd
import numpy as np
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids
from functools import reduce


# ——— 파일 경로 & 시트명 설정 ———
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]
diary = load_raw_file(paths, sheet_name="일기")
diary = diary.rename(columns={'비식별키': 'ID', '날짜' : 'date', '기분' : 'mood', '내용' : 'contents'})
diary = filter_by_valid_ids(diary ,id_column="ID")

diary = diary.drop_duplicates(subset=['ID', 'date'], keep='last')
diary.dropna(subset=['contents'], inplace=True)
diary = diary.drop(columns=['시간'])
diary.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/diary.csv")