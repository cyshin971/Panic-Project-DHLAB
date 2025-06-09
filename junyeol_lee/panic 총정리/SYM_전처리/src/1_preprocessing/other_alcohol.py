import pandas as pd
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids

# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]

# 2. “생활패턴-음주” 시트를 모두 불러와 합치기
alcohol_raw = load_raw_file(paths, sheet_name="생활패턴-음주")

# 3. ID와 날짜 컬럼을 동적으로 찾기
id_col = next((c for c in alcohol_raw.columns if "비식별키" in c), None)
date_col = next((c for c in alcohol_raw.columns if "날짜" in c), None)

if id_col is None:
    raise KeyError(f"ID 컬럼('비식별키' 포함)을 찾지 못했습니다. 가능한 컬럼: {alcohol_raw.columns.tolist()}")
if date_col is None:
    raise KeyError(f"날짜 컬럼('날짜' 포함)을 찾지 못했습니다. 가능한 컬럼: {alcohol_raw.columns.tolist()}")

# 4. ID와 날짜만 추출
df = alcohol_raw[[id_col, date_col]].copy()

# 5. 날짜를 YYYY-MM-DD 문자열로 변환
df['date'] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime("%Y-%m-%d")

# 6. 컬럼명을 통일하여 ['ID', 'date']로 이름 변경
df = df.rename(columns={id_col: 'ID'})

# 7. 한 사람(비식별키)이 특정 날짜에 음주 기록이 있으면 alcohol=1, 없으면 해당 행이 존재하지 않음
#    → 즉, 중복 제거만 하면 한 ID/날짜당 한 행이 남고, alcohol 컬럼을 1로 설정
df = df.drop_duplicates(subset=['ID', 'date'], ignore_index=True)
df['alcohol'] = 1

# 8. 최종 컬럼 순서: ['ID', 'date', 'alcohol']
df = df[['ID', 'date', 'alcohol']]
df = filter_by_valid_ids(df, id_column='ID')
# 9. 필요에 따라 저장 (예: feather)
df.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/alcohol_per_date.csv")