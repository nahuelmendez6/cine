from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .services import NotificationService


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user's notifications
        """
        include_archived = request.GET.get('include_archived', '').lower() == 'true'
        notifications = NotificationService.get_user_notifications(
            request.user,
            include_archived=include_archived
        ).values('id', 'title', 'message', 'notification_type', 'status', 'sent_at', 'read_at')
        
        return Response(list(notifications))


class UnreadNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user's unread notifications
        """
        notifications = NotificationService.get_unread_notifications(
            request.user
        ).values('id', 'title', 'message', 'notification_type', 'sent_at')
        
        return Response(list(notifications))


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        """
        Mark a specific notification as read
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.mark_as_read()
            return Response({'status': 'success'})
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Mark all notifications as read
        """
        NotificationService.mark_all_as_read(request.user)
        return Response({'status': 'success'})


class ArchiveNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Archive multiple notifications
        """
        notification_ids = request.data.get('notification_ids', [])
        if not notification_ids:
            return Response(
                {'error': 'No notification IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        NotificationService.bulk_archive_notifications(request.user, notification_ids)
        return Response({'status': 'success'})
