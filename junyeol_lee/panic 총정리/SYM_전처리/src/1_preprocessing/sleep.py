import pandas as pd
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids

# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM2.xlsx',
]

# 2. “생활패턴-음주” 시트를 모두 불러와 합치기
sleep_raw = load_raw_file(paths, sheet_name="라이프로그-수면")

sleep_raw = filter_by_valid_ids(sleep_raw, id_column="비식별키")


# 4) 날짜 컬럼 datetime으로 변환하고 normalize
sleep_raw['날짜'] = pd.to_datetime(sleep_raw['날짜'], errors='coerce').dt.normalize()

# 5) 측정값 컬럼명 자동 탐색
measure_cols = [col for col in sleep_raw.columns if '측정값' in col]
if not measure_cols:
    raise KeyError("측정값 컬럼을 찾을 수 없습니다. 컬럼명을 확인하세요.")
# 여러 개 있으면 첫 번째를 사용
measure_col = measure_cols[0]

print("사용할 측정값 컬럼:", measure_col)

# 5.5) 동일한 ID, 날짜에 대해 측정값 이어붙이기
sleep_raw = sleep_raw.groupby(['비식별키', '날짜'], as_index=False).agg({
    measure_col: lambda x: ','.join(x.dropna().astype(str)),
    '취침시간': 'first',
    '기상시간': 'first'
})

# 6) SLT별 누적 시간을 계산하는 함수
def calc_slt_times(row):
    raw = row[measure_col]
    # 쉼표로 구분된 문자열 → 정수 리스트
    vals = [int(x) for x in str(raw).split(',') if x != '']
    # 개수 세기
    count_0 = vals.count(0)  # SLT2
    count_1 = vals.count(1)  # SLT1
    count_2 = vals.count(2)  # SLT6
    count_3 = vals.count(3)  # SLT4
    count_4 = vals.count(4)  # SLT5
    # SLT3은 해당값 없음
    count_5 = 0

    # 30초 단위 → 시간(시간 단위)
    slt1_h = count_1 * 30 / 3600
    slt2_h = count_0 * 30 / 3600
    slt3_h = 0
    slt4_h = count_3 * 30 / 3600
    slt5_h = count_4 * 30 / 3600
    slt6_h = count_2 * 30 / 3600

    return pd.Series({
        'SLT1': slt1_h,
        'SLT2': slt2_h,
        'SLT3': slt3_h,
        'SLT4': slt4_h,
        'SLT5': slt5_h,
        'SLT6': slt6_h
    })

# 7) calc_slt_times를 df_filtered에 적용
slt_times = sleep_raw.apply(calc_slt_times, axis=1)

# 8) 필요한 컬럼(ID, 날짜, 취침시간, 기상시간)과 SLT 결과 합치기
df_final = pd.concat([
    sleep_raw[['비식별키', '날짜', '취침시간', '기상시간']]
        .rename(columns={'비식별키': 'ID', '날짜': 'date'})
        .reset_index(drop=True),
    slt_times.reset_index(drop=True)
], axis=1)

# 9) 'ID'·'date' 순으로 정렬
df_final = df_final.sort_values(['ID', 'date']).reset_index(drop=True)

# Convert 취침시간 and 기상시간 to datetime and compute total_sleep
df_final['취침시간'] = pd.to_datetime(df_final['취침시간'], errors='coerce')
df_final['기상시간'] = pd.to_datetime(df_final['기상시간'], errors='coerce')
df_final['total_sleep'] = (df_final['기상시간'] - df_final['취침시간']).dt.total_seconds() / 3600
# Drop 취침시간 and 기상시간 columns
df_final.drop(columns=['취침시간', '기상시간'], inplace=True)

# 10) 결과 확인 (상위 10행 출력)
print(df_final.head(10))

# 11) 결과를 CSV로 저장 (필요 시 경로 수정)
output_path = '/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/sleep_summary.csv'
df_final.to_csv(output_path, index=False)