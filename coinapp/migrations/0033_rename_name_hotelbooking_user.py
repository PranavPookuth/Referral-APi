# Generated by Django 5.1.1 on 2024-11-09 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0032_rename_price_per_night_hotel_price_per'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hotelbooking',
            old_name='name',
            new_name='user',
        ),
    ]
