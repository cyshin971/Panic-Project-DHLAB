import pandas as pd
from functools import reduce
import os
output_folder = ("/Panic-Project-DHLAB/tmp/SYM")

# (1) CSV 파일 로드 & 'Unnamed' 인덱스 컬럼 제거 함수
def load_and_clean(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df

# (2) 모든 CSV 불러오기
output_path = os.path.join(output_folder, "start_date.csv")
start_date = load_and_clean(output_path)
start_date['start_date'] = pd.to_datetime(start_date['start_date'], errors='coerce')
output_path = os.path.join(output_folder, "alcohol_per_date.csv")
Alcohol_per_date      = load_and_clean(output_path)
output_path = os.path.join(output_folder, "bandpower_fixed_720.csv")
band_power            = load_and_clean(output_path)
output_path = os.path.join(output_folder, "circadian_delta_720.csv")
circadian_delta       = load_and_clean(output_path)
output_path = os.path.join(output_folder, "coffee_per_date.csv")
coffee_date           = load_and_clean(output_path)
output_path = os.path.join(output_folder, "emotion_diary.csv")
emotion_diary         = load_and_clean(output_path)
output_path = os.path.join(output_folder, "exercise_per_date.csv")
exercise_date         = load_and_clean(output_path)
output_path = os.path.join(output_folder, "step_delta.csv")
step_delta = load_and_clean(output_path)
output_path = os.path.join(output_folder, "HR_date_fixed.csv")
HR_date               = load_and_clean(output_path)
output_path = os.path.join(output_folder, "panic_by_date.csv")
panic                 = load_and_clean(output_path).drop(columns=['time','datetime'], errors='ignore')
output_path = os.path.join(output_folder, "questionnaire.csv")
questionnaire_bydate  = load_and_clean(output_path)
output_path = os.path.join(output_folder, "sleep_summary.csv")
sleep                 = load_and_clean(output_path)
output_path = os.path.join(output_folder, "smoking_diet_mens.csv")
smoking_diet_mens     = load_and_clean(output_path)
output_path = os.path.join(output_folder, "demographic_data.csv")
demographic_data      = load_and_clean(output_path)
output_path = os.path.join(output_folder, "diary.csv")
diary = load_and_clean(output_path)
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
    smoking_diet_mens,
    diary
]


# (3.5) 모든 date 컬럼을 datetime 타입으로 변환
for df in date_dfs:
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

# (3.6) Check for records with a date earlier than the observed min_date for each ID
# Using min_date computed below in section (5.1)
# First, ensure min_date is computed before this block (move section (5.1) above section (3.6)), or compute here:
min_date = (
    pd.concat([df[['ID','date']] for df in date_dfs if 'date' in df.columns])
    .dropna()
    .assign(date=lambda x: pd.to_datetime(x['date'], errors='coerce'))
    .groupby('ID')['date']
    .min()
    .reset_index()
    .rename(columns={'date':'min_date'})
)
for df, name in zip(
    date_dfs,
    [
        'Alcohol_per_date', 'band_power', 'circadian_delta',
        'coffee_date', 'emotion_diary', 'exercise_date',
        'step_delta', 'HR_date', 'panic', 'questionnaire_bydate',
        'sleep', 'smoking_diet_mens', 'diary'
    ]
):
    # Merge each dataframe's dates with min_date by ID
    merged_dates = pd.merge(
        df[['ID', 'date']],
        min_date,
        on='ID',
        how='left'
    )
    # Find records where date < min_date
    earlier = merged_dates[merged_dates['date'] < merged_dates['min_date']]
    if not earlier.empty:
        print(f"⚠️ DataFrame {name} has {len(earlier)} records with date earlier than observed min_date")
        print(earlier.to_string(index=False))


# (5) 모든 (ID, date) 조합을 마스터 키로 생성
all_dates = pd.concat([df[['ID', 'date']] for df in date_dfs if 'date' in df.columns]).dropna()
all_dates['date'] = pd.to_datetime(all_dates['date'])

# (5.2) ID별 실제 데이터에서 가장 늦은 date를 구해 end_date 생성
end_date = (
    all_dates
    .groupby('ID')['date']
    .max()
    .reset_index()
    .rename(columns={'date':'end_date'})
)

# (5.3) min_date와 end_date 병합
id_date_range = pd.merge(min_date, end_date, on='ID', how='inner')

# 5.3) 각 ID별로 date range 생성
expanded_rows = []
for _, row in id_date_range.iterrows():
    id_ = row['ID']
    start = row['min_date']
    end = row['end_date']
    date_range = pd.date_range(start, end, freq='D')
    expanded_rows.extend([{'ID': id_, 'date': d} for d in date_range])

all_keys = pd.DataFrame(expanded_rows)

# (5.5) diary로 인해 추가된 (ID, date) 조합 확인
date_dfs_wo_diary = [df for df in date_dfs if not df.equals(diary)]
all_keys_wo_diary = pd.concat([df[['ID', 'date']] for df in date_dfs_wo_diary]).drop_duplicates().dropna()

new_keys_from_diary = pd.merge(
    all_keys,
    all_keys_wo_diary,
    how='outer',
    indicator=True
).query("_merge == 'left_only'")[['ID', 'date']]

print("📌 diary로 인해 추가된 새로운 (ID, date) 조합 수:", len(new_keys_from_diary))
print(new_keys_from_diary.head())

# (6) all_keys에 demographic 정보 붙여 master_key 생성
master_key = pd.merge(
    all_keys,
    demographic_data,
    how='left',  # all_keys의 ID-date 조합만 복제
    on='ID'
)

# === Debug: demographic_data age 확인 ===
if 'age' in demographic_data.columns:
    print("🛠 demographic_data: total rows:", len(demographic_data))
    print("🛠 demographic_data: age NaN count:", demographic_data['age'].isna().sum())
    print("🛠 demographic_data: sample IDs with missing age:", demographic_data.loc[demographic_data['age'].isna(), 'ID'].unique()[:10])
else:
    print("🛠 demographic_data에 'age' 컬럼이 없습니다.")
# all_keys 기준으로 merge 전후 age 누락 확인
merged_demo = pd.merge(all_keys[['ID']].drop_duplicates(), demographic_data[['ID','age']], how='left', on='ID')
print("🛠 all_keys와 demographic_data merge 후: total rows:", len(merged_demo))
print("🛠 all_keys merge 후: age NaN count:", merged_demo['age'].isna().sum())
print("🛠 all_keys merge 후: sample IDs with missing age:", merged_demo.loc[merged_demo['age'].isna(), 'ID'].unique()[:10])

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

# === Debug: merged_full age 상태 확인 ===
if 'age' in merged_full.columns:
    print("🛠 merged_full: total rows:", len(merged_full))
    print("🛠 merged_full: age NaN count:", merged_full['age'].isna().sum())
    print("🛠 merged_full: sample IDs with missing age:", merged_full.loc[merged_full['age'].isna(), 'ID'].unique()[:10])
    # 날짜별로 age 값이 일관되게 들어가는지 몇 개 예시 보기
    sample_ids = merged_full['ID'].unique()[:5]
    for sid in sample_ids:
        sub = merged_full[merged_full['ID']==sid]
        print(f"🛠 ID={sid}: unique age values:", sub['age'].dropna().unique()[:5], "NaN rows count:", sub['age'].isna().sum())
else:
    print("🛠 merged_full에 'age' 컬럼이 없습니다.")

# (9) panic 값이 잘 살아 있는지 확인
print("📌 panic value counts (before any drop/fill):")
print(merged_full['panic'].value_counts(dropna=False))



# panic 컬럼은 ffill 대상에서 제외
merged_full = merged_full.sort_values(['ID','date']).reset_index(drop=True)

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
merged_full = merged_full[~merged_full['ID'].isin(['SYM2-1-412', 'SYM2-1-425'])]
merged_full = merged_full.drop_duplicates(subset=['ID','date'])
print(len((merged_full['ID'].unique())))

output_path = "/Users/lee-junyeol/Documents/GitHub/Panic-Project-DHLAB/data/SYM_720.csv"
merged_full.to_csv(output_path, index=False)