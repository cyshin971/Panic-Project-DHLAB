import pandas as pd
from utils_for_analysis import mesor, amplitude, acrophase

HR_interpolated = pd.read_csv('/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/HR_interpolated.csv')
HR_interpolated['HR'] = pd.to_numeric(HR_interpolated['HR'])

id_list = HR_interpolated['ID'].unique()
circadian_data = pd.DataFrame(columns=['ID','date','acr','amp','mesor'])
                  
for id in id_list:
    temp_id = HR_interpolated.loc[(HR_interpolated['ID'] == id)]
    temp_id.reset_index(inplace=True)
    temp_id = temp_id.drop('index', axis=1)
    date_list =temp_id['date'].unique()
    for date in date_list:
        temp_date = temp_id.loc[(temp_id['date'] == date)]
        temp_date.reset_index(inplace=True)
        temp_date = temp_date.drop('index', axis=1)
        temp_date.reset_index(inplace=True)  
        if temp_date.HR.count() > 360:
            acr = acrophase(temp_date['index'], temp_date['HR'])
            amp = amplitude(temp_date['index'], temp_date['HR'])
            mes = mesor(temp_date['index'], temp_date['HR'])
            new_row = pd.DataFrame([[id, date, acr, amp, mes]], columns=['ID','date','acr','amp','mesor'])
            circadian_data = pd.concat([circadian_data, new_row], ignore_index=True)
            print(id, date, acr, amp, mes)
        else:
            pass


circadian_data.to_csv("/Users/lee-junyeol/Downloads/preprocessing_code/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/circadian_parameter.csv")