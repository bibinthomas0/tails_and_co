# Generated by Django 4.2.2 on 2023-08-03 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='payment',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]