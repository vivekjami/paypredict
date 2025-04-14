from celery import shared_task
from django.core.mail import send_mail
from .models import Invoice, Prediction

@shared_task
def send_payment_reminder(invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    prediction = Prediction.objects.filter(invoice=invoice).first()
    if invoice.status == 'pending' and prediction and prediction.risk_level == 'high':
        subject = f'Payment Reminder: Invoice {invoice.id}'
        message = (
            f"Dear {invoice.customer.name},\n\n"
            f"Your invoice for ${invoice.amount} is due on {invoice.due_date}.\n"
            f"Our system predicts a {prediction.payment_probability*100:.1f}% chance of late payment.\n"
            f"Please ensure timely payment.\n\n"
            f"Best regards,\nPayPredict Team"
        )
        send_mail(
            subject,
            message,
            'from@paypredict.com',
            [invoice.customer.email],
            fail_silently=False,
        )