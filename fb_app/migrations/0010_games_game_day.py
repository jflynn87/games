# Generated by Django 3.1 on 2020-09-06 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0009_auto_20200904_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='games',
            name='game_day',
            field=models.DateTimeField(null=True),
        ),
    ]