import pandas as pd
import joblib

# Load the trained model 
model = joblib.load('C:\\Users\\Ait\Desktop\\vulnerability_prediction_model.pkl')

# Load new scan data 
new_data = pd.read_csv('C:\\Users\\Ait\\Desktop\\ZAP-Report.csv')

# Inspect the new data columns to ensure they match expected names
print("New scan data columns:", new_data.columns.tolist())

# Preprocess new data similar to training:
# - Map severity values to numeric; adjust the column name if necessary.
#   Here, we assume the new CSV has a column named 'severity' with values "Low", "Medium", "High".
if 'severity' in new_data.columns:
    severity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    new_data['severity_numeric'] = new_data['severity'].map(severity_mapping)
else:
    # Alternatively, if using riskcode as severity (numeric already), you can do:
    new_data['severity_numeric'] = new_data['riskcode'].astype(int)

# One-hot encode categorical columns.
# Note: Adjust column names if your new scan CSV uses different names.
# For example, if your new CSV uses 'vulnerability_type' and 'url' (instead of 'alert' and 'site'):
new_data_processed = pd.get_dummies(new_data, columns=['vulnerability_type', 'url'])

# If your training data used different column names (for example, 'alert' for vulnerability type and 'site' for URL),
# you must align the new data's columns with the training features.
# One approach is to add missing columns with zeros. For example, if your training model expects columns in model.feature_names_in_:
trained_features = model.feature_names_in_
for col in trained_features:
    if col not in new_data_processed.columns:
        new_data_processed[col] = 0

# Ensure the new data is ordered in the same way as the training features.
X_new = new_data_processed[trained_features]

# Predict vulnerabilities using the trained model
predictions = model.predict(X_new)

# Add the predictions to the new data
new_data['predicted_vulnerability'] = predictions

# Identify high-risk vulnerabilities (assuming a prediction of 1 indicates a vulnerability)
high_risk_vulnerabilities = new_data[new_data['predicted_vulnerability'] == 1]

print("High-Risk Vulnerabilities Detected:")
print(high_risk_vulnerabilities)
