# Generated by Django 5.1.1 on 2024-11-12 07:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0048_hotelbooking_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotelbooking',
            name='check_in_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]