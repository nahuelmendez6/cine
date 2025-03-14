from django.db.models import Q
from django.utils import timezone
from .models import Notification


class NotificationService:
    @staticmethod
    def create_notification(user, title, message, notification_type=Notification.NotificationType.SYSTEM):
        """
        Create a new notification for a user
        """
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )

    @staticmethod
    def get_user_notifications(user, include_archived=False):
        """
        Get all notifications for a user
        """
        query = Q(user=user)
        if not include_archived:
            query &= ~Q(status=Notification.NotificationStatus.ARCHIVED)
        
        return Notification.objects.filter(query)

    @staticmethod
    def get_unread_notifications(user):
        """
        Get unread notifications for a user
        """
        return Notification.objects.filter(
            user=user,
            status=Notification.NotificationStatus.UNREAD
        )

    @staticmethod
    def mark_all_as_read(user):
        """
        Mark all unread notifications as read for a user
        """
        now = timezone.now()
        return Notification.objects.filter(
            user=user,
            status=Notification.NotificationStatus.UNREAD
        ).update(
            status=Notification.NotificationStatus.READ,
            read_at=now
        )

    @staticmethod
    def bulk_archive_notifications(user, notification_ids):
        """
        Archive multiple notifications at once
        """
        return Notification.objects.filter(
            user=user,
            id__in=notification_ids
        ).update(status=Notification.NotificationStatus.ARCHIVED)

    @staticmethod
    def delete_old_notifications(days=30):
        """
        Delete notifications older than specified days
        """
        threshold_date = timezone.now() - timezone.timedelta(days=days)
        return Notification.objects.filter(
            sent_at__lt=threshold_date,
            status=Notification.NotificationStatus.ARCHIVED
        ).delete()
