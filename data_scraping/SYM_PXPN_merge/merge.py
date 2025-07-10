import pandas as pd
import os
output_path = "/Users/lee-junyeol/Documents/GitHub/Panic-Project-DHLAB/data/merged_df.csv"
input_path_SYM = "/Users/lee-junyeol/Documents/GitHub/Panic-Project-DHLAB/data/SYM_720.csv"
input_path_PXPN = "/Users/lee-junyeol/Documents/GitHub/Panic-Project-DHLAB/data/PXPN_720.csv"
SYM = pd.read_csv(input_path_SYM, index_col=False)
PXPN = pd.read_csv(input_path_PXPN, index_col=False)
result = pd.concat([SYM, PXPN], ignore_index=True)

drop_cols = [c for c in ['Unnamed: 0'] if c in result.columns]
result = result.drop(columns=drop_cols)
result = result.drop(columns=['medication_in_month','SPAQ_1', 'SPAQ_2', 'BFNE', 'CES_D', 'KOSSSF', 'SADS', 'STAI_X1', 'mood', 'contents'])

result.to_csv(output_path, index=False)