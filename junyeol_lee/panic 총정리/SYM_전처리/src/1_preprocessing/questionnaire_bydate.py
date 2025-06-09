import pandas as pd
import numpy as np
from utils_for_preprocessing import load_raw_file, extract_questionnaire_from_raw, extract_emotion_diary_from_raw
from functools import reduce


# 1. 엑셀 파일 경로 리스트
paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]


#data loading from raw data
ACQ = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='9광장공포인지', df_name = 'ACQ', questionnaire_column = '1.광장공포_인지_척도_1번_그룹_점수_합산')
APPQ_1 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='11공황-공포', df_name = 'APPQ_1', questionnaire_column = '1.알바니_공포_공황_척도_요인1._광장공포_점수_합계')
APPQ_2 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='11공황-공포', df_name = 'APPQ_2', questionnaire_column = '2.알바니_공포_공황_척도_요인2._사회공포_점수_합계')
APPQ_3 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='11공황-공포', df_name = 'APPQ_3', questionnaire_column = '3.알바니_공포_공황_척도_요인3._내부감각두려움_점수_합계')
BSQ = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='10신체감각', df_name = 'BSQ', questionnaire_column = '1.신체감각_척도_1번_그룹_점수_합산')

GAD_7 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='8범불안 장애', df_name = 'GAD_7', questionnaire_column = '1.범불안_장애_척도_1번_그룹_점수_합산')

PHQ_9 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='1우울증 선별', df_name = 'PHQ_9', questionnaire_column = '1.우울증_척도_1번_그룹_점수_합산')

BRIAN = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='22생물학적 리듬', df_name = 'BRIAN', questionnaire_column = '1.생물학적_리듬_평가_척도_1번_히든_그룹_합산')
CSM = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='20아침형-저녁형', df_name = 'CSM', questionnaire_column = '1.조합_척도_1~13번 문항 점수 합산')
CTQ_1 = extract_questionnaire_from_raw(ppath = 'paths', questionnaire_sheet='27유년기 외상', df_name = 'CTQ_1', questionnaire_column = 'Childhood_Trauma_Scale_Factor_1._Summing_the_Emotional_Neglect_Scores')
CTQ_2 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='27유년기 외상', df_name = 'CTQ_2', questionnaire_column = '2.Childhood_Trauma_Scale_Factor_2._Total_Physical_Abuse_Scores')
CTQ_3 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='27유년기 외상', df_name = 'CTQ_3', questionnaire_column = '3.Childhood_Trauma_Scale_Factor_3._Sexual_Abuse_Total_Score')
CTQ_4 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='27유년기 외상', df_name = 'CTQ_4', questionnaire_column = '4.Childhood_Trauma_Scale_Factor_4._Emotional_Abuse_Scores_Summed')
CTQ_5 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='27유년기 외상', df_name = 'CTQ_5', questionnaire_column = '5.Childhood_Trauma_Scale_Factor_5._Physical_Neglect_Scores_Summed')

KRQ = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='13회복탄력성', df_name = 'KRQ', questionnaire_column = '1.Summing_Resilience_Scale_1_Group_Scores')
MDQ = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='2기분장애', df_name = 'MDQ', questionnaire_column = '1.Mood_Disorders_Scale_1_group_scores_combined\t')

STAI_X2 = extract_questionnaire_from_raw(path = 'paths', questionnaire_sheet='5특성 불안', df_name = 'STAI_X2', questionnaire_column = '1.Sum_Anxiety_Scale_Group_1_scores')

#data merge
data_list = [ACQ, APPQ_1, APPQ_2, APPQ_3, BSQ, GAD_7, PHQ_9, BRIAN, CSM, CTQ_1, CTQ_2, CTQ_3, CTQ_4, CTQ_5, KRQ, MDQ, STAI_X2]
for df in data_list:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Convert to datetime
questionnaire_bydate = reduce(lambda x, y : pd.merge(x, y,on=['ID', 'date'], how='outer'), data_list)

#convert type from object to float
col_list = ['ACQ', 'APPQ_1', 'APPQ_2', 'APPQ_3', 'BSQ', 'BFNE', 'CES_D', 'GAD_7', 'KOSSSF', 'PHQ_9', 'SADS', 'STAI_X1']
for i in col_list:  
    questionnaire_bydate[i] = pd.to_numeric(questionnaire_bydate[i])

#data save to feather
questionnaire_bydate.to_feather("data/processed/questionnaire_bydate.feather")