# Generated by Django 3.0.2 on 2020-03-24 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200324_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='_user_friends_+', to='users.User'),
        ),
    ]