# Generated by Django 5.1.1 on 2024-11-08 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0006_referralcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
