import pandas as pd
import datetime
import config as cfg
from path_utils import get_file_path
from pathlib import Path
import os

RAW_dir = "./data"
df1_name = "panic_pre_data_filled.csv"
df2_name = "panic_demography_data.csv"

df1_path = get_file_path(RAW_dir, df1_name)
df2_path = get_file_path(RAW_dir, df2_name)

df1 = pd.read_csv(df1_path)
df1['date'] = pd.to_datetime(df1['date'], errors='coerce')
df2 = pd.read_csv(df2_path)

df = df1.merge(df2, on=['ID'], how='left')
df_full = df.copy()

if 'panic_label' not in df_full.columns:
    df_full['panic_label'] = df_full['panic'].eq(2).astype(int)   # panic == 2 → 1, else → 0

# 현재 행의 ID_date + 1과 동일한 값을 entry_id에서 찾고 그때의 panic_label 값이 1이면 현재 행의 next_day_panic에 1 아니면 0
df_full['target_entry_id'] = (
    df_full['ID'].astype(str) + '_' +
    (df_full['date'] + pd.Timedelta(days=1)).dt.strftime('%Y-%m-%d')
)
mapping = df_full.set_index('entry_id')['panic_label'].to_dict()

df_full['next_day_panic'] = df_full['target_entry_id'].map(mapping).eq(1).astype(int)
df_full = df_full.drop(columns=['entry_id', 'dataset', 'panic', 'target_entry_id'])

result_path = os.path.join(RAW_dir, "df_720.csv")
df_full.to_csv(result_path, index=False)