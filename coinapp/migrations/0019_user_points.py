# Generated by Django 5.1.1 on 2024-11-08 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0018_remove_referralpoints_referred_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
