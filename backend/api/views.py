# backend/api/views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Invoice
from .serializers import InvoiceSerializer
from .services import PredictionService

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class PredictionView(APIView):
    def get(self, request, invoice_id):
        prediction = PredictionService.generate_prediction(invoice_id)
        return Response(prediction)