# Generated by Django 3.1 on 2021-02-04 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0029_auto_20210112_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playoffpicks',
            name='away_passer_rating',
            field=models.FloatField(default=100.0),
        ),
        migrations.AlterField(
            model_name='playoffpicks',
            name='home_passer_rating',
            field=models.FloatField(default=100.0),
        ),
    ]
