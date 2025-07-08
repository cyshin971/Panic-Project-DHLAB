# Panic-Project-DHLAB

> Digital Healthcare Laboratory  
> Yonsei University College of Medicine  
> Department of Biomedical Systems Informatics

This project contains code to perform panic prediction from tabular data (socio-demographic, questionnaire, daily log, and life log data)

---
## Data Overview

Questionnaire data consists of:
- Clinical psychological survey data such as (PHQ, MDQ, STAI, CTQ, etc.)

Life Log data consists of:
- Step features
- Heart Rate features
- Sleep features
Captured from wearable devices

Daily Log data consists of self-reported:
- Mood features
- Daily life log features (smoking, menstruation, coffee, etc.)

---
## Code Overview

This repository contains code for
1. Data scraping
2. Data preprocessing
3. Data imputation
4. (optional) Data analysis

As well as code for the following 3 models
- Next day panic prediction model 1 (entire domain)
- Next day panic prediction model 2 (2 domain ensemble)  
- Panic severity prediction model

---
## Instructions

### Data Scraping
1. Download the `pixelpanic_raw_data.zip` on dropbox
2. move the `pixelpanic_raw_data.zip` to `/data_scraping/PXPN_전처리/1_stage/초기_파일_폴더/PXPN/PXPN_dropbox` directory
3. Run All `PXPN_questionare_preprocessing_for_all_patients_no_ffill.ipynb`
4. Run files in `/data_scraping/PXPN_전처리/2_stage/src`
    Run `step.py`
    Run `step_delta.py`
    Run `step_analysis.py`
    Run `sleep_type.py`
    Run `sleep_log.py`
    Run `HR.py`
    Run `HR_statistics.py`
    Run `HR_interpolation.py`
    Run `HR_cosinor.py`
    Run `HR_cosinor_delta.py`
    Run `HR_bandpower_analysis.py`
5. Run `merge.py` in `/data_scraping/PXPN_전처리/3_stage`
6. Run files in /data_scraping/SYM_전처리/src/1_preprocessing
    Run `start_date.py`
    Run `smoking_diet_mens.py`
    Run `sleep.py`
    Run `questionnaire.py`
    Run `other_panic.py`
    Run `other_exercise.py`
    Run `other_demographics.py`
    Run `other_coffee.py`
    Run `other_alcohol.py`
    Run `lifelog_HR.py`
    Run `foot.py`
    Run `diary.py`
7. Run files in /data_scraping/SYM_전처리/src/2_data_analysis
    Run `step_delta.py`
    Run `step_analysis.py`
    Run `HR_statistics.py`
    Run `HR_interpolation.py`
    Run `HR_cosinor.py`
    Run `HR_cosinor_delta.py`
    Run `HR_bandpower_analysis.py`
8. Run `merge.py` in /data_scraping/SYM_전처리/src/3_merge
9. Run `merge.py` in /data_scraping/SYM_PXPN_merge



### Data Preprocessing
1. Move the `scraped_data.csv` to `./_data` directory
2. Open `data_preprocessing.ipynb`
3. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
4. Run All `data_preprocessing.ipynb`
5. Run All `data_imputation.ipynb`
6. Run All `data_analysis.ipynb`

> Install required packages specified in each `ipynb`

---

### Next day panic prediction model 1

### Next day panic prediction model 2

### Panic severity prediction model 
1. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
2. Under ⚙️|Settings, set `dbp` param to desired days before panic for data processing and dataset construction
3. Run All `severity_multiclass_pycare.ipynb`

> Install required packages specified in each `ipynb`