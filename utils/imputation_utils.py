import numpy as np
import pandas as pd

def growing_average_impute(df, group_col, date_col, target_cols,
                           default_fill_zero=True, prefill_value=None):
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
    df.sort_values(by=[group_col, date_col], inplace=True)

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


def group_impute(df, group_col, date_col, 
                 zero_fill_cols=None, 
                 ffill_bfill_cols=None, 
                 growing_avg_cols=None,
                 default_fill_zero=True,
                 prefill_value=None):
    """
    Perform multiple imputation strategies by group in a single function for making domain models:
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    group_col : str
        Column name to group by (e.g., patient ID or user ID).
    date_col : str
        Column name containing datetime information for sorting (e.g., 'date').
    zero_fill_cols : list[str] or None
        Columns to fill missing values with 0.
    ffill_bfill_cols : list[str] or None
        Columns to impute by forward-fill then backward-fill within each group.
    growing_avg_cols : list[str] or None
        Columns to impute using a growing (cumulative) average within each group.
    default_fill_zero : bool, default True
        If True, use 0.0 to fill leading NaNs in growing average imputation.
        If False, use group mean or global mean (or `prefill_value` if provided).
    prefill_value : float or None
        Custom value to use for leading NaNs in growing average imputation,
        which takes precedence over group/global means.
    """
    df = df.copy()
    # Parse dates and sort by group and date
    df[date_col] = pd.to_datetime(df[date_col])
    df.sort_values([group_col, date_col], inplace=True)

    # 1) Zero-fill specified columns
    if zero_fill_cols:
        df[zero_fill_cols] = df[zero_fill_cols].fillna(0)

    # 2) Forward-fill then backward-fill within each group
    if ffill_bfill_cols:
        def _grp_fill(series):
            # If there's at least one non-null value in the group,
            # apply forward-fill then backward-fill;
            # otherwise leave all values as NaN.
            if series.notna().any():
                return series.ffill().bfill()
            return series

        for col in ffill_bfill_cols:
            df[col] = df.groupby(group_col)[col].transform(_grp_fill)

    # 3) Growing average imputation within each group
    if growing_avg_cols:
        df = growing_average_impute(
            df,
            group_col=group_col,
            date_col=date_col,
            target_cols=growing_avg_cols,
            default_fill_zero=default_fill_zero,
            prefill_value=prefill_value
        )

    return df