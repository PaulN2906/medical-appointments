from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'doctors', views.DoctorViewSet)
router.register(r'schedules', views.ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'schedules/bulk_create/',
        views.ScheduleViewSet.as_view({'post': 'bulk_create'}),
        name='schedule-bulk-create',
    ),
]
