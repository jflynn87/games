# Generated by Django 2.0.4 on 2019-08-17 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0004_season_current'),
    ]

    operations = [
        migrations.AddField(
            model_name='teams',
            name='pic',
            field=models.URLField(null=True),
        ),
    ]
