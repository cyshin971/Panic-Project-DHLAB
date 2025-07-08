import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score
)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# 1. 데이터 로드 및 분할
df = pd.read_csv('/home/junyeollee/.jupyter/panic/2025.06.26/imputed_720/result/df_720_full.csv')
df = df.drop(['Unnamed: 0', 'panic_label', 'ID', 'date', 'severity'], axis=1)

df_test = pd.read_csv('/home/junyeollee/.jupyter/panic/2025.06.26/imputed_720/result/test_set.csv')
X_test = df_test.drop(columns=['label'])
y_test = df_test['label'].values

# 2. 모델 로드
model = joblib.load('/home/junyeollee/.jupyter/panic/2025.06.26/imputed_720/result/gb_model.pkl')


# 4. Hold-out 테스트셋 전체 성능 평가
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUROC:     {roc_auc_score(y_test, y_prob):.4f}")
print(f"AUPRC:     {average_precision_score(y_test, y_prob):.4f}")