# Generated by Django 5.1.1 on 2024-11-09 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0037_rename_user_hotelbooking_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotelbooking',
            name='booking_date',
            field=models.DateTimeField(),
        ),
    ]
