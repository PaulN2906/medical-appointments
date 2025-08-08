from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register the viewset at the root of this router so that the final API path
# becomes a simple `/api/appointments/`.
router.register(r'', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
