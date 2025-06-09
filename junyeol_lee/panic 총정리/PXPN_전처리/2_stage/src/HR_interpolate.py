import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from tqdm import tqdm

HR = pd.read_csv('/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR.csv')
HR = HR.rename(columns={'heart_rate' : 'HR'})
HR['HR'] = pd.to_numeric(HR['HR'])

HR['datetime'] = pd.to_datetime(HR['date'] + ' ' + HR['time'])
HR = HR.sort_values(['ID','datetime']).set_index('datetime')

time_idx = pd.date_range('00:00', '23:59', freq='1T').time
minutes = [t.strftime('%H:%M:%S') for t in time_idx]

id_list = HR['ID'].unique()
    
HR_interpolated = pd.DataFrame(columns=['index', 'ID', 'date', 'time', 'HR'])
for id in tqdm(id_list):
    temp_id = HR.loc[(HR['ID'] == id)].copy()
    temp_id.reset_index(inplace=True)
    temp_id.drop('index', axis=1, inplace=True)
    date_list =temp_id['date'].unique()
    for date in date_list:
        temp_date = temp_id.loc[(temp_id['date'] == date)].copy()
        temp_date.reset_index(inplace=True)
        temp_date.drop('index', axis=1, inplace=True)
        temp_date.reset_index(inplace=True)  
        temp_date = temp_date.replace(0, np.NaN)
        if temp_date.HR.count() > 720:
            temp_date = temp_date.interpolate(method='values', limit_direction = 'both')
            HR_interpolated = pd.concat([HR_interpolated, temp_date], axis=0)
            file_name =  id + ' ' + date
            # plot_df(temp_date['index'], temp_date['HR'], file_name)
        else:
            pass
        
HR_interpolated.reset_index(drop=True, inplace=True)
HR_interpolated.to_csv("/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR_interpolated.csv")
