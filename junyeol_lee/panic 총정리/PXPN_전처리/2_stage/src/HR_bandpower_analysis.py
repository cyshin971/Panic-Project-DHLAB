import pandas as pd
import numpy as np
from utils_for_preprocessing import (
    check_bandpower_value_a,
    check_bandpower_value_b,
    check_bandpower_value_c,
    check_bandpower_value_d,
)
from joblib import Parallel, delayed
from tqdm.auto import tqdm
from tqdm_joblib import tqdm_joblib

# 1) 파일 로드 & 타입 변환
HR = pd.read_csv(
    "/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR_interpolated.csv",
    parse_dates=["date"]
)
HR["HR"] = pd.to_numeric(HR["HR"], errors="coerce")

# ——— build per-minute DataFrame ———
df_per_min = pd.DataFrame(columns=['ID','HR','date'])
for id in HR['ID'].unique():
    df_id = HR[HR['ID'] == id]
    time_per_min = pd.date_range(df_id['date'].min(), df_id['date'].max(), freq='min')
    temp = pd.DataFrame({'date': time_per_min})
    df_id = pd.merge(df_id, temp, how='right', on='date')
    df_id['ID'] = id
    df_per_min = pd.concat([df_per_min, df_id], axis=0)

df_per_min["day"] = df_per_min["date"].dt.date

# 4) 하루 그룹 하나당 밴드파워 계산 함수
def compute_bandpower_for_group(group):
    (id_, day), sub = group
    if len(sub) < 360:
        return None
    idx = np.arange(len(sub))
    hr  = sub["HR"].to_numpy()
    return {
        "ID":           id_,
        "date":         pd.Timestamp(day),
        "bandpower_a":  check_bandpower_value_a(idx, hr),
        "bandpower_b":  check_bandpower_value_b(idx, hr),
        "bandpower_c":  check_bandpower_value_c(idx, hr),
        "bandpower_d":  check_bandpower_value_d(idx, hr),
    }

groups = df_per_min.groupby(["ID","day"], sort=False)

# 5) tqdm_joblib 로 진행률 표시하며 병렬 처리
with tqdm_joblib(tqdm(total=df_per_min["ID"].nunique(), desc="IDs")):
    results = Parallel(n_jobs=-1)(
        delayed(lambda g: compute_bandpower_for_group(g))(grp)
        for grp in groups
    )

# 6) None 삭제 & DataFrame 생성
records = [r for r in results if r is not None]
bandpower_df = pd.DataFrame(records)

# 7) 저장
bandpower_df.to_csv(
    "/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/bandpower.csv",
    index=False
)