import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import config as cfg
import pandas as pd
from path_utils import get_file_path
from pathlib import Path
import joblib
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    precision_recall_fscore_support,
)


df_base_dir = "./data"
model_base_dir = "./model"
model_name = "gb_model.pkl"
df_name = "df_720.csv"

df_dir = get_file_path(df_base_dir, df_name)
model_dir = get_file_path(model_base_dir, model_name)


# 1. 데이터 로드 및 전처리
df = pd.read_csv(df_dir)
feature_names = df.drop(['panic_label','ID','date','severity','next_day_panic'], axis=1).columns
df = df.drop(['panic_label', 'ID', 'date', 'severity'], axis=1)

X = df.drop(columns=['next_day_panic'])
y = df['next_day_panic'].values

# 2. Hold-out split for final testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 2. 파이프라인 정의
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('scaler', StandardScaler()),
    ('clf', GradientBoostingClassifier(
        ccp_alpha=0.0,
        criterion='friedman_mse',
        learning_rate=0.05,
        loss='log_loss',
        max_depth=11,
        max_features='sqrt',
        min_impurity_decrease=0.02,
        n_estimators=240,
        random_state=42,
        subsample=0.55,
        tol=0.0001,
        validation_fraction=0.1,
        verbose=0
    ))
])


# 6. 재학습 및 최종 테스트 세트 평가
pipeline.fit(X_train, y_train)
y_test_pred = pipeline.predict(X_test)
y_test_prob = pipeline.predict_proba(X_test)[:, 1]

print("\nHold-out Test Set Performance:")
print(f"Accuracy: {accuracy_score(y_test, y_test_pred):.4f}")
print(f"ROC AUC: {roc_auc_score(y_test, y_test_prob):.4f}")

# Additional performance metrics
precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='binary')
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# Save the trained model and scaler
import joblib

# Save the entire pipeline as one model
joblib.dump(pipeline, model_dir)
