import pandas as pd
from sklearn.model_selection import train_test_split
import config as cfg
import pandas as pd
from path_utils import get_file_path
from pathlib import Path
import os

RAW_dir = "./data"
full_dataset_name = "df_720_full.csv"
df_path = get_file_path(RAW_dir, full_dataset_name)

# 1. 데이터 로드
df = pd.read_csv(df_path)

# 2. 분리할 열: next_day_panic은 정답(y), 나머지는 X
y = df['next_day_panic'].values

# 3. Stratified Split (test 20%)
_, df_test = train_test_split(
    df, test_size=0.2, stratify=y, random_state=42
)

# 4. 저장
result_path = os.path.join(RAW_dir, "test_set.csv")
df_test.to_csv(result_path, index=False)