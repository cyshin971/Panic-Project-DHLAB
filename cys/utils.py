import pandas as pd
import numpy as np

def calculate_days_before_panic(df, patient_id, delta_days=3, lookback_limit=7):
    patient_data = df[df['ID'] == patient_id]
    entry_dates_series = patient_data['date']
    if len(set(entry_dates_series)) != len(entry_dates_series):
        raise ValueError(f"Duplicate dates found for patient {patient_id}. Please check the data.")
    panic_dates_series = patient_data[patient_data['dbp'] == 0]['date']
    if len(set(panic_dates_series)) != len(panic_dates_series):
        raise ValueError(f"Duplicate panic dates found for patient {patient_id}. Please check the data.")
    
    entry_dates = set(entry_dates_series)
    panic_dates = set(panic_dates_series)

    for panic_date in sorted(panic_dates, reverse=True): # Sort from latest to earliest
        index = patient_data[patient_data['date'] == panic_date].index[0]
        event_id = patient_data.loc[index, 'entry_id']
        df.loc[index, 'dbp'] = 0
        df.loc[index, 'ref_event_id'] = None
        for j in range(1, delta_days + 1):
            prior_date = panic_date - pd.Timedelta(days=j)
            if prior_date in entry_dates:
                index = patient_data[patient_data['date'] == prior_date].index[0]
                df.loc[index, 'dbp'] = j
                df.loc[index, 'ref_event_id'] = event_id
    
    for entry_date in sorted(entry_dates, reverse=True):
        for j in range(1, lookback_limit + 1):
            if j == lookback_limit+1:
                df.loc[index, 'n_prior_data'] = j
                break
            prior_date = entry_date - pd.Timedelta(days=j)
            if prior_date not in entry_dates:
                break
            index = patient_data[patient_data['date'] == prior_date].index[0]
            if df.loc[index, 'panic_label'] == 1:
                break
            index = patient_data[patient_data['date'] == entry_date].index[0]
            df.loc[index, 'n_prior_data'] = j

def process_calculate_days_before_panic(df, delta_days=3, lookback_limit=7):
    patient_ids = df['ID'].unique()
    for patient_id in patient_ids:
        calculate_days_before_panic(df, patient_id, delta_days, lookback_limit)
        progress = (np.where(patient_ids == patient_id)[0][0] + 1) / len(patient_ids) * 100
        print(f"Processing: {progress:.2f}% complete", end='\r')
    # replace None values in 'n_prior_data' with 0
    df['n_prior_data'] = df['n_prior_data'].fillna(0).astype(int)
    return df