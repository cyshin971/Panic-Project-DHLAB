import pandas as pd
import numpy as np
from datetime import datetime
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids

# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]

# 2. “연구 참여자 기본 정보” 시트를 모두 불러와 합치기
raw = load_raw_file(paths, sheet_name="연구 참여자 기본 정보")

# 3. 필요한 컬럼을 동적으로 찾기
cols = raw.columns.tolist()

# - ID: “비식별키” 포함
id_col = next((c for c in cols if "비식별" in c), None)

# - Date_of_birth: “Date_of_birth” 또는 “Birth” 등 날짜 포함
dob_col = next((c for c in cols if "Date_of_birth" in c or "생년월일" in c), None)

# - Gender: “Gender” 또는 “성별”
gender_col = next((c for c in cols if "Gender" in c or "성별" in c), None)

ht_col = next(
    (c for c in cols
     if (("height" in c or "키" in c) and "비식별" not in c)),
    None
)

# - Weight: “Weight” 또는 “체중”
wt_col = next((c for c in cols if "Weight" in c or "몸무게" in c), None)

# - Marriage: “Marital” 또는 “혼인” 등
marriage_col = next((c for c in cols if "Marital" in c or "결혼" in c), None)

# - Job: “Occupation” 또는 “직업”
job_col = next((c for c in cols if "Occupation" in c or "직업" in c), None)

# - Smoker history: “Smoker” 또는 “Smoking” 등
smkHx_col = next((c for c in cols if "Smoker" in c or "과거_흡연_여부" in c), None)

# - Drinker history: “Drinker” 또는 “Drinking” 등
drinkHx_col = next((c for c in cols if "Drinker" in c or "음주_여부" in c), None)

# - Suicide history: “Suicide_history” 또는 “자살” 등
suicideHx_col = next(
    (c for c in cols
     if (("Suicide_history" in c or "자살_시도_여부" in c) and "1달" not in c)),
    None
)

# - Suicide ideation in past month: “Suicide_ideation” 또는 “Self_harm” 등
suicide_need_col = next((c for c in cols if "Suicide_ideation" in c or "자살_시도_욕구" in c), None)

# - Medication in past month: “Medication_history” 또는 “Medication” 등
medication_col = next((c for c in cols if "Medication_history" in c or "처방약_여부" in c), None)

# 4. 칼럼 존재 여부 확인

required = {
    "ID": id_col,
    "Date_of_birth": dob_col,
    "Gender": gender_col,
    "Height": ht_col,
    "Weight": wt_col,
    "Marriage": marriage_col,
    "Job": job_col,
    "Smoker_history": smkHx_col,
    "Drinker_history": drinkHx_col,
    "Suicide_history": suicideHx_col,
    "Suicide_ideation": suicide_need_col,
    "Medication_history": medication_col,
}

missing = [name for name, col in required.items() if col is None]
if missing:
    raise KeyError(f"다음 필수 컬럼을 찾을 수 없습니다: {missing}\n실제 컬럼명: {cols}")

# 5. 필요한 컬럼만 골라서 복사
demographic_data = raw[
    [
        id_col,
        dob_col,
        gender_col,
        ht_col,
        wt_col,
        marriage_col,
        job_col,
        smkHx_col,
        drinkHx_col,
        suicideHx_col,
        suicide_need_col,
        medication_col,
    ]
].copy()

# 6. '생년월일' 컬럼명을 'Date_of_birth'로 변경
demographic_data.rename(columns={dob_col: "Date_of_birth"}, inplace=True)

# 7. Date_of_birth → datetime64로 변환 (형식: YYYYMMDD)
demographic_data["Date_of_birth"] = pd.to_datetime(
    demographic_data["Date_of_birth"],
    format="%Y%m%d",
    errors="coerce"
)
# 변환 실패한 항목은 NaT가 되며, 이후 계산 시 주의

# 8. 오늘 날짜 기준으로 나이(age) 계산
today = datetime.now().date()

# datetime64 시리즈인 'Date_of_birth' 그대로 .dt 속성 사용
birth_dates = demographic_data["Date_of_birth"]
birth_years = birth_dates.dt.year
birth_months = birth_dates.dt.month
birth_days = birth_dates.dt.day

# year 차이 계산
years_diff = today.year - birth_years

# 생일이 아직 안 지난 경우 보정
adjust = (
    (today.month < birth_months)
    | ((today.month == birth_months) & (today.day < birth_days))
).astype(int)

# 나이 계산 (NaT로 인해 생기는 NaN은 0으로 대체 후 정수화)
ages = (years_diff - adjust).fillna(0).astype(int)

# 9. 'age' 컬럼으로 삽입
demographic_data["age"] = ages

# 10. 이후 더 이상 'Date_of_birth' 컬럼은 필요 없으니 삭제
demographic_data.drop(columns=["Date_of_birth"], inplace=True)

# 11. 컬럼명 개별 매핑
demographic_data.rename(columns={
    id_col: "ID",
    gender_col: "gender",
    ht_col: "ht",
    wt_col: "wt",
    marriage_col: "marriage",
    job_col: "job",
    smkHx_col: "smkHx",
    drinkHx_col: "drinkHx",
    suicideHx_col: "suicideHx",
    suicide_need_col: "suicide_need_in_month",
    medication_col: "medication_in_month"
}, inplace=True)
# 'age' 컬럼은 이미 올바른 이름이므로 그대로 둡니다.

# 12. 범주형 변수를 1/0으로 변환
demographic_data["marriage"] = demographic_data["marriage"].astype(str).str.upper().eq("Y").astype(int)
demographic_data["job"] = demographic_data["job"].astype(str).str.upper().eq("Y").astype(int)
demographic_data["smkHx"] = demographic_data["smkHx"].astype(str).str.upper().eq("Y").astype(int)
demographic_data["drinkHx"] = demographic_data["drinkHx"].astype(str).str.upper().eq("Y").astype(int)
demographic_data["suicideHx"] = demographic_data["suicideHx"].astype(str).str.upper().eq("Y").astype(int)
demographic_data["suicide_need_in_month"] = (
    demographic_data["suicide_need_in_month"].astype(str).str.upper().eq("Y").astype(int)
)
demographic_data["medication_in_month"] = (
    demographic_data["medication_in_month"].astype(str).str.upper().eq("Y").astype(int)
)
demographic_data["gender"] = demographic_data["gender"].astype(str).str.upper().map({"M": 1, "F": 0}).fillna(0).astype(int)

# 13. 유효한 ID만 필터링
print(demographic_data.columns)
demographic_data = filter_by_valid_ids(demographic_data, id_column="ID")

# 14. 인덱스 리셋 및 저장
demographic_data.reset_index(drop=True, inplace=True)
demographic_data.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/demographic_data.csv")