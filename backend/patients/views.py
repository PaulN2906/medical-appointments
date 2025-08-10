from rest_framework import viewsets, permissions
from .models import Patient
from .serializers import PatientSerializer
from authentication.permissions import IsAdminRole

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admin can see all patients
        if IsAdminRole().has_permission(self.request, self):
            return Patient.objects.all().select_related('user')

        if user.is_staff or user.is_superuser:
            return Patient.objects.all()
        
        if hasattr(user, "doctor"):
            return Patient.objects.filter(appointments__doctor=user.doctor).distinct()
        
        if hasattr(user, "patient"):
            return Patient.objects.filter(pk=user.patient.pk)
        
        return Patient.objects.none()
