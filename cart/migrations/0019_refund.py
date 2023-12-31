# Generated by Django 4.2.2 on 2023-08-19 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0018_wallet_wallethistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refund_amount', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('S', 'Recieved')], default='P', max_length=1)),
                ('orderitem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.orderitem')),
            ],
        ),
    ]
