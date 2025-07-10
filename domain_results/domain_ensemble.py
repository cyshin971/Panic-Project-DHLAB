import shap
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
import argparse
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
from sklearn.cluster import KMeans
from sklearn.inspection import permutation_importance

from utils.domain_preproc_utils import load_config
from utils.domain_utils import compute_category_probs, soft_vote_ensemble, compute_category_shap_fast


def main():
    parser = argparse.ArgumentParser(description='Soft-voting ensemble')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Path to YAML config file')
    args = parser.parse_args()

    cfg = load_config(args.config)
    cols  = cfg.get("COLUMNS", {})
    basic   = cols.get("basic", [])
    demo    = cols.get("demo", [])
    daily   = cols.get("daily", [])
    mood    = cols.get("mood", [])
    lifelog = cols.get("lifelog", [])
    survey5 = cols.get("survey5", [])

    # define base+category feature lists
    base = basic + demo
    CATEGORY_COLS = {
        'daily':   base + daily,
        'mood':    base + mood,
        'lifelog': base + lifelog,
        'survey5': base + survey5,
    }

    # directory settings from config or defaults
    hr_filter  = cfg.get('HR_FILTER', '720')
    scenario   = cfg.get('SCENARIO', 'A+B')
    data_root  = Path(cfg.get('DATA_DIR', 'default data directory'))
    result_root= Path(cfg.get('RESULT_DIR','default result directory'))

    data_dir   = data_root / hr_filter
    save_dir = result_root / f"{hr_filter}_{scenario}"
    save_dir.mkdir(parents=True, exist_ok=True)
    model_dir  = result_root / f"{hr_filter}_{scenario}" / 'model'

    # load models for each category
    models = {
        cat: joblib.load(model_dir / f"best_base_{cat}.pkl")
        for cat in CATEGORY_COLS
    }

    # load test data
    df = pd.read_csv(data_dir / "full_panic.csv")
    y_true = df['next_day_panic'].astype(int)

    # perform soft-voting ensemble
    ensemble_threshold = cfg.get('ENSEMBLE_THRESHOLD', 0.5)
    proba, pred, detail_df = soft_vote_ensemble(
        df, models, CATEGORY_COLS, ensemble_threshold=ensemble_threshold
    )

    # # --- compute and print feature importances ---
    # print("\n>>> Computing per‐model and ensemble feature importances...\n")
    # X = df.drop(columns=['ID','date','panic','next_day_panic'])
    # y = y_true
    # ensemble_imp = compute_ensemble_importances(models, CATEGORY_COLS, X, y)

    # # ensemble top features
    # top10_ens = ensemble_imp.sort_values(ascending=False).head(10)
    # print(f"[Ensemble] Scenario {scenario} top 10 important features:")
    # print(top10_ens.to_string(), "\n")

    # # save ensemble importances
    # ens_imp_path = save_dir / "ensemble_model_importances.csv"
    # ensemble_imp.to_csv(ens_imp_path, index=True)
    # print(f"Saved ensemble feature importances to {ens_imp_path}\n")

    # fast SHAP compute
    print("Computing fast SHAP contributions…")
    shap_df = compute_category_shap_fast(df, models, CATEGORY_COLS,
                                         kmeans_K=150, nsamples=200)

    # per-model top features by SHAP (mean absolute)
    print("\n[Per-model SHAP top features]")
    # iterate categories again for individual SHAP
    for cat in models:
        cols = [c for c in CATEGORY_COLS[cat] if c in shap_df.columns]
        valid_idx = df[cols].notna().all(axis=1)
        tmp = shap_df.loc[valid_idx, cols].abs().mean().sort_values(ascending=False).head(5)
        print(f"{cat}:")
        print(tmp.to_string(), "\n")

    # ensemble SHAP top 10
    mean_abs = shap_df.abs().mean(axis=0).sort_values(ascending=False)
    top10 = mean_abs.head(10)
    print("[Ensemble SHAP top 10 features]")
    print(top10.to_string(), "\n")

    # save shap contributions
    shap_path = save_dir / "ensemble_shap_fast.csv"
    shap_df.to_csv(shap_path, index=True)
    print(f"Saved fast SHAP values to {shap_path}\n")

    used_df = detail_df.notna().astype(int)
    used_df.columns = [f"used_{c}" for c in used_df.columns]

    # print evaluation metrics
    print("ensemble accuracy :", round(accuracy_score(y_true, pred),4))
    print("ensemble precision:", round(precision_score(y_true, pred),4))
    print("ensemble recall   :", round(recall_score(y_true, pred),4))
    print("ensemble f1       :", round(f1_score(y_true, pred),4))
    print("ensemble AUC      :", round(roc_auc_score(y_true, proba),4))

    # save results
    out = df[['ID','date','next_day_panic']].copy()
    out['ensemble_pred']  = pred
    out['ensemble_proba'] = proba
    out = pd.concat([out, used_df], axis=1)

    save_path = save_dir / "ensemble_results.csv"
    out.to_csv(save_path, index=False)
    print(f"Saved ensemble results to {save_path}")

if __name__ == "__main__":
    main()