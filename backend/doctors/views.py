from rest_framework import viewsets, permissions
from .models import Doctor, Schedule
from .serializers import DoctorSerializer, ScheduleSerializer
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        print("User autenticat:", request.user)
        return super().list(request, *args, **kwargs)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # @method_decorator(cache_page(60*5))  # Cache pentru 5 minute, dezactivat momentan
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Implementam logica de validare si creare cu tranzactii
        return super().create(request, *args, **kwargs)
