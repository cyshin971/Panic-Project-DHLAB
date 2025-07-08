import pandas as pd
import numpy as np
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids
from functools import reduce


# ——— 파일 경로 & 시트명 설정 ———
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]
steps = load_raw_file(paths, sheet_name="라이프로그-걸음수")

# ——— 1. SYM1 & SYM2 엑셀병합 & 유효 ID 필터링 ———
# raw_dfs: 각 엑셀파일에서 같은 시트 읽어서 DataFrame 리스트로
# valid_ids 필터링

# ——— 2. 중복 ID·날짜 제거 ———
foot = steps.drop_duplicates(subset=['비식별키', '날짜'], keep='last')


# ——— 4. Mi Band 사용자 데이터 제외 ———
#    '측정_유형' 컬럼이 'Mi Band'인 행을 제거
foot = foot[foot['측정_유형'] != 'MI-BAND']

# ——— 5. 측정값(NaN) 있는 행 제거 ———
foot.dropna(subset=['측정값(_1_:_값_없음)'], inplace=True)



# ——— 8. 불필요 컬럼 제거 ———
foot.drop(['총_걸음수', '측정_유형'], axis=1, inplace=True)

# ——— 9. 인덱스 리셋 ———
foot.reset_index(drop=True, inplace=True)

# ——— 10. 시계열 형태로 변환 (serialize_lifelog_data) ———
#  하루 1440분에 대응하는 시간 인덱스 생성
time_idx = pd.date_range('00:00:00', periods=1440, freq='1min').time
col_minutes = [t.strftime('%H:%M:%S') for t in time_idx]

#  '측정값(-1_:_값_없음)' 컬럼을 쉼표로 분리
split_vals = foot['측정값(_1_:_값_없음)'].str.split(',').tolist()
df_splitted = pd.DataFrame(split_vals, columns=col_minutes)

#  원본과 합치고, 원래 측정 단위·값 컬럼 제거
df_merged = pd.concat([foot[['날짜', '비식별키']].reset_index(drop=True),
                       df_splitted.reset_index(drop=True)], axis=1)

#  melt로 long 포맷 변환
foot_melted = df_merged.melt(id_vars=['날짜', '비식별키'],
                             var_name='time',
                             value_name='foot')

# ——— 11. 컬럼명 정리 & 값 정제 ———
foot_melted.rename(columns={
    '날짜': 'date',
    '비식별키': 'ID'
}, inplace=True)

#  '-1' 값을 np.nan으로 변경
foot_melted.loc[foot_melted['foot'] == '-1', 'foot'] = np.nan


#  date 컬럼을 'YYYY-MM-DD' 포맷 문자열로
foot_melted['date'] = foot_melted['date'].astype(str).str[:10]

foot_melted = filter_by_valid_ids(foot_melted, id_column="ID")


# ——— 12. 결과 저장 (CSV) ———
output_path = "/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/foot.csv"
foot_melted.to_csv(output_path, index=False)