import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import shap
from sklearn.inspection import permutation_importance



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
df['gpa_x_attendance_rate'] = df['student_gpa_norm'] * df['attendance_rate_norm']
def classify_weather_commute(row):
    if row['weather_condition_Rainy'] == 1 and row['commute_type_shuttler'] == 1:
        return 'High'
    elif row['weather_condition_Cold'] == 1 and row['commute_type_renter_weekly'] == 1:
        return 'Medium'
    else:
        return 'Low'

df['weather_x_commute_risk'] = df.apply(classify_weather_commute, axis=1)
df['risk_averse_x_tracked'] = ((df['is_risk_averse'] == 1) & (df['is_attendance_tracked'] == 1)).astype(int)
df['difficulty_score'] = (1 - df['avg_grade_last_year_norm']) + df['fail_rate_last_year_norm']
df['difficulty_weighted_by_gpa'] = df['difficulty_score'] * (1 - df['student_gpa_norm'])
def classify_commute_fatigue(row):
    if row.get('commute_type_shuttler', 0) == 1 and row.get('time_of_day_08:30', 0) == 1:
        return 'High'
    elif (row.get('commute_type_renter_weekly', 0) == 1 or row.get('commute_type_renter_rarely', 0) == 1) and row.get('time_of_day_08:30', 0) == 1:
        return 'Medium'
    else:
        return 'Low'

df['commute_fatigue_index'] = df.apply(classify_commute_fatigue, axis=1)
df = pd.get_dummies(df, columns=['weather_x_commute_risk', 'commute_fatigue_index'], drop_first=False)


# Students who need enforcement vs those who don't
df['enforcement_dependency'] = (
    (df['is_attendance_tracked'] == 0) & 
    (df['is_participation_graded'] == 0) & 
    (df['attendance_rate'] < 0.6)
).astype(int)

# High achievers in low-enforcement settings
df['self_motivated_high_performer'] = (
    (df['student_gpa'] > 3.0) & 
    (df['is_attendance_tracked'] == 0) & 
    (df['attendance_rate'] > 0.7)
).astype(int)

# Academic risk with no safety net
df['at_risk_no_enforcement'] = (
    (df['student_gpa'] < 2.5) & 
    (df['is_attendance_tracked'] == 0) & 
    (df['is_participation_graded'] == 0)
).astype(int)

# Build on attendance_tracked (your strongest signal)
df['tracked_but_poor_attendance'] = (
    (df['is_attendance_tracked'] == 1) & 
    (df['attendance_rate'] < 0.7)
).astype(int)

df['tracked_high_risk'] = (
    (df['is_attendance_tracked'] == 1) & 
    (df['student_gpa'] < 2.5)
).astype(int)

# Expand the successful risk_averse_x_tracked pattern
df['risk_averse_x_participation'] = (
    (df['is_risk_averse'] == 1) & 
    (df['is_participation_graded'] == 1)
).astype(int)

df['risk_averse_x_session_type'] = (
    (df['is_risk_averse'] == 1) & 
    (df['session_type'] == 1)
).astype(int)



# MODAL TRAINING ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

X = df.drop(columns=['final_attendance'])  # Features
y = df['final_attendance']                # Target


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

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

y_pred_xgb = xgb_model.predict(X_test)
y_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]

print("XGBoost Metrics")
print(f"Accuracy:  {accuracy_score(y_test, y_pred_xgb):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_xgb):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_xgb):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred_xgb):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_xgb))

print("\nClassification Report:")
print(classification_report(y_test, y_pred_xgb))

results_xgb = pd.DataFrame({
    'Actual': y_test.values,
    'Predicted': y_pred_xgb,
    'Attendance_Probability': y_proba_xgb
})
print("\n Sample predictions with probabilities:")
print(results_xgb.head(10))


# ----------- 1. XGBoost Built-in Importance (Gain) ------------------
plt.figure(figsize=(10, 6))
xgb.plot_importance(xgb_model, importance_type='gain', title='XGBoost Feature Importance (Gain)', max_num_features=20)
plt.tight_layout()
plt.show()


# ----------- 2. Permutation Importance -------------------------------
perm_result = permutation_importance(xgb_model, X_test, y_test, n_repeats=10, random_state=42, scoring='f1')

# Convert to DataFrame for plotting
perm_df = pd.DataFrame({
    'feature': X_test.columns,
    'importance': perm_result.importances_mean
}).sort_values(by='importance', ascending=False)

# Plot Permutation Importance
plt.figure(figsize=(10, 6))
perm_df.head(20).plot(kind='barh', x='feature', y='importance', legend=False, title='Permutation Importance (F1-based)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()



# ----------- 3. SHAP Values ------------------------------------------
# Create TreeExplainer instead of regular Explainer
#explainer = shap.TreeExplainer(xgb_model)
#shap_values = explainer.shap_values(X_test)

# Global summary
#plt.figure(figsize=(10, 6))
#shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
#plt.tight_layout()
#plt.show()
#plt.close()

# Full summary
#plt.figure(figsize=(10, 8))
#shap.summary_plot(shap_values, X_test, show=False)
#plt.tight_layout()
#plt.show()
#plt.close()
