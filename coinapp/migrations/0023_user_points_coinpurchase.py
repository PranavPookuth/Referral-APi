# Generated by Django 5.1.1 on 2024-11-08 08:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0022_remove_user_points_delete_coinpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='CoinPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_coins', models.PositiveIntegerField(default=1)),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
                ('points_awarded_to_referrer', models.IntegerField(default=0)),
                ('referred_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals_earning_points', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coin_purchases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
