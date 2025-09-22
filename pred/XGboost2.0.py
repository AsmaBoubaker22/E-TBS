import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt



df = pd.read_csv("simulatedAttendanceDataset.csv")

# ENCODING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Step 1: Binary encode `session_type`
df['session_type'] = df['session_type'].map({'Lecture': 0, 'Tutorial': 1})

# Step 2: One-hot encode categorical features
categorical_features = ['time_of_day', 'day_of_week', 'commute_type', 'weather_condition']
df = pd.get_dummies(df, columns=categorical_features, drop_first=False)


# Display resulting columns
print("Encoded feature columns:")
print(df.columns.tolist())


# CLEANING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Check for missing values
print("Missing values per column:")
print(df.isnull().sum())

# Check for duplicate rows
duplicate_count = df.duplicated().sum()
print(f"\n Number of duplicate rows: {duplicate_count}")

# Check value ranges (continuous features)
print("\n Range of continuous features:")
print("GPA:", df['student_gpa'].min(), "to", df['student_gpa'].max())
print("Avg Grade Last Year:", df['avg_grade_last_year'].min(), "to", df['avg_grade_last_year'].max())
print("Fail Rate Last Year:", df['fail_rate_last_year'].min(), "to", df['fail_rate_last_year'].max())

# Loop through all day_of_week columns 
day_columns = [col for col in df.columns if col.startswith('day_of_week_')]

for col in day_columns:
    count = df[df[col] == 1].shape[0]
    print(f"{col}: {count} rows")


# Initialize the scaler
scaler = MinMaxScaler()

# Normalize continuous features to range [0, 1]
df[['student_gpa_norm', 'attendance_rate_norm', 'avg_grade_last_year_norm', 'fail_rate_last_year_norm']] = scaler.fit_transform(
    df[['student_gpa', 'attendance_rate', 'avg_grade_last_year', 'fail_rate_last_year']]
)


df['first_session_of_day'] = df['time_of_day_08:30'].astype(int)
df['last_session_of_day'] = df['time_of_day_15:00'].astype(int)
df['is_single_session_day'] = (df['number_of_courses_per_day'] == 1).astype(int)

df['gpa_x_attendance_rate'] = df['student_gpa'] * df['attendance_rate']
df['risk_averse_x_tracked'] = ((df['is_risk_averse'] == 1) & (df['is_attendance_tracked'] == 1)).astype(int)

# Academic risk with no safety net
df['at_risk_no_enforcement'] = (
    (df['student_gpa'] < 2.5) & 
    (df['is_attendance_tracked'] == 0) & 
    (df['is_participation_graded'] == 0)
).astype(int)




# MODAL TRAINING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

X = df.drop(columns=['final_attendance'])  # Features
y = df['final_attendance']                # Target


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
features_to_drop = [
    'student_gpa_norm',
    'fail_rate_last_year_norm',
    'avg_grade_last_year_norm',
    'avg_grade_last_year'
]

X_train = X_train.drop(columns=features_to_drop, errors='ignore')
X_test = X_test.drop(columns=features_to_drop, errors='ignore')


xgb_model = xgb.XGBClassifier(
    n_estimators=250,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=1,
    scale_pos_weight=0.8,  # Lower = bias toward absent (class 0)
    eval_metric='logloss',
    random_state=42
)

xgb_model.fit(X_train, y_train)

y_pred_final_xgb = xgb_model.predict(X_test)
y_proba_final_xgb = xgb_model.predict_proba(X_test)[:, 1]

print("Final XGBoost (Re-tuned) Metrics")
print(f"Accuracy:  {accuracy_score(y_test, y_pred_final_xgb):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_final_xgb):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_final_xgb):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred_final_xgb):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_final_xgb))

print("\nClassification Report:")
print(classification_report(y_test, y_pred_final_xgb))

results_final_xgb = pd.DataFrame({
    'Actual': y_test.values,
    'Predicted': y_pred_final_xgb,
    'Attendance_Probability': y_proba_final_xgb
})
print("\n Sample predictions with probabilities:")
print(results_final_xgb.head(10))


import shap

# Convert X_train to numeric format
X_train_shap = X_train.select_dtypes(include=['int64', 'float64', 'bool'])

# Create the explainer with the numeric features only
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_train_shap)

# Your selected key features
features_to_plot = [
    "is_attendance_tracked",
    "attendance_rate",
    "session_type",
    "is_participation_graded",
    "gpa_x_attendance_rate"
]

# Generate individual dependence plots for each feature
for feature in features_to_plot:
    if feature in X_train_shap.columns:
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(
            ind=feature,
            shap_values=shap_values,
            features=X_train_shap,
            show=False,
            alpha=0.5,
            dot_size=50
        )
        plt.title(f"SHAP Dependence Plot for {feature}")
        plt.tight_layout()
        plt.show()
        plt.close()  # Close the figure to free memory

# Create a summary plot of feature importance
#plt.figure(figsize=(10, 6))
#shap.summary_plot(shap_values, X_train_shap, plot_type="bar", show=False)
#plt.title("Feature Importance Based on SHAP Values")
#plt.tight_layout()
#plt.show()
#plt.close()

from sklearn.inspection import permutation_importance

# Run on test set (X_test, y_test)
#perm = permutation_importance(xgb_model, X_test, y_test, n_repeats=10, scoring='f1', random_state=42)

# Display sorted
#sorted_idx = perm.importances_mean.argsort()[::-1]
#for i in sorted_idx:
#    print(f"{X_test.columns[i]}: {perm.importances_mean[i]:.4f}")

#plt.barh(X_test.columns[sorted_idx][:20], perm.importances_mean[sorted_idx][:20])
#plt.title("Permutation Importance (F1 Score)")
#plt.xlabel("Mean Importance")
#plt.gca().invert_yaxis()
#plt.tight_layout()
#plt.show()
