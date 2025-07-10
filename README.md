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
2. move the `pixelpanic_raw_data.zip` to `/raw_data/PXPN` directory
3. Download the `픽셀패닉 enroll 정보` and move to `/raw_data/PXPN`
3. Dowonload the SYM1, SYM2 excel files
4. move the SYM excel files to `/data_scraping/raw_data/PXPN`
5. Run  `/data_scraping/PXPN/1_stage.ipynb`
        `/data_scraping/PXPN/2_stage.ipynb`
        `/data_scraping/PXPN/3_stage.ipynb`
6. Run  `/data_scraping/SYM/1_stage_SYM.ipynb`
        `/data_scraping/SYM/2_stage_SYM.ipynb`
        `/data_scraping/SYM/3_stage_SYM.ipynb`
7. Run  `/data_scraping/SYM_PXPN_merge/merge.ipynb`


### Data Preprocessing
1. Move the `scraped_data.csv` to `./_data` directory
2. Open `data_preprocessing.ipynb`
3. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
4. Run All `data_preprocessing.ipynb`
5. Run All `data_imputation.ipynb`
6. Run All `data_analysis.ipynb`
7. Run `full_dataset.py`
> Install required packages specified in each `ipynb`

---

### Next day panic prediction model 1
1. Run `/Panic-Project-DHLAB/model/Gradient_boosting_clasifier.py` with `test_set.csv` or new dataset
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