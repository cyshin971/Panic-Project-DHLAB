import numpy as np

def growing_average_impute(df, group_col, target_cols,
                           default_fill_zero=True,
                           prefill_value=None):
    """
    Impute NaN values in target columns by growing average within each group.
    Parameters:
        df (pd.DataFrame): DataFrame to impute.
        group_col (str): Grouping column (e.g., patient ID).
        target_cols (list): Columns to impute.
        default_fill_zero (bool): If True, use 0.0 as prefill before first value; else use group mean or prefill_value.
        prefill_value (float, optional): Custom value to use as prefill (takes precedence over group mean if provided).
    Returns:
        pd.DataFrame: Imputed DataFrame.
    """
    df = df.copy()
    df.sort_values(by=[group_col, 'date'], inplace=True)

    # Precompute group means and global means if needed
    if not default_fill_zero:
        group_means = df.groupby(group_col)[target_cols].mean()
    global_means = df[target_cols].mean()

    for col in target_cols:
        for pid, sub in df.groupby(group_col):
            vals = sub[col].values
            mask = ~np.isnan(vals)

            running_sum = 0.0
            running_count = 0

            # Determine fill value for "pre-first" NaNs
            if default_fill_zero:
                fill_val = 0.0
            elif prefill_value is not None:
                fill_val = prefill_value
            else:
                group_mean = group_means.loc[pid, col] if pid in group_means.index else np.nan
                # If group mean is nan or missing, fallback to global mean, else 0.0
                if not np.isnan(group_mean):
                    fill_val = group_mean
                elif not np.isnan(global_means[col]):
                    fill_val = global_means[col]
                else:
                    fill_val = 0.0

            # Growing average imputation
            for i in range(len(vals)):
                if mask[i]:
                    running_sum += vals[i]
                    running_count += 1
                else:
                    if running_count == 0:
                        vals[i] = fill_val
                    else:
                        vals[i] = running_sum / running_count

            # Write back to DataFrame
            df.loc[sub.index, col] = vals

        # After group loop, fill any remaining NaNs with global mean (if not default_fill_zero)
        if not default_fill_zero:
            df[col].fillna(global_means[col], inplace=True)

    return df