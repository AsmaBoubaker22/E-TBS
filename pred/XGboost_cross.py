import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer, accuracy_score, f1_score, recall_score
import numpy as np



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

y_pred = xgb_model.predict(X_test)
y_proba = xgb_model.predict_proba(X_test)[:, 1]

print("Final XGBoost (Re-tuned) Metrics")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

results_final_xgb = pd.DataFrame({
    'Actual': y_test.values,
    'Predicted': y_pred,
    'Attendance_Probability': y_proba
})
print("\n Sample predictions with probabilities:")
print(results_final_xgb.head(10))



# Create custom scorers
scoring = {
    'accuracy': make_scorer(accuracy_score),
    'f1': make_scorer(f1_score),
    'recall_absent': make_scorer(recall_score, pos_label=0)
}

# Run cross-validation (5-fold)
cv_results = cross_validate(
    xgb_model,
    X_train, 
    y_train,
    cv=5,
    scoring=scoring,
    return_train_score=False
)

# Print results
for metric in scoring.keys():
    mean = np.mean(cv_results[f'test_{metric}'])
    std = np.std(cv_results[f'test_{metric}'])
    print(f"{metric}: {mean:.4f} ± {std:.4f}")
