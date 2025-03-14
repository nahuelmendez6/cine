from django.db import models

from users.models import CustomUser


# Create your models here.
class Notification(models.Model):
    class NotificationType(models.TextChoices):
        SYSTEM = 'SYSTEM', 'System Notification'
        BOOKING = 'BOOKING', 'Booking Notification'
        REMINDER = 'REMINDER', 'Reminder'
        PROMO = 'PROMO', 'Promotional'

    class NotificationStatus(models.TextChoices):
        UNREAD = 'UNREAD', 'Not read'
        READ = 'READ', 'Read'
        ARCHIVED = 'ARCHIVED', 'Archived'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.UNREAD
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.title} ({self.status})"

    def mark_as_read(self):
        from django.utils import timezone
        if self.status == self.NotificationStatus.UNREAD:
            self.status = self.NotificationStatus.READ
            self.read_at = timezone.now()
            self.save()

    def archive(self):
        self.status = self.NotificationStatus.ARCHIVED
        self.save()