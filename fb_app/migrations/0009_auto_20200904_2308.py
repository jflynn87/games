# Generated by Django 3.1 on 2020-09-04 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0008_league_ties_lose'),
    ]

    operations = [
        migrations.AlterField(
            model_name='week',
            name='game_cnt',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
