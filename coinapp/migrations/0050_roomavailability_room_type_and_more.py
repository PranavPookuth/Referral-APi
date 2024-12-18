# Generated by Django 5.1.1 on 2024-11-12 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0049_hotelbooking_check_in_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomavailability',
            name='room_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='coinapp.roomtype'),
        ),
        migrations.AlterField(
            model_name='roomavailability',
            name='available_rooms',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='roomavailability',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coinapp.hotel'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='available_rooms',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_types_list', to='coinapp.hotel'),
        ),
    ]
