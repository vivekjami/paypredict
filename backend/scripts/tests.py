import joblib
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
import datetime
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

# Parameters
N_customers = 1000
M_invoices_per_customer = 10
p_late = 0.4
mu_D = np.log(14)  # For delay, mean 14 for calculation, adjusted
sigma_D = 0.5
mu_amount = np.log(1000) - (0.6)**2 / 2  # Adjust for mean $1000, std ≈ 478
sigma_amount = 0.6
mean_credit_score = 650
std_credit_score = 100
low_credit_score = 300
high_credit_score = 850
start_date = '2024-01-01'
end_date = '2024-12-31'

# Generate customers
a, b = (low_credit_score - mean_credit_score) / std_credit_score, (high_credit_score - mean_credit_score) / std_credit_score
credit_scores = truncnorm.rvs(a, b, loc=mean_credit_score, scale=std_credit_score, size=N_customers)
customers_df = pd.DataFrame({
    'customer_id': range(1, N_customers+1),
    'credit_score': credit_scores
})

# Generate invoices
invoices_list = []
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date)
for idx, row in customers_df.iterrows():
    customer_id = row['customer_id']
    credit_score = row['credit_score']
    for i in range(M_invoices_per_customer):
        random_prop = np.random.random()
        issue_date = start_dt + (end_dt - start_dt) * random_prop
        due_date = issue_date + pd.Timedelta(days=30)
        if np.random.rand() < p_late:
            D = np.random.lognormal(mean=mu_D, sigma=sigma_D)
            is_late = True
        else:
            D = 0
            is_late = False
        payment_date = due_date + pd.Timedelta(days=D)
        invoices_list.append({
            'customer_id': customer_id,
            'invoice_id': len(invoices_list)+1,
            'credit_score': credit_score,
            'amount': np.random.lognormal(mean=mu_amount, sigma=sigma_amount),
            'issue_date': issue_date,
            'due_date': due_date,
            'payment_date': payment_date,
            'is_late': is_late,
            'delay_days': D
        })

invoices_df = pd.DataFrame(invoices_list)
invoices_df.to_csv('synthetic_ar_data.csv', index=False)

# Train the model
X = invoices_df[['credit_score', 'amount']]
y = invoices_df['is_late']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initial model
initial_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', 
                          max_depth=3, learning_rate=0.3, n_estimators=100)
initial_model.fit(X_train, y_train)
y_pred = initial_model.predict(X_test)
print(f'Initial Accuracy: {accuracy_score(y_test, y_pred)}')
print(classification_report(y_test, y_pred))

# Hyperparameter tuning with Grid Search
param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.3],
    'n_estimators': [100, 300, 500],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}

grid_search = GridSearchCV(
    xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
    param_grid, cv=3, scoring='accuracy', n_jobs=-1
)
grid_search.fit(X_train, y_train)
print(f'Best parameters: {grid_search.best_params_}')

best_model = grid_search.best_estimator_
y_pred_tuned = best_model.predict(X_test)
print(f'Tuned Accuracy: {accuracy_score(y_test, y_pred_tuned)}')
print(classification_report(y_test, y_pred_tuned))

# Save the best model (trained on original features)
best_model_filename = 'payment_delay_model.pkl'
joblib.dump(best_model, best_model_filename)
print(f"Model saved to {best_model_filename}")

# Example prediction with the basic model
print("\nPrediction with basic model:")
new_data = np.array([[700, 1500]])  # credit_score, amount
prediction = best_model.predict(new_data)
prediction_proba = best_model.predict_proba(new_data)
print(f'Prediction: {"Late" if prediction[0] else "On Time"}')
print(f'Probability: {prediction_proba[0]}')

# OPTION 2: Train a separate model with polynomial features
print("\nTraining model with polynomial features:")

# Create polynomial features with feature names preserved
X_train_df = pd.DataFrame(X_train, columns=['credit_score', 'amount'])
X_test_df = pd.DataFrame(X_test, columns=['credit_score', 'amount'])

poly = PolynomialFeatures(degree=2, include_bias=False)
X_train_poly = poly.fit_transform(X_train_df)
X_test_poly = poly.transform(X_test_df)

# Get the feature names from polynomial transformation
poly_feature_names = poly.get_feature_names_out(['credit_score', 'amount'])
X_train_poly_df = pd.DataFrame(X_train_poly, columns=poly_feature_names)
X_test_poly_df = pd.DataFrame(X_test_poly, columns=poly_feature_names)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_poly_df)
X_test_scaled = scaler.transform(X_test_poly_df)

# Convert back to DataFrame to preserve feature names
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=poly_feature_names)
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=poly_feature_names)

# Train a new model with polynomial features
poly_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', 
                       max_depth=5, learning_rate=0.1, n_estimators=300)
poly_model.fit(X_train_scaled_df, y_train)

# Evaluate polynomial model
y_pred_poly = poly_model.predict(X_test_scaled_df)
print(f'Polynomial Features Accuracy: {accuracy_score(y_test, y_pred_poly)}')
print(classification_report(y_test, y_pred_poly))

# Save the polynomial model and preprocessing objects
poly_model_filename = 'payment_delay_poly_model.pkl'
poly_filename = 'polynomial_features.pkl'
scaler_filename = 'scaler.pkl'

joblib.dump(poly_model, poly_model_filename)
joblib.dump(poly, poly_filename)
joblib.dump(scaler, scaler_filename)

print(f"Polynomial model and preprocessors saved to {poly_model_filename}, {poly_filename}, and {scaler_filename}")

# Example prediction with the polynomial model
print("\nPrediction with polynomial model:")
# Create a proper DataFrame for the new data to avoid feature name warnings
new_data_df = pd.DataFrame([[700, 1500]], columns=['credit_score', 'amount'])

# Transform and predict using the same preprocessing pipeline
new_data_poly = poly.transform(new_data_df)
new_data_poly_df = pd.DataFrame(new_data_poly, columns=poly_feature_names)
new_data_scaled = scaler.transform(new_data_poly_df)
new_data_scaled_df = pd.DataFrame(new_data_scaled, columns=poly_feature_names)

poly_prediction = poly_model.predict(new_data_scaled_df)
poly_prediction_proba = poly_model.predict_proba(new_data_scaled_df)

print(f'Polynomial Prediction: {"Late" if poly_prediction[0] else "On Time"}')
print(f'Polynomial Probability: {poly_prediction_proba[0]}')

# DEMO: Loading and using the models
print("\nDemo: Loading and using saved models:")

# Load basic model
loaded_model = joblib.load(best_model_filename)
# Make prediction with basic model
basic_pred = loaded_model.predict(new_data_df)
print(f"Basic model prediction: {'Late' if basic_pred[0] else 'On Time'}")

# Load polynomial model and preprocessors
loaded_poly = joblib.load(poly_filename)
loaded_scaler = joblib.load(scaler_filename)
loaded_poly_model = joblib.load(poly_model_filename)

# Use the correct preprocessing pipeline
new_data_df = pd.DataFrame([[700, 1500]], columns=['credit_score', 'amount'])
poly_feat_names = loaded_poly.get_feature_names_out(['credit_score', 'amount'])

# Transform new data properly preserving feature names
new_data_transformed = loaded_poly.transform(new_data_df)
new_data_transformed_df = pd.DataFrame(new_data_transformed, columns=poly_feat_names)
new_data_scaled = loaded_scaler.transform(new_data_transformed_df)
new_data_scaled_df = pd.DataFrame(new_data_scaled, columns=poly_feat_names)

# Make prediction with polynomial model
poly_pred = loaded_poly_model.predict(new_data_scaled_df)
print(f"Polynomial model prediction: {'Late' if poly_pred[0] else 'On Time'}")