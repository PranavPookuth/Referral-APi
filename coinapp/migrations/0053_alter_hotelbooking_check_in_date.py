# Generated by Django 5.1.1 on 2024-11-12 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0052_remove_roomavailability_room_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotelbooking',
            name='check_in_date',
            field=models.DateField(),
        ),
    ]
