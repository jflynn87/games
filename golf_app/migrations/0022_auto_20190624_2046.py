# Generated by Django 2.0.4 on 2019-06-24 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0021_field_playerid'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='map_link',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='field',
            name='pic_link',
            field=models.URLField(null=True),
        ),
    ]