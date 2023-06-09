# Generated by Django 4.1.7 on 2023-05-16 16:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('generalshop', '0002_order_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordered_products', to='generalshop.order'),
        ),
        migrations.AlterField(
            model_name='orderedproduct',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
