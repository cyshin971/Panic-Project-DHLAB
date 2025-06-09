import pandas as pd

step = pd.read_csv('/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/step_date.csv', index_col=0)
step['date'] = pd.to_datetime(step['date'])
id_list = step['ID'].unique()

step_delta = pd.DataFrame(columns=['ID', 'date', 'steps', 'step_max', 'step_mean', 'step_hvar_mean', 'step_delta', 'step_max_delta',
                                   'step_mean_delta', 'step_hvar_mean_delta', 'step_delta2', 'step_max_delta2',
                                   'step_mean_delta2', 'step_hvar_mean_delta2'])
for id in id_list:
    step_id = step.loc[(step.ID == id)]
    time_per_day = pd.date_range(step_id.date.min(), step_id.date.max(), freq='D')
    temp = pd.DataFrame()
    temp['date'] = time_per_day
    step_id = pd.merge(step_id, temp, how='right', on='date')
    step_id.ID = id
    step_id['step_delta'] = step_id['steps'].diff()
    step_id['step_delta2'] = step_id['steps'].diff(periods=2)
    step_id['step_max_delta'] = step_id['step_max'].diff()
    step_id['step_max_delta2'] = step_id['step_max'].diff(periods=2)
    step_id['step_mean_delta'] = step_id['step_mean'].diff()
    step_id['step_mean_delta2'] = step_id['step_mean'].diff(periods=2)
    step_id['step_hvar_mean_delta'] = step_id['step_hvar_mean'].diff()
    step_id['step_hvar_mean_delta2'] = step_id['step_hvar_mean'].diff(periods=2)
    step_delta = pd.concat([step_delta, step_id], axis=0)



step_delta['date'] = step_delta['date'].dt.strftime('%Y-%m-%d')
step_delta.reset_index(drop=True, inplace=True)
# Drop rows where steps, step_delta, and step_delta2 are all zero
step_delta = step_delta[~((step_delta['steps'] == 0) & (step_delta['step_delta'] == 0) & (step_delta['step_delta2'] == 0))]

# %%
step_delta.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/step_delta.csv", index=False)