# Generated by Django 4.2.2 on 2023-08-13 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_remove_orderitem_payment_method_order_payment_method_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_applied',
            field=models.CharField(blank=True, null=True),
        ),
    ]