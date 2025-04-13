from rest_framework import serializers
from .models import Invoice, Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'credit_score']

class InvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.UUIDField(write_only=True)
    amount = serializers.FloatField()  # Ensure amount is serialized as a number

    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'customer_id', 'amount', 'due_date', 'status', 'created_at']