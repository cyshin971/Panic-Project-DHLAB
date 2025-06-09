import pandas as pd
SYM = pd.read_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/result/result.csv", index_col=False)
PXPN = pd.read_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/result/result.csv", index_col=False)
result = pd.concat([SYM, PXPN], ignore_index=True)
# Combine duplicated age columns into a single 'age'
if 'age_x' in result.columns and 'age_y' in result.columns:
    # If both exist, prefer non-null values from age_x then age_y
    result['age'] = result['age_x'].fillna(result['age_y'])
# Drop the now redundant columns
drop_cols = [c for c in ['age_x', 'age_y', 'Unnamed: 0'] if c in result.columns]
result = result.drop(columns=drop_cols)
result.to_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_PXPN_merge/final_result.csv")