from rest_framework.permissions import BasePermission

class IsAdminGroupUser(BasePermission):

    """
    Permiso que permite el acceso solo a usuarios que pertenecen al grupo 'admin'
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_autehnticated and request.user.groups.filter(name='admin').exists()