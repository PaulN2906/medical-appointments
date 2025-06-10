from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/regenerate_backup_codes/',
        views.UserViewSet.as_view({'post': 'regenerate_backup_codes'}),
        name='user-regenerate-backup-codes',
    ),
]
