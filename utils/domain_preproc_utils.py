import argparse
import yaml
import pandas as pd
from pathlib import Path

from utils.preproc_utils import add_next_day_panic
from utils.imputation_utils import group_impute


def load_config(config_path: Path) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def merge_data(panic_path: Path, demo_path: Path):
    df_panic = pd.read_csv(panic_path)
    df_demo = pd.read_csv(demo_path)
    # merge dataframes
    df = df_panic.merge(df_demo, on='ID', how='left', validate='many_to_one')
    return df
    
def reorder(df):
    front_cols = ['entry_id', 'dataset', 'ID', 'date', 'panic', 'next_day_panic']
    # 1) front_cols 중 실제 df에 있는 것만 취하고
    front = [c for c in front_cols if c in df.columns]
    # 2) 나머지 컬럼은 원래 순서대로
    rest  = [c for c in df.columns if c not in front]
    return df[front + rest]

def filter_missing_rows(df, cols_to_check):
    # 각 컬럼에 하나라도 NaN이 없는(모두 값이 있는) 행만 필터링
    mask_all_notna = df[cols_to_check].notna().all(axis=1)
    df_complete = df.loc[mask_all_notna, cols_to_check].copy()

    print(f"전체 행 수: {len(df)}")
    print(f"해당 컬럼들 모두 결측 없는 행 수: {len(df_complete)}")
    print(f"n = {len(df_complete.ID.unique())}")
    return df_complete

def data_preprocessing(group_col, date_col, 
                    daily_cols, survey_cols,
                    panic_path, demo_path):
    # Merge datas
    df = merge_data(panic_path, demo_path)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    # Add columns
    df_cp = df.copy()
    df_full = add_next_day_panic(df_cp) 
    # Reorder columns
    df_full = reorder(df_full)
    # Fill missing values
    df_full = group_impute(
        df, group_col, date_col, 
        zero_fill_cols=daily_cols, 
        ffill_bfill_cols=survey_cols
    )
    return df_full