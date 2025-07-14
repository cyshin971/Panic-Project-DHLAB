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
## Required Packages
`Python Version = 3.10`
- `ipykernel`
- `pandas`
- `openpyxl`
- `xlrd`
- `mne`
- `CosinorPy`
- `seaborn`

## Instructions

### Setup
1. Install required packages:  
- `cd <Panic-Project-DHLAB root directory>`
- `conda env create -f dhlab_panic_env.yml`
- `conda activate dhlab_panic_env`
1. Navigate to the shared dropbox `픽셀패닉 데이터_연세대 제공용`
2. Download `픽셀패닉 Raw Data` folder
    - rename to `pixelpanic_raw_data.zip`
    - if the file is not compressed, compress to `zip` file
4. Move `pixelpanic_raw_data.zip` to `./raw_data/PXPN/` directory
    - Create `./raw_data/PXPN/` directory if it does not exist
5. Download "픽셀패닉 enroll 정보"
    - `1. 픽셀패닉 enroll 정보_250516.xlsx` (20250711)
    - if using new enroll file, change `enroll_file_name` under in `PXPN/1-stage.ipynb`
6. Move "픽셀패닉 enroll 정보" to `/data_scraping/raw_data/PXPN/`
7. Download `SYM.zip`
8. Extract `SYM.zip`
9. Move the SYM excel files to `/data_scraping/raw_data/SYM`
    - `backup_SYM2.xlsx`
    - `backup_SYM1.xlsx`

### Data Scraping
1. Run PXPN data scraping notebooks
    1. `./data_scraping/PXPN/1_stage.ipynb`  
        - Under ⚙️|Settings, update `enroll_file_name` to "픽셀패닉 enroll 정보" file name
    2. `./data_scraping/PXPN/2_stage.ipynb`  
        - Under ⚙️|Settings, update `enroll_file_name` to "픽셀패닉 enroll 정보" file name
    3. `./data_scraping/PXPN/3_stage.ipynb`  
2. Run SYM data scraping notebooks
    1. `./data_scraping/SYM/1_stage_SYM.ipynb`  
    2. `./data_scraping/SYM/2_stage_SYM.ipynb`  
    3. `./data_scraping/SYM/3_stage_SYM.ipynb`  
3. Run `./data_scraping/SYM_PXPN_merge/merge.ipynb`
4. Check `merged_df.csv` in `./data/`


### Data Preprocessing
2. Open `./data_preprocessing/data_preprocessing.ipynb`
3. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
4. Run All `./data_preprocessing/data_preprocessing.ipynb`
5. Run All `./data_preprocessing/data_imputation.ipynb`
6. Run All `./data_preprocessing/data_analysis.ipynb`
7. Run `full_dataset.py`
> Install required packages specified in each `ipynb`

---

### Next day panic prediction model 1
1. Run `./model/Gradient_boosting_classifier.py` with your dataset.
2. If you want to test with an existing datset,
    run `/model/unseen_test_set.py`
    and run `./model/Gradient_boosting_classifier.py`
### Next day panic prediction model 2
To select the best model for each domain:
1. ⚙️|Settings, set the parameters in `./library/config_domain.yaml`
2. Run the domain_main script, passing in the config file:
    ```bash
    PYTHONPATH=./Panic-Project-DHLAB \
    python ./panic_domain_model/domain_main.py \
    --config ./library/config_domain.yaml
    ```
To create an ensemble model using all the best domain models:
1. ⚙️|Settings, set the parameters in `./library/config_ensemble.yaml`
2. Run the domain_ensemble script, passing in the config file:
    ```bash
    PYTHONPATH=./Panic-Project-DHLAB \
    python ./panic_domain_model/domain_ensemble.py \
    --config ./library/config_ensemble.yaml
    ```
### Panic severity prediction model 
1. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
2. Under ⚙️|Settings, set `dbp` param to desired days before panic for data processing and dataset construction
3. Run All `severity_multiclass_pycare.ipynb`

> Install required packages specified in each `ipynb`