# Generated by Django 3.1 on 2021-02-18 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0060_tournament_ignore_name_mismatch'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoredict',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
