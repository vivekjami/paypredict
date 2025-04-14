# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, PredictionView

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('predictions/<uuid:invoice_id>/', PredictionView.as_view(), name='prediction'),
]