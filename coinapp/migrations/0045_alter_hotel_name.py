# Generated by Django 5.1.1 on 2024-11-11 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0044_alter_hotel_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]