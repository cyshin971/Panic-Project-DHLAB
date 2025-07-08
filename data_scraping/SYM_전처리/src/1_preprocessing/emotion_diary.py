import pandas as pd
import numpy as np
from utils_for_preprocessing import extract_emotion_diary_from_raw, filter_by_valid_ids
from functools import reduce

paths = [
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/excel_files/backup_SYM2.xlsx',
]

# For each metric, extract from both files and concatenate
positive_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='positive_feeling',
        questionnaire_column='긍정적기분'
    ) for p in paths
]
positive = pd.concat(positive_dfs, ignore_index=True)

negative_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='negative_feeling',
        questionnaire_column='부정적기분'
    ) for p in paths
]
negative = pd.concat(negative_dfs, ignore_index=True)

positive_E_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='positive_E',
        questionnaire_column='긍정적에너지'
    ) for p in paths
]
positive_E = pd.concat(positive_E_dfs, ignore_index=True)

negative_E_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='negative_E',
        questionnaire_column='부정적에너지'
    ) for p in paths
]
negative_E = pd.concat(negative_E_dfs, ignore_index=True)

anxiety_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='anxiety',
        questionnaire_column='불안'
    ) for p in paths
]
anxiety = pd.concat(anxiety_dfs, ignore_index=True)

annoying_dfs = [
    extract_emotion_diary_from_raw(
        p,
        questionnaire_sheet='정서일지',
        df_name='annoying',
        questionnaire_column='짜증'
    ) for p in paths
]
annoying = pd.concat(annoying_dfs, ignore_index=True)

#data preprocessing
data_list = [positive, negative, positive_E, negative_E, anxiety, annoying]
emotion_diary = reduce(lambda x, y : pd.merge(x, y, on=['ID', 'date'], how='outer'), data_list)
emotion_diary = filter_by_valid_ids(emotion_diary, id_column='ID')
#data save to feather
emotion_diary.to_csv("/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/SYM_전처리/data/processed/emotion_diary.csv")