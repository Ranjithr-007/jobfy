# Generated by Django 3.2.5 on 2021-08-07 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
