import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score
)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


import config as cfg
import pandas as pd
from path_utils import get_file_path
from pathlib import Path

df_base_dir = "./data"
model_base_dir = "./model"
model_name = "gb_model.pkl"
df_name = "test_set.csv"

df_dir = get_file_path(df_base_dir, df_name)
model_dir = get_file_path(model_base_dir, model_name)

df = pd.read_csv(df_dir)
X_test = df.drop(columns=['next_day_panic', 'Unnamed: 0', 'panic_label', 'ID', 'date', 'severity'], errors='ignore')
y_test = df['next_day_panic'].values

# 2. 모델 로드
model = joblib.load(model_dir)


# 4. Hold-out 테스트셋 전체 성능 평가
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUROC:     {roc_auc_score(y_test, y_prob):.4f}")
print(f"AUPRC:     {average_precision_score(y_test, y_prob):.4f}")