# Generated by Django 5.1.1 on 2024-11-07 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0003_remove_user_road_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, max_length=36, null=True, unique=True),
        ),
    ]
