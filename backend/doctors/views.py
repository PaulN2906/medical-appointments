from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import PermissionDenied
from .models import Doctor, Schedule
from .serializers import DoctorSerializer, ScheduleSerializer
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

logger = logging.getLogger(__name__)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Doctor.objects.all()
        if hasattr(user, "doctor"):
            return Doctor.objects.filter(pk=user.doctor.pk)
        return Doctor.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        logger.debug("User autenticat: %s", request.user)
        return super().list(request, *args, **kwargs)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Schedule.objects.all()
        if hasattr(user, "doctor"):
            return Schedule.objects.filter(doctor=user.doctor)
        return Schedule.objects.none()
    
    # @method_decorator(cache_page(60*5))  # Cache pentru 5 minute, dezactivat momentan
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "doctor"):
            raise PermissionDenied("Only doctors can create schedules.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=user.doctor)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request, *args, **kwargs):
        """Create multiple schedules in a single transaction"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_bulk_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor"):
            raise PermissionDenied("Only doctors can create schedules.")

        serializer.save(doctor=user.doctor)
