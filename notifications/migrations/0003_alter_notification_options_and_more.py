# Generated by Django 5.1.6 on 2025-03-19 18:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-sent_at']},
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('SYSTEM', 'System Notification'), ('BOOKING', 'Booking Notification'), ('REMINDER', 'Reminder'), ('PROMO', 'Promotional')], default='SYSTEM', max_length=20),
        ),
        migrations.AddField(
            model_name='notification',
            name='read_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('UNREAD', 'Not read'), ('READ', 'Read'), ('ARCHIVED', 'Archived')], default='UNREAD', max_length=20),
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='Default Title', max_length=200),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['-sent_at'], name='notificatio_sent_at_789d15_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['status'], name='notificatio_status_d92267_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user'], name='notificatio_user_id_c291d5_idx'),
        ),
    ]
