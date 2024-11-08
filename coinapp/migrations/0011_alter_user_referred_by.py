# Generated by Django 5.1.1 on 2024-11-08 05:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0010_user_referred_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referrals_by', to=settings.AUTH_USER_MODEL),
        ),
    ]