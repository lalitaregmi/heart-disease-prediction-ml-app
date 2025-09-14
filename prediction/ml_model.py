# prediction/ml_model.py

import os
import logging
import pandas as pd
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# --- Global variables to hold the loaded objects ---
MODEL = None
PREPROCESSING_ARTIFACTS = None
MODEL_FEATURES = []
LOADING_SUCCESSFUL = False

# File paths
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
ML_FILES_DIR = os.path.join(MODEL_DIR, 'mlmodels')
MODEL_PATH = os.path.join(ML_FILES_DIR, 'heart_disease_model.pkl')
ARTIFACTS_PATH = os.path.join(ML_FILES_DIR, 'features.pkl')

def load_ml_artifacts():
    """
    Loads both the model and the single preprocessing artifacts file.
    This function should be called once when the Django application starts.
    """
    global MODEL, PREPROCESSING_ARTIFACTS, MODEL_FEATURES, LOADING_SUCCESSFUL
    try:
        if not os.path.exists(MODEL_PATH):
            logger.error(f" Model file not found at: {MODEL_PATH}")
            return
        
        if not os.path.exists(ARTIFACTS_PATH):
            logger.error(f" Preprocessing artifacts file not found at: {ARTIFACTS_PATH}")
            return

        # Load the model
        MODEL = joblib.load(MODEL_PATH)
        logger.info(" Model loaded successfully.")

        # Load the preprocessing artifacts dictionary
        PREPROCESSING_ARTIFACTS = joblib.load(ARTIFACTS_PATH)
        logger.info(" Preprocessing artifacts loaded successfully.")

        # Populate the MODEL_FEATURES list from within the artifacts for convenience
        MODEL_FEATURES = PREPROCESSING_ARTIFACTS.get('final_feature_list', [])
        if not MODEL_FEATURES:
            logger.error(" 'final_feature_list' not found in artifacts. Preprocessing may fail.")
            LOADING_SUCCESSFUL = False
            return
            
        LOADING_SUCCESSFUL = True

    except Exception as e:
        logger.error(f" Failed to load ML model or artifacts: {e}", exc_info=True)
        MODEL = None
        PREPROCESSING_ARTIFACTS = None
        MODEL_FEATURES = []
        LOADING_SUCCESSFUL = False

def prepare_user_input(form_data: dict) -> pd.DataFrame:
    """
    Prepares raw form data for prediction by applying the same preprocessing steps 
    used during model training.
    """
    if not LOADING_SUCCESSFUL or not PREPROCESSING_ARTIFACTS:
        raise RuntimeError("Preprocessing artifacts are not loaded. Cannot prepare input.")

    input_df = pd.DataFrame(0, index=[0], columns=MODEL_FEATURES)

    numeric_cols = PREPROCESSING_ARTIFACTS['numeric_cols']
    for col in numeric_cols:
        value = form_data.get(col, 0)
        input_df.loc[0, col] = float(value)

    binary_fields = [
        'Smoking', 'AlcoholDrinking', 'Stroke', 'DiffWalking',
        'PhysicalActivity', 'Asthma', 'KidneyDisease', 'SkinCancer'
    ]
    for field in binary_fields:
        if form_data.get(field) == 'Yes':
            feature_name = f'{field}_Yes'
            if feature_name in input_df.columns:
                input_df.loc[0, feature_name] = 1

    if form_data.get('Sex') == 'Male':
        input_df.loc[0, 'Sex_Male'] = 1

    top_categories_map = PREPROCESSING_ARTIFACTS['top_categories_map']
    for col, top_cats in top_categories_map.items():
        user_value = form_data.get(col)
        if not user_value:
            continue

        if user_value in top_cats:
            feature_name = f"{col}_{user_value}"
            if feature_name in input_df.columns:
                input_df.loc[0, feature_name] = 1
        else:
            feature_name = f"{col}_Other"
            if feature_name in input_df.columns:
                input_df.loc[0, feature_name] = 1

    scaler = PREPROCESSING_ARTIFACTS['scaler']
    input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])

    return input_df


def predict(input_df: pd.DataFrame) -> (int, list):
    """
    Takes the prepared DataFrame, returns the prediction and probabilities.
    """
    if not LOADING_SUCCESSFUL or MODEL is None:
        raise RuntimeError("Model is not loaded. Cannot make a prediction.")
        
    prediction_code = MODEL.predict(input_df)[0]
    probability_array = MODEL.predict_proba(input_df)[0]
    
    return int(prediction_code), list(probability_array)

# --- NEW FUNCTION TO BE ADDED ---
def get_risk_label(probability: float) -> str:
    """
    Converts a prediction probability (for class '1' - Heart Disease) 
    into a human-readable risk label.
    """
    if probability >= 0.70:  # 70% chance or higher
        return "High Risk"
    elif probability >= 0.40: # 40% to 69.9% chance
        return "Mild Risk"
    else:                    # Below 40% chance
        return "Low Risk"

# --- Call the loading function when this module is imported by Django ---
load_ml_artifacts()