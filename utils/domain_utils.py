# ================= PyCaret ==================
import glob
import shutil
from pathlib import Path

import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, recall_score, precision_score,
    f1_score, roc_auc_score, precision_recall_curve
)

from imblearn.over_sampling import (
    SMOTE, ADASYN, BorderlineSMOTE, KMeansSMOTE
)
from imblearn.under_sampling import (
    RandomUnderSampler, NearMiss, ClusterCentroids
)
from imblearn.combine import SMOTEENN, SMOTETomek

from pycaret.classification import (
    setup, compare_models, tune_model, calibrate_model,
    finalize_model, save_model, predict_model, plot_model
)


# ============================ PyCaret ============================
def _make_sampler(name, n_neg, n_pos, strategy, k_neighbors, seed):
    """
    Create and return a sampler object based on the specified strategy.
    """
    name = name.lower()
    if name == 'smote':
        desired = int(n_neg * strategy)
        return SMOTE(
            sampling_strategy={1: max(n_pos, desired)},
            k_neighbors=k_neighbors,
            random_state=seed
        )
    if name == 'adasyn':
        desired = int(n_neg * strategy)
        return ADASYN(
            sampling_strategy={1: max(n_pos, desired)},
            n_neighbors=k_neighbors,
            random_state=seed
        )
    if name == 'smoteenn':
        return SMOTEENN(sampling_strategy=strategy, random_state=seed)
    if name == 'smotetomek':
        return SMOTETomek(sampling_strategy=strategy, random_state=seed)
    if name == 'borderline':
        desired = int(n_neg * strategy)
        return BorderlineSMOTE(
            kind_sel='borderline-1',
            sampling_strategy={1: max(n_pos, desired)},
            random_state=seed,
            k_neighbors=k_neighbors
        )
    if name == 'kmeans':
        desired = int(n_neg * strategy)
        return KMeansSMOTE(
            sampling_strategy={1: max(n_pos, desired)},
            random_state=seed
        )
    if name == 'under':
        return RandomUnderSampler(
            sampling_strategy={0: int(n_pos * strategy)},
            random_state=seed
        )
    if name == 'nearmiss':
        return NearMiss(version=1, sampling_strategy=strategy)
    if name == 'clustercentroids':
        return ClusterCentroids(
            sampling_strategy={0: int(n_pos * strategy)},
            random_state=seed
        )
    return None


def _evaluate_test(is_train, y_true, y_pred, y_prob):
    """
    Compute evaluation metrics for either training or testing data.
    """
    prefix = 'train' if is_train else 'test'
    return {
        f'{prefix}_accuracy':  round(accuracy_score(y_true, y_pred), 4),
        f'{prefix}_recall':    round(recall_score(y_true, y_pred), 4),
        f'{prefix}_precision': round(precision_score(y_true, y_pred), 4),
        f'{prefix}_f1':        round(f1_score(y_true, y_pred), 4),
        f'{prefix}_auc':       round(roc_auc_score(y_true, y_prob), 4),
    }


def _compute_shap_top5(model, X_train, bg_size, figure_dir, name, seed):
    """
    Compute SHAP values, save a global summary plot, and return the top 5 features.
    """
    # Sample background data for SHAP explainer
    bg = X_train.sample(min(len(X_train), bg_size), random_state=seed)
    explainer = shap.Explainer(model.predict_proba, bg)
    shap_exp = explainer(X_train)

    # Determine top-5 features by mean absolute SHAP value
    vals = np.abs(shap_exp.values).mean(axis=(0, 2))
    top5_idx = np.argsort(vals)[-5:][::-1]
    top5 = [shap_exp.feature_names[i] for i in top5_idx]

    # Create and save global SHAP bar plot
    sv_mean = shap_exp.values.mean(axis=2)
    plt.figure(figsize=(6, len(shap_exp.feature_names) * 0.2 + 1))
    shap.summary_plot(
        sv_mean,
        features=shap_exp.data,
        feature_names=shap_exp.feature_names,
        plot_type="bar",
        max_display=10,
        show=False
    )
    plt.savefig(
        figure_dir / f"{name}_global_shap.png",
        bbox_inches='tight',
        dpi=150
    )
    plt.close()

    # Save SHAP values for later inspection
    np.savez_compressed(
        figure_dir / f"{name}_shap_values.npz",
        values=shap_exp.values,
        feature_names=shap_exp.feature_names
    )
    return top5


def run_pycaret_experiment(
    df: pd.DataFrame,
    name: str,
    model_dir: Path,
    figure_dir: Path,
    prob_models: list[str],
    seed: int = 42,
    bg_size: int = 1000,
    use_sampler: bool = False,
    sampler_type: str = None,
    sampling_strategy: float = 0.5,
    k_neighbors: int = 5
):
    """
    Run a full PyCaret classification experiment:
      1) Split data into train and test
      2) Handle class imbalance (optional sampling)
      3) Setup PyCaret, compare, tune, calibrate, finalize, and save the best model
      4) Evaluate on train and test, save predictions
      5) Generate and save AUC and Precision-Recall threshold plots
      6) Perform SHAP analysis and save top-5 feature list
    """
    print(f"\n===== Experiment: {name} =====")
    print("Overall class distribution:", df['next_day_panic'].value_counts().to_dict())

    # 1) Split into training+validation and test sets
    train_val, test = train_test_split(
        df,
        test_size=0.2,
        stratify=df['next_day_panic'],
        random_state=seed
    )

    # Drop non-feature columns
    for subset in (train_val, test):
        subset.drop(columns=['ID', 'date', 'panic'], errors='ignore', inplace=True)

    # 2) Optional sampling to address class imbalance
    sampled_counts = train_val['next_day_panic'].value_counts().to_dict()
    if sampler_type:
        counts = sampled_counts
        sampler = _make_sampler(
            sampler_type,
            counts.get(0, 0),
            counts.get(1, 0),
            sampling_strategy,
            k_neighbors,
            seed
        )
        X, y = train_val.drop(columns=['next_day_panic']), train_val['next_day_panic']
        X_res, y_res = sampler.fit_resample(X, y)
        train_val = pd.concat([X_res, y_res.rename('next_day_panic')], axis=1)
        sampled_counts = train_val['next_day_panic'].value_counts().to_dict()
        # sampler = None  # Defer to PyCaret's imbalance handling

    print("> After sampling counts:", sampled_counts)

    # 3) Initialize PyCaret experiment
    exp = setup(
        data=train_val,
        target='next_day_panic',
        session_id=seed,
        normalize=True,
        imputation_type='simple',
        fold=5,
        fold_strategy='stratifiedkfold',
        n_jobs=8,
        ignore_features=['ID', 'date'],
        fix_imbalance=use_sampler,
        fix_imbalance_method=sampler
    )
    best = compare_models(include=prob_models, n_select=1, sort='AUC', fold=5)
    tuned = tune_model(best, optimize='F1', n_iter=30, fold=5)
    calib = calibrate_model(tuned, method='sigmoid', fold=5)
    final = finalize_model(calib)
    save_model(final, model_dir / f"best_{name}")

    # 4) Evaluate on training data
    train_pred = predict_model(final, data=train_val)
    y_true_train = train_val['next_day_panic'].astype(int)
    y_pred_train = train_pred['prediction_label'].astype(int)
    y_prob_train = final.predict_proba(
        train_val.drop(columns=['next_day_panic'])
    )[:, 1]
    train_metrics = _evaluate_test(True, y_true_train, y_pred_train, y_prob_train)
    print("> Train metrics:", train_metrics)

    # 5) Evaluate on test data
    test_pred = predict_model(final, data=test)
    y_true_test = test['next_day_panic'].astype(int)
    y_prob_test = final.predict_proba(
        test.drop(columns=['next_day_panic'])
    )[:, 1]

    # Determine best precision-recall threshold
    prec, rec, thresh = precision_recall_curve(y_true_test, y_prob_test)
    candidates = np.where((rec[1:] >= 0.8) & (prec[1:] >= 0.3))[0] + 1
    best_threshold = (
        round(
            thresh[candidates[np.argmax(
                2 * prec[candidates] * rec[candidates] /
                (prec[candidates] + rec[candidates] + 1e-8)
            )]],
            4
        ) if candidates.size else 0.5
    )
    print(f"> Best threshold: {best_threshold}")

    y_pred_test = (y_prob_test >= best_threshold).astype(int)
    test_metrics = _evaluate_test(False, y_true_test, y_pred_test, y_prob_test)
    print("> Test metrics:", test_metrics)

    # Save test predictions to CSV
    out = pd.DataFrame({
        'next_day_panic': y_true_test,
        'y_pred_default': test_pred['prediction_label'].astype(int),
        'y_pred_adj':     y_pred_test,
        'y_prob':         y_prob_test,
        'best_threshold': best_threshold
    })
    out.to_csv(figure_dir / f"{name}_test_predictions.csv", index=False)
    print(f"> Saved test predictions: {name}_test_predictions.csv")

    # 6) Save AUC plot
    plot_model(final, plot='auc', save=True)
    for f in glob.glob("*AUC.png"):
        shutil.move(f, figure_dir / f"{name}_AUC.png")

    # 7) Save Precision-Recall vs Threshold plot
    f1_scores = 2 * prec * rec / (prec + rec + 1e-8)
    plt.figure(figsize=(8, 6))
    plt.plot(thresh, prec[1:], label='Precision')
    plt.plot(thresh, rec[1:], label='Recall')
    plt.plot(thresh, f1_scores[1:], label='F1')
    plt.xlabel('Threshold')
    plt.ylabel('Score')
    plt.legend()
    plt.title(f'Precision/Recall/F1 vs Threshold ({name})')
    plt.tight_layout()
    plt.savefig(figure_dir / f"{name}_PR_threshold.png", bbox_inches='tight')
    plt.close()

    # 8) Perform SHAP analysis and save top-5 features
    X_train = train_val.drop(columns=['next_day_panic'])
    top5 = _compute_shap_top5(final, X_train, bg_size, figure_dir, name, seed)
    print(f"Top-5 SHAP features: {top5}")

    return {
        'dataset':      name,
        'best_model':   best._name,
        'best_class':   best.__class__.__name__,
        **train_metrics,
        **test_metrics,
        'top5_shap':    ";".join(top5),
        'ori_count_0':  df['next_day_panic'].value_counts().get(0, 0),
        'ori_count_1':  df['next_day_panic'].value_counts().get(1, 0),
        'train_count_0': train_val['next_day_panic'].value_counts().get(0, 0),
        'train_count_1': train_val['next_day_panic'].value_counts().get(1, 0),
        'sampled_count_0': sampled_counts.get(0, 0),
        'sampled_count_1': sampled_counts.get(1, 0),
    }

# ============================ Ensemble ============================
# 1) helper: compute per-category positive-class probabilities
def compute_category_probs(
    df: pd.DataFrame,
    models: dict,
    category_cols: dict
) -> pd.DataFrame:
    """
    Returns a DataFrame of shape (n_samples, n_models) where each column is
    the positive-class probability from that category's model, or NaN if
    required features are missing.
    """
    proba_df = pd.DataFrame(index=df.index, columns=models.keys(), dtype=float)
    for cat, model in models.items():
        cols = category_cols[cat]
        valid = df[cols].notna().all(axis=1)
        if valid.any():
            X_sub = df.loc[valid, cols]
            X_sub = X_sub.drop(columns=['ID','date','panic','next_day_panic'], errors='ignore')
            proba_df.loc[valid, cat] = model.predict_proba(X_sub)[:, 1]
    return proba_df

# 2) soft-voting ensemble function
def soft_vote_ensemble(
    df: pd.DataFrame,
    models: dict,
    category_cols: dict,
    ensemble_threshold: float = 0.5
):
    # get per-model probabilities
    proba_df = compute_category_probs(df, models, category_cols)
    # average non-NaN probabilities; fill rows with no valid models as 0.5
    ensemble_proba = proba_df.mean(axis=1, skipna=True).fillna(0.5)
    ensemble_pred  = (ensemble_proba >= ensemble_threshold).astype(int)
    return ensemble_proba, ensemble_pred, proba_df

# 3) fast SHAP for each category and ensemble
def compute_category_shap_fast(
    df: pd.DataFrame,
    models: dict,
    category_cols: dict,
    kmeans_K: int = 150,
    nsamples: int = 100
) -> pd.DataFrame:
    """
    각 모델별로 pred_contrib(트리) 또는 KernelExplainer(비트리)를 이용해
    SHAP 값을 빠르게 계산 → 전체 피처에 매핑 → 평균한 DataFrame 반환.
    """
    # drop meta columns
    meta = ['ID','date','panic','next_day_panic']
    all_feats = [c for c in df.columns if c not in meta]
    shap_sum = pd.DataFrame(0.0, index=df.index, columns=all_feats)
    model_count = 0

    for cat, model in models.items():
        cols = [c for c in category_cols[cat] if c in all_feats]
        valid = df[cols].notna().all(axis=1)
        if not valid.any():
            continue

        X_sub = df.loc[valid, cols]

        if hasattr(model, "feature_importances_"):
            # LightGBM/XGB: pred_contrib 사용
            booster = getattr(model, "booster_", model)
            contrib = booster.predict(X_sub, pred_contrib=True)
            # 마지막 열은 base_value; drop it
            shap_df = pd.DataFrame(
                contrib[:, :-1],
                index=X_sub.index,
                columns=cols
            )
        else:
            # non-tree: approximate with kmeans + nsamples
            def f(x_np):
                tmp = pd.DataFrame(x_np, columns=cols)
                return model.predict_proba(tmp)[:, 1]

            kmeans = KMeans(n_clusters=kmeans_K, random_state=0)
            kmeans.fit(X_sub.values)
            bg = kmeans.cluster_centers_

            expl = shap.KernelExplainer(f, bg, feature_names=cols)
            vals = expl.shap_values(X_sub.values, nsamples=nsamples)
            shap_df = pd.DataFrame(vals, index=X_sub.index, columns=cols)

        # reindex to full feature set, missing→0
        shap_df = shap_df.reindex(columns=all_feats, fill_value=0.0)
        shap_sum.loc[valid] += shap_df
        model_count += 1
    return (shap_sum / model_count) if model_count else shap_sum