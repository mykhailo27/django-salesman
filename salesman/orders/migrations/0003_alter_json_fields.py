# Generated by Django 4.0.3 on 2022-03-14 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesmanorders', '0002_alter_order_ref'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='_extra',
            field=models.JSONField(blank=True, default=dict, verbose_name='Extra'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='_extra',
            field=models.JSONField(blank=True, default=dict, verbose_name='Extra'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product_data',
            field=models.JSONField(blank=True, default=dict, verbose_name='Product data'),
        ),
    ]
