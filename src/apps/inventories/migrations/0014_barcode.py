# Generated by Django 3.0.11 on 2021-03-20 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20201008_2213'),
        ('inventories', '0013_auto_20201009_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='BarCode',
            fields=[
                ('quantity', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('id', models.CharField(max_length=13, primary_key=True, serialize=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.Product')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Unit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]