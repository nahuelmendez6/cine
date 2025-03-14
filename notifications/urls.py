from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('unread/', views.UnreadNotificationsView.as_view(), name='unread_notifications'),
    path('<int:notification_id>/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('archive/', views.ArchiveNotificationsView.as_view(), name='archive_notifications'),
] 