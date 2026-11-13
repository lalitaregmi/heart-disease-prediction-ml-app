# Heart Disease Prediction Using Machine Learning

A machine-learning research project developed as part of my MSc in Data Science at York St John University, United Kingdom. The project explores the application of machine-learning algorithms to heart disease prediction and integrates the selected model into a Django-based web application.

## 1. Project Overview

Heart disease is a major public-health concern. This project investigates how machine-learning techniques can analyse health and lifestyle indicators to estimate the likelihood of heart disease.

Three machine-learning classification algorithms were implemented and compared:

- Logistic Regression
- Random Forest
- XGBoost

The models were evaluated using different classification metrics and visualisation techniques. Random Forest was selected as the best-performing model based on its F1-score in the original experimental evaluation.

The selected model was integrated into a Django web application called **HeartGuard**, which allows users to complete health assessments and receive estimated heart disease risk predictions.

**Project information:**
- Degree: MSc Data Science
- University: York St John University, United Kingdom
- Research project: Predictive Modelling for Heart Disease Diagnosis Using Electronic Health Records
- Research project mark: 72%
- Programming language: Python
- Web framework: Django

> **Disclaimer:** This project is an academic research prototype. It is not a clinically validated diagnostic system and must not be used as a substitute for professional medical advice.

## 2. Dataset

The project used the `heart_2020_cleaned.csv` dataset, derived from the CDC's 2020 Behavioral Risk Factor Surveillance System (BRFSS) survey data.

The dataset contains health and lifestyle indicators associated with heart disease, including:

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

**Dataset clarification:** Although the official dissertation title refers to Electronic Health Records, the dataset used in the implementation is survey-derived health data from the CDC BRFSS programme, rather than hospital electronic health records.

## 3. Methodology

### 3.1 Data Exploration and Preprocessing

The project included the following data preparation steps:

- Initial dataset exploration
- Missing-value and duplicate checks
- Duplicate-row removal
- Target-variable encoding
- Identification of categorical and numerical features
- Top-category grouping for categorical variables
- One-hot encoding
- Z-score-based outlier removal
- Numerical feature scaling using StandardScaler

### 3.2 Handling Class Imbalance

The Synthetic Minority Over-sampling Technique (SMOTE) was used to address class imbalance by generating synthetic samples for the minority class.

### 3.3 Machine-Learning Models

Three classification algorithms were implemented and compared.

| Algorithm | Description |
|---|---|
| Logistic Regression | Baseline binary classification model |
| Random Forest | Ensemble learning algorithm |
| XGBoost | Gradient-boosting classification algorithm |

### 3.4 Model Evaluation

The models were evaluated using stratified five-fold cross-validation and a train/test evaluation in the original experimental workflow.

The evaluation metrics included:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

Additional evaluation and visualisation techniques included:

- Classification reports
- Confusion matrices
- ROC curves
- Predicted probability distributions
- Feature-importance analysis

## 4. Model Performance Results

The following table presents the average five-fold cross-validation results reported in my MSc dissertation.

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7476 | 0.7550 | 0.7331 | 0.7439 | 0.8247 |
| Random Forest | **0.8891** | 0.8829 | **0.8971** | **0.8899** | 0.9471 |
| XGBoost | 0.8749 | **0.8935** | 0.8513 | 0.8719 | **0.9488** |

### Key Findings

- Random Forest achieved the highest F1-score of 0.8899.
- Random Forest achieved the highest recall of 0.8971.
- XGBoost achieved the highest precision of 0.8935.
- XGBoost achieved the highest ROC-AUC of 0.9488.
- Logistic Regression provided a baseline for comparison with the ensemble-based models.

Based on the highest F1-score, Random Forest was selected as the best-performing model in the original project and saved for integration into the web application.

*These figures are reproduced from the original MSc dissertation and represent the results of the original experimental workflow. They have not been independently verified.*

## 5. Explainable Artificial Intelligence (XAI)

SHAP (SHapley Additive exPlanations) was used to investigate feature contributions to the XGBoost model's predictions.

The project also examined feature importance from the individual classification models.

Some of the influential features identified in the analysis included:

- BMI
- General health
- Sleep time
- Mental health
- Physical health
- Diabetes
- Difficulty walking
- Stroke history
- Age category

The SHAP feature-importance analysis helped explore how different health and lifestyle indicators contributed to model outputs.

These feature-importance results describe model behaviour and should not be interpreted as proof of causal relationships with heart disease.

## 6. HeartGuard Web Application

The selected machine-learning model was integrated into a Django-based web application called **HeartGuard**.

The application demonstrates how a trained machine-learning model can be incorporated into a web-based health-risk assessment system.

### Main Features

- User registration and login
- Patient/user and doctor account roles
- Health and lifestyle risk-assessment questionnaire
- Machine-learning-based risk prediction
- Estimated risk-level display
- Prevention recommendations
- Assessment history for registered users
- Doctor dashboard
- Health information and prevention content

The application accepts user-provided health and lifestyle information, prepares the input using saved preprocessing components and passes it to the trained model to generate an estimated risk prediction.

The output is intended for academic demonstration and is not a medical diagnosis.

## 7. Technologies and Libraries

### Programming and Web Development
- Python
- Django
- HTML
- CSS

### Machine Learning and Data Science
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Imbalanced-learn (SMOTE)
- SHAP

### Data Visualisation
- Matplotlib
- Seaborn

### Model Saving and Development Tools
- Joblib
- Git
- GitHub
- Jupyter Notebook
- Poetry

## 8. Repository Structure

The repository is organised as a Django project with a main project configuration folder and a separate application for prediction functionality.

```text
heart-disease-prediction-ml-app/
│
├── heart_risk_project/
│
├── prediction/
│   ├── migrations/
│   ├── mlmodels/
│   ├── templates/
│   │   └── prediction/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── ml_model.py
│   ├── models.py
│   ├── test.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitattributes
├── README.md
├── manage.py
├── poetry.lock
└── pyproject.toml
```

### Main Components

- `heart_risk_project/`: Django project configuration.
- `prediction/`: Main application containing prediction, forms, views and database-related functionality.
- `prediction/mlmodels/`: Directory containing saved machine-learning and preprocessing artefacts.
- `prediction/templates/prediction/`: HTML templates used by the application.
- `manage.py`: Django management utility.
- `pyproject.toml`: Python project configuration and dependency declarations.
- `poetry.lock`: Locked dependency versions.
- `.gitattributes`: Git attributes configuration, including file-handling rules.

## 9. Saved Model and Preprocessing Artefacts

The application uses saved machine-learning and preprocessing artefacts stored in the `prediction/mlmodels/` directory.

The repository includes:

- `heart_disease_model.pkl`
- `features.pkl`

The model is loaded using Joblib. The preprocessing artefacts contain information required to prepare user inputs consistently with the features expected by the model.

The model file is stored using Git Large File Storage (Git LFS) because of its large size.

**Note:** The original training code saved the preprocessing artefact as `preprocessing_artifacts.pkl`, while the Django application uses `features.pkl`. The artefact supplied to the application must have the structure expected by `ml_model.py`.

## 10. Running the Application

The application was developed as a Django project.

### Step 1: Clone the Repository

```bash
git clone https://github.com/lalitaregmi/heart-disease-prediction-ml-app.git
cd heart-disease-prediction-ml-app
```

### Step 2: Retrieve Git LFS Files

Install Git LFS if it is not already installed, then run:

```bash
git lfs install
git lfs pull
```

This retrieves large files stored through Git Large File Storage.

### Step 3: Set Up the Python Environment

The repository includes `pyproject.toml` and `poetry.lock` for dependency management.

Set up the environment using the project's dependency configuration and the compatible Python and package versions.

### Step 4: Run the Django Development Server

After configuring the environment and dependencies, run:

```bash
python manage.py runserver
```

The application can then be accessed locally through the Django development server.

*Note: These are general setup instructions. The original project may require additional environment-specific configuration.*

## 11. Methodological Limitations and Future Research

The original implementation has methodological limitations that should be considered when interpreting the reported evaluation results.

In the original training workflow:

- SMOTE was applied to the complete dataset before cross-validation and the train/test split.
- Preprocessing operations were performed before the data split.
- This creates a risk of data leakage because information from observations later used for validation or testing may influence the training process.

Consequently, the reported evaluation metrics may provide optimistic estimates of model performance. They should not be interpreted as independently validated performance on unseen real-world populations.

Potential areas for future investigation include:

- Applying preprocessing and SMOTE within training folds using an appropriate pipeline.
- Evaluating models on an untouched test set with the original class distribution.
- Investigating model calibration and prediction uncertainty.
- Assessing performance across different demographic groups.
- Exploring external validation using independent datasets.
- Improving explainability and interpretation of individual predictions.
- Investigating responsible, human-centred applications of machine learning in digital health.

The original project code has been retained as developed for the MSc research project. This README documents the methodology and its limitations; it does not imply that the implementation has been revised.

## 12. Author

**Lalita Regmi**

MSc Data Science  
York St John University, United Kingdom

GitHub: https://github.com/lalitaregmi

## 13. Disclaimer

This project was developed for academic purposes as part of an MSc research project.

The HeartGuard application is an experimental research prototype. It is not a medical device, does not provide a clinical diagnosis and has not been established as suitable for clinical use.

The predictions should not be used to make medical decisions. Users should consult qualified healthcare professionals for medical advice, diagnosis and treatment.
