import pandas as pd
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids

# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM2.xlsx',
]

# 2. “공황일지” 시트를 모두 불러와 합치기
panic_raw = load_raw_file(paths, sheet_name="공황일지")

# 3. 필요한 컬럼을 동적으로 찾기
cols = panic_raw.columns.tolist()

# - ID: “비식별키” 포함
id_col = next((c for c in cols if "비식별키" in c), None)
# - date: “날짜” 포함
date_col = next((c for c in cols if "날짜" in c or "Date" in c), None)
# - severity(강도): “강도” 또는 “Severity” 포함
severity_col = next((c for c in cols if "강도" in c or "Severity" in c), None)

# 4. 컬럼 존재 여부 확인
missing = [name for name, col in [("ID", id_col), ("date", date_col), ("severity", severity_col)]
           if col is None]
if missing:
    raise KeyError(f"다음 필수 컬럼을 찾을 수 없습니다: {missing}\n실제 컬럼명: {cols}")

# 5. ID, date, severity 컬럼만 추출

panic = panic_raw[[id_col, date_col, severity_col]].copy()

# 6. 날짜를 YYYY-MM-DD 문자열로 변환
panic['date'] = pd.to_datetime(panic[date_col], errors='coerce').dt.strftime("%Y-%m-%d")

# 7. panic = 2로 일괄 설정 (데이터가 존재하면 공황 기록이 있다는 의미)
panic['panic'] = 2

# 8. 컬럼 이름 통일
panic.rename(columns={
    id_col: 'ID',
    severity_col: 'severity'
}, inplace=True)

# 9. 이제 필요한 최종 컬럼 순서만 남기기
panic = panic[['ID', 'date', 'panic', 'severity']]
# 10. 유효한 ID만 남기기
panic = filter_by_valid_ids(panic, id_column="ID")
# 11. 같은 ID, date에 중복된 행이 있을 경우 severity와 panic의 최대값만 남기기
panic = panic.groupby(['ID', 'date'], as_index=False).agg({
    'panic': 'max',
    'severity': 'max'
})
# 10. 저장 (필요 시 feather 또는 CSV로)
panic.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/panic_by_date.csv")