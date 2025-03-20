from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationsView,
    MarkNotificationReadView,
    MarkAllReadView,
    ArchiveNotificationsView
)

app_name = 'notifications'

urlpatterns = [
    # Listar todas las notificaciones (con opción de incluir archivadas)
    path('list/', NotificationListView.as_view(), name='notification-list'),
    
    # Listar notificaciones no leídas
    path('unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    
    # Marcar una notificación específica como leída
    path('<int:notification_id>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
    
    # Marcar todas las notificaciones como leídas
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    
    # Archivar múltiples notificaciones
    path('archive/', ArchiveNotificationsView.as_view(), name='archive-notifications'),
] 