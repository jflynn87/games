# Generated by Django 3.2.2 on 2021-06-05 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0069_rename_piayername_auctionpick_playername'),
    ]

    operations = [
        migrations.AddField(
            model_name='golfer',
            name='results',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
