# Generated by Django 2.0.4 on 2019-04-24 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0015_field_teamid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='teamID',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
