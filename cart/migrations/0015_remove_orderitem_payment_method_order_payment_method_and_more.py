# Generated by Django 4.2.2 on 2023-08-13 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0014_rename_payment_orderitem_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='payment_status',
            field=models.CharField(choices=[('P', 'Pending'), ('S', 'Recieved')], default='P', max_length=1),
        ),
    ]
