import pandas as pd
import numpy as np
from utils_for_preprocessing import (
    load_raw_file,
    serialize_lifelog_heartrate,
    filter_by_valid_ids
)


paths = [
    '/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM2.xlsx',
]
sheet_name = "라이프로그-심박수"

# For each path, produce the long-format heart-rate DataFrame
hr_dfs = [serialize_lifelog_heartrate(p) for p in paths]
HR_melted = pd.concat(hr_dfs, ignore_index=True)
HR_melted.rename(columns={"heart_rate": "HR"}, inplace=True)
HR_melted["HR"] = HR_melted["HR"].fillna(0)
HR_melted["date"] = HR_melted["date"].astype(str).str[:10]
HR_melted = filter_by_valid_ids(HR_melted, id_column='ID')
output_path = "/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/HR.csv"
HR_melted.to_csv(output_path)

print(HR_melted.head(10))