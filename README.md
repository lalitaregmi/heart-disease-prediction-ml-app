# Heart Disease Prediction Using Machine Learning

A machine-learning research project developed as part of my MSc in Data Science at York St John University. The project explores the use of classification algorithms to predict heart disease indicators and integrates a selected model into a Django-based web application.

## Project Overview

Heart disease is an important public-health concern. This project investigates how machine-learning techniques can be used to analyse health and lifestyle indicators and estimate the likelihood of heart disease.

Three classification algorithms were implemented and compared:

- Logistic Regression
- Random Forest
- XGBoost

The models were evaluated using classification metrics and visual analysis. Random Forest was selected as the best-performing model based on its reported F1-score in the project's evaluation.

The selected model was integrated into a Django web application called **HeartGuard**.

> **Important:** This project is an academic research prototype. It is not a clinically validated diagnostic system and should not be used to make medical decisions.

## Research Project Information

- **Degree:** MSc Data Science
- **University:** York St John University, United Kingdom
- **Project:** Predictive Modelling for Heart Disease Diagnosis Using Electronic Health Records
- **Project mark:** 72%
- **Programming language:** Python
- **Web framework:** Django

## Dataset

The project used the `heart_2020_cleaned.csv` heart disease indicators dataset, derived from the CDC's 2020 Behavioral Risk Factor Surveillance System (BRFSS) survey data.

The dataset contains health and lifestyle indicators, including:

- Heart disease status
- Body Mass Index (BMI)
- Smoking
- Alcohol consumption
- Physical activity
- General health
- Physical and mental health
- Sleep time
- Diabetes
- Stroke history
- Kidney disease
- Age category and other demographic indicators

The target variable was `HeartDisease`, encoded as:
- `1`: Yes
- `0`: No

The dataset represents survey-derived health indicators, not hospital electronic health records.

## Methodology

### 1. Data exploration and preprocessing

The project included:

- Initial dataset exploration
- Missing-value and duplicate checks
- Duplicate-row removal
- Target-variable encoding
- Categorical feature grouping using top-category encoding
- One-hot encoding
- Z-score-based outlier removal
- Numerical feature scaling using StandardScaler

### 2. Class imbalance handling

SMOTE (Synthetic Minority Over-sampling Technique) was used to generate synthetic minority-class samples and balance the class distribution.

### 3. Model development

Three classification algorithms were trained and compared:

| Model | Description |
|---|---|
| Logistic Regression | Baseline classification model |
| Random Forest | Ensemble learning model |
| XGBoost | Gradient-boosting classification model |

### 4. Model evaluation

The project used stratified five-fold cross-validation and a separate train/test evaluation in the original experimental workflow.

Evaluation metrics included:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

Additional analysis included classification reports, confusion matrices, ROC curves and feature-importance visualisations.

### 5. Explainable AI

SHAP (SHapley Additive exPlanations) was used to examine feature contributions to the XGBoost model's predictions.

Feature-importance analysis was also conducted for the three models to investigate the health and lifestyle variables that influenced their predictions.

## Reported Model Results

The following table presents the average five-fold cross-validation results reported in the MSc dissertation.

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7476 | 0.7550 | 0.7331 | 0.7439 | 0.8247 |
| Random Forest | **0.8891** | 0.8829 | **0.8971** | **0.8899** | 0.9471 |
| XGBoost | 0.8749 | **0.8935** | 0.8513 | 0.8719 | **0.9488** |

Random Forest achieved the highest cross-validation F1-score (0.8899), while XGBoost achieved the highest cross-validation precision (0.8935) and ROC-AUC (0.9488).

Random Forest was selected as the best-performing model based on F1-score.

These figures are reproduced from the original MSc dissertation and are not independently verified.

## Important Methodological Limitation

In the original implementation, SMOTE was applied to the complete dataset before cross-validation and the train/test split. Consequently, synthetic samples could be related to observations later included in validation or test sets. Preprocessing was also performed before splitting.

This introduces a risk of data leakage and may lead to optimistic performance estimates. The reported metrics should therefore be interpreted in the context of the original experimental procedure rather than as independently validated estimates of performance on unseen real-world populations.

The original project code has been retained as developed for the MSc project. This README documents its methodology and limitations; it does not imply that the implementation has been revised.

## HeartGuard Web Application

The selected model was integrated into a Django-based web application named **HeartGuard**.

### Application features

- User registration and login
- Patient/user and doctor account roles
- Health and lifestyle risk-assessment questionnaire
- Machine-learning-based risk prediction
- Estimated risk-level display
- Prevention recommendations
- Assessment history for registered users
- Doctor dashboard
- Health information and prevention content

The application displays estimated risk categories and is intended as an academic demonstration of machine-learning integration into a web application.

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Imbalanced-learn (SMOTE)
- SHAP
- Matplotlib
- Seaborn
- Joblib
- Django
- HTML and CSS
- Git and GitHub

## Project Structure

The main Django application is organised into the following components:

```text
heart-disease-prediction-ml-app/
│
├── heart_risk_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── prediction/
│   ├── migrations/
│   ├── mlmodels/
│   ├── templates/
│   │   └── prediction/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── ml_model.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
└── README.md
```

The `prediction` application contains the model-loading, input-preparation, prediction and web application functionality.

## Model and Preprocessing Files

The application uses saved machine-learning and preprocessing artefacts stored in the `prediction/mlmodels/` directory.

The repository includes:
- `heart_disease_model.pkl`
- `features.pkl`

The model is loaded using Joblib. The preprocessing artefacts contain information required to prepare user inputs consistently with the model's expected features.

The original training notebook saved its preprocessing artefacts under the filename `preprocessing_artifacts.pkl`. The application repository uses `features.pkl`; users reproducing the project should ensure that the artefact supplied to the application has the structure expected by `ml_model.py`.

The model file is large and is stored using Git Large File Storage (Git LFS).

## Running the Application

The application was developed as a Django project. The exact dependency versions and environment configuration should be checked against the original project files before setting up a new environment.

### Clone the repository

```bash
git clone https://github.com/lalitaregmi/heart-disease-prediction-ml-app.git
cd heart-disease-prediction-ml-app
```

### Retrieve Git LFS files

If Git LFS is used for the model artefacts, install and initialise Git LFS before retrieving the large files:

```bash
git lfs install
git lfs pull
```

### Set up the Python environment

Install the project's dependencies using the dependency configuration supplied in the repository. The original development environment used Python and the libraries listed in the Technologies Used section.

### Start the Django development server

After the environment and dependencies are configured:

```bash
python manage.py runserver
```

The application can then be accessed locally through the Django development server.

**Note:** The original project may require environment-specific configuration or additional setup. These instructions describe the general workflow and are not a guarantee of a clean installation on every system.

## Limitations and Future Research

Potential areas for further investigation include:

- Evaluating models with preprocessing and SMOTE applied only within training folds.
- Using an untouched test set with the original class distribution.
- Assessing model performance across different demographic groups.
- Investigating model calibration and prediction uncertainty.
- Improving explainability and interpretation of individual predictions.
- Exploring external validation using independent datasets.
- Investigating the suitability of machine learning for responsible, human-centred digital-health applications.

## Author

**Lalita Regmi**

MSc Data Science, York St John University, United Kingdom

GitHub: https://github.com/lalitaregmi

## Disclaimer

This project was developed for academic purposes as part of an MSc research project. It is not a medical device, does not provide a clinical diagnosis and has not been established as suitable for clinical use. Users should consult qualified healthcare professionals for medical advice.

Git and GitHub
