# Generated by Django 5.1.1 on 2024-11-13 09:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0055_remove_hotelbooking_check_out_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotelbooking',
            name='check_out_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
