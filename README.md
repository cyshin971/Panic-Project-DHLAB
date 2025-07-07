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

### Data Preprocessing
1. Move the `scraped_data.csv` to `./_data` directory
2. Open `data_preprocessing.ipynb`
3. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
4. Run All `data_preprocessing.ipynb`
5. Run All `data_imputation.ipynb`
6. Run All `data_analysis.ipynb`

> Install packages required specified in each `ipynb`

### Panic Severity 
1. Under ⚙️|Settings, change `scraped_data_filename` to selected `scraped_data`
2. Under ⚙️|Settings, set `dbp` param to desired days before panic for data processing and datset construction
3. Run All `severity_multiclass_pycare.ipynb`

> Install packages required specified in each `ipynb`