# Generated by Django 3.1 on 2021-09-06 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0078_auto_20210906_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='fedexseason',
            name='prior_season_data',
            field=models.JSONField(default={}),
        ),
    ]
