import argparse
import yaml
import pandas as pd
from pathlib import Path

from utils.domain_preproc_utils import *
from utils.domain_utils import *

def main():
    parser = argparse.ArgumentParser(description="Preprocess panic and demographic data")
    parser.add_argument(
        '--config', '-c', type=Path, 
        default=Path(__file__).parent / 'config_preprocessing.yaml',
        help='path to YAML config file'
    )
    parser.add_argument(
        '--panic_file', '-p',
        type=Path,
        help='path to panic data CSV (overrides config)'
    )
    parser.add_argument(
        '--demo_file', '-d',
        type=Path,
        help='path to demographic data CSV (overrides config)'
    )
    parser.add_argument(
        '--scenario',
        type=str,
        help='dataset scenario (overrides config)'
    )
    args = parser.parse_args()

    # 1) Read configuration
    cfg = load_config(args.config)

    # 2) Override command-line arguments
    panic_filename = args.panic_file or Path(cfg['PANIC_FILE'])
    demo_filename  = args.demo_file  or Path(cfg['DEMO_FILE'])
    scenario       = args.scenario   or cfg['SCENARIO']

    # 3) Set up directories
    data_dir     = Path(cfg['DATA_DIR']) / str(cfg["HR_FILTER"])
    save_dir     = Path(cfg['SAVE_DIR']) / f"{cfg['HR_FILTER']}_{scenario}"
    save_data_dir= data_dir / f"{cfg['HR_FILTER']}_{scenario}"
    model_dir    = save_dir / "model"
    fig_dir      = save_dir / "figure"
    for d in (save_dir, save_data_dir, model_dir, fig_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Read column lists for each category
    cols    = cfg.get("COLUMNS", {})
    basic   = cols.get("basic", [])
    demo    = cols.get("demo", [])
    daily   = cols.get("daily", [])
    mood    = cols.get("mood", [])
    lifelog = cols.get("lifelog", [])
    survey5 = cols.get("survey5", [])

    # Combine base columns with category-specific ones
    base      = basic + demo
    b_daily   = base + daily
    b_mood    = base + mood
    b_lifelog = base + lifelog
    b_survey5 = base + survey5

    # 4) Data preprocessing
    df_full = data_preprocessing('ID', 'date', daily, survey5,
                                 data_dir / panic_filename,
                                 data_dir / demo_filename)

    # Split data by panic label
    df_non_panic = df_full[df_full['panic_label'] == 0]
    df_panic     = df_full[df_full['panic_label'] == 1]

    # Save full, non-panic, and panic datasets
    df_full.to_csv(data_dir / "full_panic.csv",     index=False)
    df_non_panic.to_csv(data_dir / "non_panic_days.csv", index=False)
    df_panic.to_csv(data_dir / "panic_days.csv",    index=False)

    # Filter rows with missing values by column category (using filter_missing_rows)
    if cfg["FULL_DATASET"]:
        df = df_full
    else:
        df = df_panic if cfg["PANIC"] else df_non_panic

    df_daily   = filter_missing_rows(df, b_daily)
    df_mood    = filter_missing_rows(df, b_mood)
    df_lifelog = filter_missing_rows(df, b_lifelog)
    df_survey5 = filter_missing_rows(df, b_survey5)

    # Save filtered datasets to CSV
    df_daily.to_csv(save_data_dir / "base_daily.csv",     index=False)
    df_mood.to_csv(save_data_dir / "base_mood.csv",       index=False)
    df_lifelog.to_csv(save_data_dir / "base_lifelog.csv", index=False)
    df_survey5.to_csv(save_data_dir / "base_survey5.csv", index=False)

    # 5) Run PyCaret experiments
    if cfg['PYCARET']:
        CSV_FILES    = cfg["csv_files"]
        PROB_MODELS  = cfg["prob_models"]
        SEED         = cfg["seed"]
        SHAP_BG_SIZE = cfg.get("shap_bg_size", 10000)

        summary = []
        for name, fname in CSV_FILES.items():
            df = load_and_clean(save_data_dir / fname)

            sampler_type = cfg["SAMPLER_TYPE"] if cfg["USE_SAMPLER"] else None

            res = run_pycaret_experiment(
                df=df,
                name=name,
                model_dir=model_dir,
                figure_dir=fig_dir,
                prob_models=PROB_MODELS,
                use_class_weight=cfg["USE_CLASS_WEIGHT"],
                weight_scheme=cfg["WEIGHT_SCHEME"],
                seed=SEED,
                bg_size=SHAP_BG_SIZE,
                sampler_type=sampler_type,
                sampling_strategy=cfg["SAMPLING_STRATEGY"],
                k_neighbors=cfg["K_NEIGHBORS"]
            )
            summary.append(res)

        pd.DataFrame(summary).to_csv(save_dir / "experiment_summary.csv", index=False)
        print("-> Experiment summary saved to experiment_summary.csv")
        print("\nAll experiments completed!")

if __name__ == "__main__":
    main()