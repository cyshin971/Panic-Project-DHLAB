import pandas as pd
from functools import reduce

# (1) CSV 파일 로드 & 'Unnamed' 인덱스 컬럼 제거 함수
def load_and_clean(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df

# (2) 모든 CSV 불러오기
Alcohol_per_date      = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/alcohol_per_date.csv")
band_power            = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/bandpower.csv")
circadian_delta       = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/circadian_delta.csv")
coffee_date           = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/coffee_per_date.csv")
emotion_diary         = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/emotion_diary.csv")
exercise_date         = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/exercise_per_date.csv")
step_delta = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/step_delta.csv")
HR_date               = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/HR_date.csv")
panic                 = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/panic_by_date.csv") \
                            .drop(columns=['time','datetime'], errors='ignore')
questionnaire_bydate  = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/questionnaire.csv")
sleep                 = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/sleep_summary.csv")
smoking_diet_mens     = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/smoking_diet_mens.csv")
demographic_data      = load_and_clean("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/demographic_data.csv")

# (3) 날짜 기반 데이터 리스트
date_dfs = [
    Alcohol_per_date,
    band_power,
    circadian_delta,
    coffee_date,
    emotion_diary,
    exercise_date,
    step_delta,
    HR_date,
    panic,
    questionnaire_bydate,
    sleep,
    smoking_diet_mens
]

# (3.5) 모든 date 컬럼을 datetime 타입으로 변환
for df in date_dfs:
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

# (5) 모든 (ID, date) 조합을 마스터 키로 생성
all_keys = pd.concat([df[['ID', 'date']] for df in date_dfs])
all_keys = all_keys.drop_duplicates().dropna()

# (6) all_keys에 demographic 정보 붙여 master_key 생성
master_key = pd.merge(
    all_keys,
    demographic_data,
    how='left',  # all_keys의 ID-date 조합만 복제
    on='ID'
)

# (7) date 정보가 없는 ID 처리: demographic-only IDs를 한 행으로 추가
ids_with_dates = all_keys['ID'].unique()
demog_only = demographic_data[~demographic_data['ID'].isin(ids_with_dates)].copy()
demog_only['date'] = pd.NaT
# demographic-only 행 추가
master_key = pd.concat([master_key, demog_only], ignore_index=True)

# (8) master_key 위에 날짜 기반 데이터를 순차적으로 left join
merged_full = master_key
for df in date_dfs:
    merged_full = pd.merge(
        merged_full,
        df,
        how='left',
        on=['ID', 'date']
    )

# (9) panic 값이 잘 살아 있는지 확인
print("📌 panic value counts (before any drop/fill):")
print(merged_full['panic'].value_counts(dropna=False))

# (10) ffill 대상 컬럼 정의
survey_cols = [
    'BRIAN','CSM','CTQ_1','CTQ_2','CTQ_3','CTQ_4','CTQ_5',
    'KRQ','MDQ','SPAQ_1','SPAQ_2','STAI_X2','ACQ',
    'APPQ_1','APPQ_2','APPQ_3','BSQ','BFNE','CES_D',
    'GAD_7','KOSSSF','PHQ_9','SADS','STAI_X1'
]
band_cols   = [c for c in merged_full.columns if c.startswith('bandpower')]
ffill_cols  = [c for c in survey_cols + band_cols if c in merged_full.columns]

# panic 컬럼은 ffill 대상에서 제외
merged_full = merged_full.sort_values(['ID','date'])
merged_full[ffill_cols] = merged_full.groupby('ID')[ffill_cols].ffill()

# (11) 컬럼 정리 및 결측 처리
merged_full.rename(columns={
    'amp': 'HR_amplitude',           'mesor': 'HR_mesor',         'acr': 'HR_acrophase',
    'amp_delta': 'HR_amplitude_difference',  'mesor_delta': 'HR_mesor_difference',   'acr_delta': 'HR_acrophase_difference',
    'amp_delta2': 'HR_amplitude_difference_2d',  'mesor_delta2': 'HR_mesor_difference_2d',  'acr_delta2': 'HR_acrophase_difference_2d',
    'positive': 'positive_feeling', 
    'negative': 'negative_feeling',
    'step_max': 'steps_maximum',    'step_var': 'steps_variance',
    'step_mean': 'steps_mean', 
    'bandpower_a': 'bandpower(0.001-0.0005Hz)', 
    'bandpower_b': 'bandpower(0.0005-0.0001Hz)',
    'bandpower_c': 'bandpower(0.0001-0.00005Hz)', 
    'bandpower_d': 'bandpower(0.00005-0.00001Hz)',
    'suicide_need_in_month': 'suicide_need'
}, inplace=True)

merged_full.drop(['ht','wt','late_night_snack'], axis=1, inplace=True, errors='ignore')
merged_full['alcohol'] = merged_full['alcohol'].fillna(0)
merged_full['exercise'] = merged_full['exercise'].fillna(0)
merged_full['coffee'] = merged_full['coffee'].fillna(0)
merged_full['smoking'] = merged_full['smoking'].fillna(0)
merged_full['menstruation'] = merged_full['menstruation'].fillna(0)

# (12) date 컬럼이 datetime 타입인 경우, 문자열 YYYY-MM-DD로 변환
if 'date' in merged_full.columns:
    merged_full['date'] = merged_full['date'].dt.strftime('%Y-%m-%d')

# (13) 컬럼 순서: ID, date, panic → 나머지
cols = merged_full.columns.tolist()
ordered_cols = ['ID', 'date', 'panic'] + [c for c in cols if c not in ['ID', 'date', 'panic']]
merged_full = merged_full[ordered_cols]

# (13.5) panic == 2인 날의 이전 날에 panic == 1 채우기
merged_full = merged_full.sort_values(['ID', 'date']).reset_index(drop=True)
for i in range(1, len(merged_full)):
    if merged_full.loc[i, 'panic'] == 2:
        j = i - 1
        while j >= 0 and merged_full.loc[j, 'ID'] == merged_full.loc[i, 'ID']:
            if pd.isna(merged_full.loc[j, 'panic']):
                merged_full.loc[j, 'panic'] = 1
                break
            elif merged_full.loc[j, 'panic'] == 2:
                j -= 1
            else:
                break

# (14) panic의 남은 NaN은 0으로 처리
merged_full['panic'] = merged_full['panic'].fillna(0)

print("📌 panic value counts after concat:")
print(merged_full['panic'].value_counts(dropna=False))


# ───────────────────────────────────────────
# (16) panic 라벨 감소 원인별 개수 확인
# ───────────────────────────────────────────

# 1) ID·date 순으로 정렬된 DataFrame이 필요하므로 다시 정렬
merged_full = merged_full.sort_values(['ID', 'date']).reset_index(drop=True)

# 2) 전체 panic==2, panic==1 개수 구하기
total_2 = (merged_full['panic'] == 2).sum()
total_1 = (merged_full['panic'] == 1).sum()

# 3) 카운터 초기화
skipped_consecutive_2 = 0    # 연속된 2로 인해 1로 채우기 대상에서 제외된 경우
skipped_first_date = 0       # 해당 ID에서 첫날이 2라서 앞에 쓸 수 없어서 제외된 경우
skipped_non_nan_prev = 0     # 전날 값이 이미 NaN이 아닌(0 혹은 1)이어서 1로 덮어쓰지 않은 경우

# 4) ID별로 순회하며 스킵 케이스 계산
for id_, group in merged_full.groupby('ID'):
    group = group.reset_index(drop=True)
    for i in range(len(group)):
        if group.loc[i, 'panic'] == 2:
            if i == 0:
                # (2) ID별 첫날이 panic==2인 경우
                skipped_first_date += 1
            else:
                prev_val = group.loc[i-1, 'panic']
                if prev_val == 2:
                    # (1) 연속된 2인 경우: 첫 번째 2의 전날만 1로 채우고 이후 연속된 2들은 전날이 2라서 skip
                    skipped_consecutive_2 += 1
                elif pd.notna(prev_val):
                    # (3) 전날 값이 NaN이 아닌(즉 이미 0 혹은 1로 채워짐) 경우 → 덮어쓰지 않고 skip
                    skipped_non_nan_prev += 1
                # 만약 prev_val이 NaN이면 정상적으로 1로 라벨링됐으므로 제외

# 5) 설명되지 않는 나머지 차이 계산
explained = skipped_consecutive_2 + skipped_first_date + skipped_non_nan_prev
unexplained = total_2 - explained

# 6) 결과 출력
print("\n──────── Panic Label Analysis ────────")
print(f"Total panic==2 count:                       {total_2}")
print(f"Total panic==1 count:                       {total_1}")
print(f"Skipped due to consecutive 2:               {skipped_consecutive_2}")
print(f"Skipped due to first date being 2:          {skipped_first_date}")
print(f"Skipped due to previous not NaN (already labeled): {skipped_non_nan_prev}")
print(f"Unexplained difference:                     {unexplained}")
print("────────────────────────────────────────\n")


## (17) SYM1-1-343, 2021-05-22 중복 처리: 첫 번째 행 드롭 (마지막 행 유지)
mask = (merged_full['ID'] == 'SYM1-1-343') & (merged_full['date'] == '2021-05-22')
dup_idxs = merged_full[mask].index
if len(dup_idxs) > 1:
    merged_full = merged_full.drop(dup_idxs[0])

# (15) 저장
merged_full.to_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/result/result.csv", index=False)
merged_full_dropna = merged_full.dropna()
merged_full_dropna.to_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/result/result_dropna.csv", index=False)

print("✅ 저장 완료: result.csv / result_dropna.csv")