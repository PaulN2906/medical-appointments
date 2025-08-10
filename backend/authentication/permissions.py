from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only to users with an admin profile role."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                getattr(user, 'is_staff', False) or
                getattr(user, 'is_superuser', False) or
                (hasattr(user, 'profile') and user.profile.role == 'admin')
            )
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
