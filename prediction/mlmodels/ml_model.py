

# Step 1: Clean up old/conflicting packages
!pip uninstall -y numpy scipy shap xgboost scikit-learn imbalanced-learn --quiet

# Step 2: Reinstall compatible versions with force-reinstall
!pip install --upgrade --force-reinstall --quiet \
    numpy==1.24.4 \
    pandas==2.2.2 \
    scipy==1.11.4 \
    scikit-learn==1.3.2 \
    xgboost==1.7.6 \
    shap==0.41.0 \
    imbalanced-learn

# Step 3: Monkey patch deprecated NumPy aliases (for backward compatibility)
import numpy as np
np.bool = bool
np.int = int
np.float = float
np.object = object

print(" Environment setup completed successfully!")

# Step 4: Safe imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib
import warnings
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from scipy import stats

warnings.filterwarnings("ignore")
sns.set(style="whitegrid")

# 1. Load Dataset
df = pd.read_csv("heart_2020_cleaned.csv")

# 2. Initial Exploration
print("\nInitial Data Info:\n", df.info())
print("\nMissing Values:\n", df.isnull().sum())
print("\nDuplicate Rows:", df.duplicated().sum())
df = df.drop_duplicates()

# 3. Target Encoding
df['HeartDisease'] = df['HeartDisease'].map({'Yes': 1, 'No': 0})

# 4. Feature Categorization
categorical_cols = df.select_dtypes(include='object').columns.tolist()
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
numeric_cols.remove('HeartDisease')

# 5. Top-N Encoding
TOP_N = 3
top_categories_map = {}
for col in categorical_cols:
    top_n = df[col].value_counts().nlargest(TOP_N).index.tolist()
    top_categories_map[col] = top_n
    df[col] = df[col].apply(lambda x: x if x in top_n else 'Other')
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# 6. Outlier Removal
z_scores = np.abs(stats.zscore(df_encoded[numeric_cols]))
df_encoded = df_encoded[(z_scores < 3).all(axis=1)]

# 7. Feature Scaling
scaler = StandardScaler()
df_encoded[numeric_cols] = scaler.fit_transform(df_encoded[numeric_cols])

# 8. Prepare Data
X = df_encoded.drop('HeartDisease', axis=1)
y = df_encoded['HeartDisease']
final_feature_list = X.columns.tolist()

# 9. SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# 10. Model Setup
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "RandomForest": RandomForestClassifier(random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
}

# 11. Cross-Validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
cv_results = {}
for name, model in models.items():
    scores = cross_validate(model, X_resampled, y_resampled, cv=cv, scoring=scoring)
    cv_results[name] = {metric: np.mean(scores[f'test_{metric}']) for metric in scoring}
cv_df = pd.DataFrame(cv_results).T.round(4)
print("\n5-Fold Cross-Validation Results ")
print(cv_df)

# 12. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, stratify=y_resampled, random_state=42)

# 13. Train & Evaluate
results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    results[name] = {
        "model": model,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "report": classification_report(y_test, y_pred)
    }
    print(f"\n{name} Classification Report:")
    print(results[name]["report"])

# 13.5 Sigmoid Curve
x_vals = np.linspace(-10, 10, 100)
y_vals = 1 / (1 + np.exp(-x_vals))
plt.figure(figsize=(8, 5))
plt.plot(x_vals, y_vals, label='Sigmoid Function', color='blue', linewidth=2)
plt.axvline(0, color='black', linestyle='--', label='Threshold (0.5)')
plt.title('Sigmoid Function in Logistic Regression')
plt.xlabel('Weighted Sum of Features (z)')
plt.ylabel('Predicted Probability')
plt.legend()
plt.grid(True)
plt.show()

# 14. SHAP Summary Plot for XGBoost
explainer = shap.TreeExplainer(models["XGBoost"])
shap_values = explainer.shap_values(X_test.sample(200, random_state=42))
shap.summary_plot(shap_values, X_test.sample(200, random_state=42), plot_type="bar")

# 15. Confusion Matrices
for name, model in models.items():
    cm = confusion_matrix(y_test, model.predict(X_test))
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Confusion Matrix - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

# 16. ROC Curves
plt.figure(figsize=(10, 6))
for name, model in models.items():
    fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:,1])
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc_score(y_test, model.predict_proba(X_test)[:,1]):.2f})")
plt.plot([0,1], [0,1], 'k--')
plt.title("ROC Curves")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.grid(True)
plt.show()

# 17. Feature Importances
print("\nTop 10 Important Features Per Model:")
for name, model in models.items():
    print(f"\n{name}:")
    if hasattr(model, "feature_importances_"):
        imp = pd.Series(model.feature_importances_, index=X.columns)
    elif hasattr(model, "coef_"):
        imp = pd.Series(model.coef_[0], index=X.columns).abs()
    else:
        continue
    print(imp.sort_values(ascending=False).head(10))

# 18. Save Best Model
best_model_name = max(results, key=lambda x: results[x]['f1'])
joblib.dump(results[best_model_name]['model'], "heart_disease_model.pkl")
joblib.dump({
    "numeric_cols": numeric_cols,
    "categorical_cols": categorical_cols,
    "top_categories_map": top_categories_map,
    "scaler": scaler,
    "final_feature_list": final_feature_list
}, "preprocessing_artifacts.pkl")
print(f"\nBest model saved: {best_model_name}")
