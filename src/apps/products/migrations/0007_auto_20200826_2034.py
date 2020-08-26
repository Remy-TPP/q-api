# Generated by Django 3.0.9 on 2020-08-26 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_delete_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='avg_weight',
            field=models.DecimalField(decimal_places=5, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='density',
            field=models.DecimalField(decimal_places=5, max_digits=12, null=True),
        ),
    ]
