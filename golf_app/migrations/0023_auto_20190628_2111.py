# Generated by Django 2.0.4 on 2019-06-28 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0022_auto_20190624_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='sow_WGR',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='field',
            name='soy_WGR',
            field=models.IntegerField(null=True),
        ),
    ]