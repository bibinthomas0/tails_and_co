# Generated by Django 4.2.3 on 2023-09-04 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0036_alter_order_coin_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='coin_discount',
            field=models.IntegerField(default=0),
        ),
    ]
