# Generated by Django 5.1.6 on 2025-02-06 17:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_remove_function_function_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='function',
            name='function_time_end',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
    ]
