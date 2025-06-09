import pandas as pd
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids
import datetime
import numpy as np
# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]
# 2. “공황일지” 시트를 모두 불러와 합치기
sdm = load_raw_file(paths, sheet_name='생활패턴-흡연,식사,생리')




# ——— 2. 이진 변수 변환 ———
# 흡연량 >0 → 1, else 0
sdm['흡연량'] = np.where(sdm['흡연량'] > 0, 1, 0)
# 생리 여부 Y → 1, else 0
sdm['생리'] = np.where(sdm['생리'] == 'Y', 1, 0)
# 야식 여부 Y → 1, else 0
sdm['야식'] = np.where(sdm['야식'] == 'Y', 1, 0)

# ——— 3. 불필요 컬럼 제거 ———
sdm.drop(
    columns=['아침식사','점심식사','저녁식사','오전간식','오후간식'],
    inplace=True
)

# ——— 4. 컬럼명 정리 ———
sdm = sdm.rename(columns={
    '비식별키': 'ID',
    '날짜': 'date',
    '흡연량': 'smoking',
    '야식': 'late_night_snack',
    '생리': 'menstruation'
})[['ID','date','smoking','late_night_snack','menstruation']].copy()
sdm = filter_by_valid_ids(sdm, id_column='ID')
# ——— 5. 인덱스 리셋 & 결과 저장 ———
sdm.reset_index(drop=True, inplace=True)
sdm.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/smoking_diet_mens.csv", index=False)