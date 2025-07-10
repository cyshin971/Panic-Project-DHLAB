import pandas as pd
import zipfile
from io import BytesIO


import pandas as pd
from functools import reduce

# (1) CSV 파일 로드 & 'Unnamed' 인덱스 컬럼 제거 함수
def load_and_clean(path):
    df = pd.read_csv(path)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df

# (2) 모든 CSV 불러오기
preprocessed = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/1_stage/전처리 결과/processed.csv")
band_power            = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/bandpower_720.csv")
circadian_delta       = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/circadian_delta_720.csv")
step_delta = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/step_delta.csv")
HR_date               = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/HR_date_fixed.csv")
sleep                 = load_and_clean("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/sleep_type.csv")

# (3) 날짜 기반 데이터 리스트
date_dfs = [
    preprocessed,
    band_power,
    circadian_delta,
    step_delta,
    HR_date,
    sleep,
]

# (3.5) 모든 date 컬럼을 datetime 타입으로 변환
for df in date_dfs:
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

# (5) 모든 (ID, date) 조합을 마스터 키로 생성
all_keys = pd.concat([df[['ID', 'date']] for df in date_dfs])
all_keys = all_keys.drop_duplicates().dropna()

# (6) 각 df를 마스터 키 기준으로 align
def align_to_master(df):
    return pd.merge(all_keys, df, how='left', on=['ID', 'date'])

aligned_dfs = [align_to_master(df) for df in date_dfs]

# (7) 모든 날짜별 테이블을 outer join 으로 순차 병합 (순서 영향 없음)
merged_all = reduce(lambda left, right: pd.merge(left, right, how='outer', on=['ID', 'date']), aligned_dfs)


merged_full = merged_all.sort_values(['ID','date'])

# (11) 컬럼 정리 및 결측 처리
merged_full.rename(columns={
    'amp': 'HR_amplitude',           'mesor': 'HR_mesor',         'acr': 'HR_acrophase',
    'amp_delta': 'HR_amplitude_difference',  'mesor_delta': 'HR_mesor_difference',   'acr_delta': 'HR_acrophase_difference',
    'amp_delta2': 'HR_amplitude_difference_2d',  'mesor_delta2': 'HR_mesor_difference_2d',  'acr_delta2': 'HR_acrophase_difference_2d',
    'step_max': 'steps_maximum',    'step_var': 'steps_variance',
    'step_mean': 'steps_mean', 
    'negative': 'negative_feeling',
    'bandpower_a': 'bandpower(0.001-0.0005Hz)', 
    'bandpower_b': 'bandpower(0.0005-0.0001Hz)',
    'bandpower_c': 'bandpower(0.0001-0.00005Hz)', 
    'bandpower_d': 'bandpower(0.00005-0.00001Hz)',
    'suicide_need_in_month': 'suicide_need'
}, inplace=True)



# (12) date 컬럼이 datetime 타입인 경우, 문자열 YYYY-MM-DD로 변환
if 'date' in merged_full.columns:
    merged_full['date'] = merged_full['date'].dt.strftime('%Y-%m-%d')

# (13) 컬럼 순서: ID, date, panic → 나머지
cols = merged_full.columns.tolist()
ordered_cols = ['ID', 'date', 'panic'] + [c for c in cols if c not in ['ID', 'date', 'panic']]
merged_full = merged_full[ordered_cols]

merged_full.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/result/result_before_severity.csv")


# 1. Load all_data and prepare the 'severity' column
all_data_path = "/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/result/result_before_severity.csv"
all_data = pd.read_csv(all_data_path, dtype={"ID": str})

# Ensure 'date' is in datetime.date format for matching
all_data["date"] = pd.to_datetime(all_data["date"]).dt.date

# Initialize a new column 'severity' with NaN
all_data["severity"] = pd.NA


# 2. Fill 'severity' for PXPN-group patients by reading each patient's panic CSV inside the nested ZIP
zip_path = "/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox/pixelpanic_raw_data.zip"
with zipfile.ZipFile(zip_path, "r") as outer_zip:
    # patient indices run from 6 to 40 (inclusive)
    for i in range(6, 41):
        formatted_index = f"{i:02d}"
        patient_code = f"PXPN_100{formatted_index}"
        inner_zip_name = f"ActiveData/{patient_code}_ActiveData.zip"

        # Skip if the inner zip for this patient isn't present
        if inner_zip_name not in outer_zip.namelist():
            continue

        # Read the inner ZIP from the outer ZIP into memory
        inner_zip_bytes = BytesIO(outer_zip.read(inner_zip_name))
        with zipfile.ZipFile(inner_zip_bytes, "r") as inner_zip:
            inner_file_name = f"{patient_code}_Panic.csv"
            if inner_file_name not in inner_zip.namelist():
                continue

            # Open the patient's panic CSV
            with inner_zip.open(inner_file_name) as f:
                df_panic = pd.read_csv(f, dtype={"강도": float})

            # Convert the 작성일 column to datetime.date
            df_panic["작성일"] = pd.to_datetime(df_panic["작성일"]).dt.date

            # For each row in df_panic, match ID & date, then assign '강도' to all_data['severity']
            for _, row in df_panic.iterrows():
                panic_date = row["작성일"]
                severity_val = row["강도"]

                mask = (all_data["ID"] == patient_code) & (all_data["date"] == panic_date)
                if mask.any():
                    all_data.loc[mask, "severity"] = severity_val


# 5. (Optional) Check how many rows still have NaN in severity
num_missing = all_data["severity"].isna().sum()
print(f"Number of rows with missing severity: {num_missing}")

# 6. Save the updated DataFrame
output_path = "/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/result/result_720_no_fill.csv"
all_data.to_csv(output_path, index=False)
