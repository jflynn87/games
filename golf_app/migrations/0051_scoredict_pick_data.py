# Generated by Django 3.1 on 2020-09-12 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0050_auto_20200905_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoredict',
            name='pick_data',
            field=models.JSONField(null=True),
        ),
    ]