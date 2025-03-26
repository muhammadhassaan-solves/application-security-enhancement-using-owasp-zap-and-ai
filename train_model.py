import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib
from imblearn.over_sampling import SMOTE

# Load the CSV data
data = pd.read_csv('C:\\Users\\Ait\\Desktop\\combined_zap_results.csv')
print("CSV Columns:", data.columns.tolist())

# Convert 'riskcode' to numeric severity
data['severity_numeric'] = data['riskcode'].astype(int)

# One-hot encode the 'alert' (vulnerability type) and 'site' (affected URL) columns
data_encoded = pd.get_dummies(data, columns=['alert', 'site'])

# Define features and target
# Drop extra columns not used in training
columns_to_drop = ['riskcode', 'vulnerability_detected', 'riskdesc', 'confidence', 'count']
X = data_encoded.drop(columns=columns_to_drop)
y = data_encoded['vulnerability_detected']

# Split data into training and test sets (70% train, 30% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Augment training data with SMOTE to balance classes
sm = SMOTE(random_state=42)
X_train_aug, y_train_aug = sm.fit_resample(X_train, y_train)

print("Class distribution before augmentation:")
print(y_train.value_counts())
print("Class distribution after augmentation:")
print(pd.Series(y_train_aug).value_counts())

# Optionally, add a small amount of random noise (jitter) to training features to simulate more variability
jitter = 0.001  # Adjust as needed
X_train_aug += np.random.normal(0, jitter, X_train_aug.shape)

# Train a Logistic Regression model with stronger L2 regularization (lower C value)
model = LogisticRegression(penalty='l2', solver='liblinear', random_state=42, C=0.01)
model.fit(X_train_aug, y_train_aug)

# Evaluate the model on the test set
predictions = model.predict(X_test)
test_accuracy = accuracy_score(y_test, predictions)
print(f"Test Set Accuracy: {test_accuracy}")

# Confusion Matrix
cm = confusion_matrix(y_test, predictions)
print("Confusion Matrix:\n", cm)

# 5-fold Cross-validation
cv_scores = cross_val_score(model, X, y, cv=5)
print("Cross-Validation Scores:", cv_scores)
print("Mean CV Accuracy:", cv_scores.mean())

# Save the trained model
joblib.dump(model, 'C:\\Users\\Ait\\Desktop\\vulnerability_prediction_model.pkl')
print("Logistic Regression model saved as vulnerability_prediction_model.pkl")
