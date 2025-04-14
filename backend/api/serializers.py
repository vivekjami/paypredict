from rest_framework import serializers
from .models import Customer, Invoice, Prediction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'credit_score']

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['payment_probability', 'expected_date', 'risk_level']

class InvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    prediction = PredictionSerializer(allow_null=True)

    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'amount', 'due_date', 'status', 'created_at', 'prediction']