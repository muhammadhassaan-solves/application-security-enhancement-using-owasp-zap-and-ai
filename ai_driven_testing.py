import pandas as pd
import joblib

# ---------------------------
# 0. CONFIGURATION
MODEL_PATH = r"C:\Users\Ait\Desktop\vulnerability_prediction_model.pkl"
CSV_PATH = r"C:\Users\Ait\Desktop\ZAP-Report-renamed.csv"  # or ZAP-Report.csv if you haven't renamed
VULN_COL = "vulnerability_type"   # The column name in your CSV that represents the vulnerability type
URL_COL = "url"                   # The column name in your CSV that represents the URL
SEVERITY_COL = "riskcode"         # The column name you use as a proxy for severity
USE_SEVERITY_MAPPING = False      # Set to True if you have "Low"/"Medium"/"High" in SEVERITY_COL
# ---------------------------

# 1. Load the trained model
print(f"Loading model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

# 2. Load your CSV scan data
print(f"Loading new scan data from: {CSV_PATH}")
new_data = pd.read_csv(CSV_PATH)
print("Columns in the loaded CSV:", new_data.columns.tolist())

# 3. Preprocess severity
if USE_SEVERITY_MAPPING:
    # If your CSV has "Low", "Medium", "High"
    severity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    if SEVERITY_COL in new_data.columns:
        new_data['severity_numeric'] = new_data[SEVERITY_COL].map(severity_mapping)
    else:
        print(f"Warning: Column '{SEVERITY_COL}' not found for severity mapping. Using riskcode=0 as fallback.")
        new_data['severity_numeric'] = 0
else:
    # If you're using riskcode as an integer
    if SEVERITY_COL in new_data.columns:
        new_data['severity_numeric'] = new_data[SEVERITY_COL].astype(int)
    else:
        print(f"Warning: Column '{SEVERITY_COL}' not found. Creating severity_numeric=0 as fallback.")
        new_data['severity_numeric'] = 0

# 4. One-hot encode categorical columns if they exist
columns_to_encode = []
if VULN_COL in new_data.columns:
    columns_to_encode.append(VULN_COL)
else:
    print(f"Warning: '{VULN_COL}' not found in CSV; skipping one-hot encoding for it.")

if URL_COL in new_data.columns:
    columns_to_encode.append(URL_COL)
else:
    print(f"Warning: '{URL_COL}' not found in CSV; skipping one-hot encoding for it.")

new_data_processed = pd.get_dummies(new_data, columns=columns_to_encode)

# 5. Align with the model’s expected features
trained_features = model.feature_names_in_
print("Model expects these features:", trained_features)

# Add any missing columns with default 0
for col in trained_features:
    if col not in new_data_processed.columns:
        new_data_processed[col] = 0

# If the CSV has extra columns the model doesn’t need, that’s okay; we’ll just select what the model wants
X_new = new_data_processed[trained_features]

# 6. Make predictions
print("Making predictions...")
predictions = model.predict(X_new)
new_data['predicted_vulnerability'] = predictions

# 7. Identify high-risk rows
high_risk_vulnerabilities = new_data[new_data['predicted_vulnerability'] == 1]
print("High-Risk Vulnerabilities Detected:")
print(high_risk_vulnerabilities)

# 8. (Optional) Save the results to a new CSV
output_csv = r"C:\Users\Ait\Desktop\AI_Testing_Results.csv"
new_data.to_csv(output_csv, index=False)
print(f"Results saved to {output_csv}")
