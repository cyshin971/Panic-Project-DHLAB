import pandas as pd
SYM = pd.read_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/result/result_diary_720_no_ffill.csv", index_col=False)
PXPN = pd.read_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/result/result_720_no_fill.csv", index_col=False)
result = pd.concat([SYM, PXPN], ignore_index=True)

drop_cols = [c for c in ['Unnamed: 0'] if c in result.columns]
result = result.drop(columns=drop_cols)
result = result.drop(columns=['medication_in_month','SPAQ_1', 'SPAQ_2', 'BFNE', 'CES_D', 'KOSSSF', 'SADS', 'STAI_X1', 'mood', 'contents'])

result.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_PXPN_merge/final_result_720_no_ffill.csv", index=False)