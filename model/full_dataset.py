import pandas as pd
import datetime
df1 = pd.read_csv("/panic_pre_data_filled.csv")
df1['date'] = pd.to_datetime(df1['date'], errors='coerce')
df2 = pd.read_csv("/panic_demography_data.csv")
df = df1.merge(df2, on=['ID'], how='left')
def add_next_day_panic(df):
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
    print(df_full[['entry_id','target_entry_id','panic_label','next_day_panic']])
    df_full = df_full.drop(columns=['entry_id', 'dataset', 'panic', 'target_entry_id'])
    df_full = df_full.drop(['panic_label', 'ID', 'date', 'severity'], axis=1)
    df_full.to_csv("/Panic-Project-DHLAB/model/df_720.csv", index=False)
    return df_full
add_next_day_panic(df)