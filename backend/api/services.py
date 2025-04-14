import joblib
import pandas as pd
from datetime import date
from uuid import UUID
from .models import Invoice, Prediction

class PredictionService:
    # Load model and preprocessors
    poly_model = joblib.load('models/payment_delay_poly_model.pkl')
    poly_features = joblib.load('models/polynomial_features.pkl')
    scaler = joblib.load('models/scaler.pkl')
    feature_names = poly_features.get_feature_names_out(['credit_score', 'amount'])

    @staticmethod
    def generate_prediction(invoice_id: UUID) -> dict:
        invoice = Invoice.objects.get(id=invoice_id)
        # Prepare input data
        input_data = pd.DataFrame(
            [[invoice.customer.credit_score, float(invoice.amount)]],
            columns=['credit_score', 'amount']
        )
        # Apply polynomial features and scaling
        poly_data = PredictionService.poly_features.transform(input_data)
        poly_data_df = pd.DataFrame(poly_data, columns=PredictionService.feature_names)
        scaled_data = PredictionService.scaler.transform(poly_data_df)
        scaled_data_df = pd.DataFrame(scaled_data, columns=PredictionService.feature_names)
        # Predict
        is_late = PredictionService.poly_model.predict(scaled_data_df)[0]
        probability = PredictionService.poly_model.predict_proba(scaled_data_df)[0]
        # Estimate expected date (heuristic: late payments add 10 days)
        expected_date = (
            invoice.due_date + pd.Timedelta(days=10)
            if is_late
            else invoice.due_date
        )
        risk_level = 'high' if is_late else 'low'
        # Save prediction
        prediction, _ = Prediction.objects.update_or_create(
            invoice=invoice,
            defaults={
                'payment_probability': float(probability[1]),  # Probability of late
                'expected_date': expected_date,
                'risk_level': risk_level
            }
        )
        return {
            'invoice_id': str(invoice_id),
            'payment_probability': prediction.payment_probability,
            'expected_date': prediction.expected_date.isoformat(),
            'risk_level': prediction.risk_level
        }