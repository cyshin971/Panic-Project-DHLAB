import pandas as pd
from sklearn.model_selection import train_test_split

# 1. 데이터 로드
df = pd.read_csv('/Panic-Project-DHLAB/model/df_720_full.csv')

# 2. 분리할 열: next_day_panic은 정답(y), 나머지는 X
y = df['next_day_panic'].values

# 3. Stratified Split (test 20%)
_, df_test = train_test_split(
    df, test_size=0.2, stratify=y, random_state=42
)

# 4. 저장
df_test.to_csv('/Panic-Project-DHLAB/model/test_set.csv', index=False)