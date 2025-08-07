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
    # Admin user management endpoints
    path(
        'users/admin/all/',
        views.UserViewSet.as_view({'get': 'get_all_users_for_admin'}),
        name='admin-get-all-users',
    ),
    path(
        'users/<int:pk>/admin/update/',
        views.UserViewSet.as_view({'put': 'update_user_by_admin'}),
        name='admin-update-user',
    ),
    path(
        'users/<int:pk>/admin/reset-password/',
        views.UserViewSet.as_view({'post': 'reset_password_by_admin'}),
        name='admin-reset-password',
    ),
    path(
        'users/<int:pk>/admin/toggle-active/',
        views.UserViewSet.as_view({'post': 'deactivate_user'}),
        name='admin-toggle-user-active',
    ),
]
