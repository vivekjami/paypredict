from django.db import models
from uuid import uuid4

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    credit_score = models.IntegerField()

    def __str__(self):
        return self.name

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.name}"

class Prediction(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    payment_probability = models.FloatField()
    expected_date = models.DateField()
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('high', 'High')
    ])

    def __str__(self):
        return f"Prediction for Invoice {self.invoice.id}"