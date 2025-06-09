import pandas as pd
import numpy as np
from utils_for_preprocessing import load_raw_file, filter_by_valid_ids
from functools import reduce

paths = [
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM1.xlsx',
    '/Users/lee-junyeol/Downloads/Panic/SYM/New_preprocessing/excel/backup_SYM2.xlsx',
]



def extract_questionnaire_from_raw(path, questionnaire_sheet, df_name, questionnaire_column):
    df = load_raw_file(path, sheet_name=questionnaire_sheet)
    # Load 비식별키, 설문시작일, 설문완료일, and questionnaire_column
    df = df[['비식별키', '설문시작일', '설문완료일', questionnaire_column]]
    # Filter to keep only rows where 설문완료일 is not null
    df = df[pd.notnull(df['설문완료일'])].copy()
    # Use 설문시작일 as date
    df = df[['비식별키', '설문시작일', questionnaire_column, '설문완료일']]
    # Drop the 설문완료일 column
    df.drop(['설문완료일'], axis=1, inplace=True)
    # Rename columns to ["ID", "date", df_name]
    df.columns = ["ID", "date", df_name]
    df.drop_duplicates(['ID','date'], keep='last', inplace=True, ignore_index=False)
    return df


# ——— 1. 각 설문지별 시트 이름과 문항 컬럼 매핑 ———
questionnaire_specs = {
    'BRIAN':  ('22생물학적 리듬',    '1.생물학적_리듬_평가_척도_1번_히든_그룹_합산'),
    'CSM':    ('20아침형-저녁형', '1.조합_척도_1~13번_문항_점수_합산'),
    'CTQ_1':  ('27유년기 외상',       '1.유년기_외상_척도_요인1._정서방임_점수_합산'),
    'CTQ_2':  ('27유년기 외상',       '2.유년기_외상_척도_요인2._신체학대_점수_합산'),
    'CTQ_3':  ('27유년기 외상',       '3.유년기_외상_척도_요인3._성학대_점수_합산'),
    'CTQ_4':  ('27유년기 외상',       '4.유년기_외상_척도_요인4._정서학대_점수_합산'),
    'CTQ_5':  ('27유년기 외상',       '5.유년기_외상_척도_요인5._신체방임_점수_합산'),
    'KRQ':    ('13회복탄력성',              '1.회복탄력성_척도_1번_그룹_점수_합산'),
    'MDQ':    ('2기분 장애',          '1.기분_장애_척도_1번_그룹_점수_합산'),
    'SPAQ_1': ('21계절성 양상',             '1.계절성_양상_척도_2번_그룹_점수_합산'),
    'SPAQ_2': ('21계절성 양상',             '2.계절성_양상_척도_3번_문항_점수'),
    'STAI_X2':('5특성 불안',           '1.특성_불안_척도_1번_그룹_점수_합산'),
    'ACQ':    ('9광장공포인지', '1.광장공포_인지_척도_1번_그룹_점수_합산'),
    'APPQ_1': ('11공황-공포',         '1.알바니_공포_공황_척도_요인1._광장공포_점수_합계'),
    'APPQ_2': ('11공황-공포',         '2.알바니_공포_공황_척도_요인2._사회공포_점수_합계'),
    'APPQ_3': ('11공황-공포',         '3.알바니_공포_공황_척도_요인3._내부감각두려움_점수_합계'),
    'BSQ':    ('10신체감각','1.신체감각_척도_1번_그룹_점수_합산'),
    'BFNE':   ('6부정적평가에 대한 두려움','1.두려움_척도_1번_그룹_점수_합산'),
    'CES_D':  ('32우울증',         '1.우울_척도_개정판_1번_그룹_점수_합산'),
    'GAD_7':  ('8범불안 장애','1.범불안_장애_척도_1번_그룹_점수_합산'),
    'KOSSSF': ('12직무스트레스',         '1.직무스트레스_단축형_척도_1번_그룹_점수_합산'),
    'PHQ_9':  ('1우울증 선별','1.우울증_척도_1번_그룹_점수_합산'),
    'SADS':   ('7사회적회피 및 불편감','1.사회적_회피_및_불편감_척도_1번_그룹_점수_합산'),
    'STAI_X1':('4상태 불안',       '1.불안_척도_1번_그룹_점수_합산'),
}



# ——— 2. SYM1·SYM2 파일에서 같은 설문지만 모아오는 함수 ———
def extract_multi(paths, sheet_name, df_name, questionnaire_col):
    dfs = []
    for p in paths:
        df = extract_questionnaire_from_raw(
            path=p,
            questionnaire_sheet=sheet_name,
            df_name=df_name,
            questionnaire_column=questionnaire_col
        )
        dfs.append(df)
    # 동일 ID·date 중복 시 마지막 값을 남기고 제거
    return pd.concat(dfs, ignore_index=True) \
             .drop_duplicates(subset=['ID','date'], keep='last')

# ——— 3. 각 설문지 데이터 로드 ———
loaded = {}
for name, (sheet, col) in questionnaire_specs.items():
    loaded[name] = extract_multi(paths, sheet, name, col)

# ——— 4. 날짜 컬럼 datetime 변환 ———
for df in loaded.values():
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# ——— 5. 여러 설문지 병합 (outer join) ———
questionnaire_bydate = reduce(
    lambda left, right: pd.merge(left, right, on=['ID','date'], how='outer'),
    loaded.values()
)

# ——— 6. 수치형 변환 ———
for col in loaded.keys():
    questionnaire_bydate[col] = pd.to_numeric(questionnaire_bydate[col], errors='coerce')

# ——— 7. 결과 저장 (CSV) ———
output_path = "/Users/lee-junyeol/Downloads/Panic/SYM_전처리/data/processed/questionnaire.csv"
questionnaire_bydate = filter_by_valid_ids(questionnaire_bydate, id_column="ID")
questionnaire_bydate.to_csv(output_path, index=False)