import pandas as pd

#load data
step= pd.read_csv('/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/foot.csv')
step.rename(columns={'foot': 'step'}, inplace=True)

#data preprocessing
step['step'] = pd.to_numeric(step['step'])
step_nonzero = step[step.step != 0]

#statistical analysis
step_mean = step_nonzero.groupby(['ID','date'])['step'].mean().reset_index().rename(columns={'step':'step_mean'})
step_var = step_nonzero.groupby(['ID','date'])['step'].var().reset_index().rename(columns={'step':'step_var'})
step_max = step_nonzero.groupby(['ID','date'])['step'].max().reset_index().rename(columns={'step':'step_max'})

#calculation of step_hvar_mean
step_nonzero['hour'] = pd.to_datetime(step_nonzero['time']).dt.hour 
step_hvar = step_nonzero.groupby(['ID','date','hour'])['step'].var().reset_index()

step_hvar_mean = step_hvar.groupby(['ID','date'])['step'].mean().reset_index().rename(columns={'step':'step_hvar_mean'})

# create total daily steps
daily_steps = step.groupby(['ID','date'])['step'].sum().reset_index().rename(columns={'step':'steps'})

#data merge
step_statistics_merged= pd.merge(left=step, right=step_var, how="outer", on =['date','ID'])
step_statistics_merged= pd.merge(left=step_statistics_merged, right=step_max, how="outer", on =['date','ID'])
step_statistics_merged= pd.merge(left=step_statistics_merged, right=step_mean, how="outer", on =['date','ID'])
step_statistics_merged= pd.merge(left=step_statistics_merged, right=step_hvar_mean, how="outer", on =['date','ID'])

#data preprocessing
step_statistics_merged['datetime'] = step_statistics_merged['date'] + ' ' + step_statistics_merged['time']

#data save to feather
step_statistics_merged.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/step_stactistics.csv")

#data per date
step_date= pd.merge(left=daily_steps, right=step_var, how="left", on =['date','ID'])
step_date= pd.merge(left=step_date, right=step_max, how="left", on =['date','ID'])
step_date= pd.merge(left=step_date, right=step_mean, how="left", on =['date','ID'])
step_date= pd.merge(left=step_date, right=step_hvar_mean, how="left", on =['date','ID'])

#data save to feather
step_date.to_csv("/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/step_date.csv")