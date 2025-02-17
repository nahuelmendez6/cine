from rest_framework.permissions import BasePermission

class IsAdminGroupUser(BasePermission):
    """
    Permiso que permite acceso solo a usuarios administradores.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
