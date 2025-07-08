import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from tqdm import tqdm
from sklearn.model_selection import train_test_split

HR = pd.read_csv('/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/HR.csv')
HR['HR'] = pd.to_numeric(HR['HR'])
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
HR_interpolated.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/HR_interpolated_720.csv")
