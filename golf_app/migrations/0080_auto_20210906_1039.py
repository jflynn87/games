# Generated by Django 3.1 on 2021-09-06 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0079_fedexseason_prior_season_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fedexseason',
            name='prior_season_data',
            field=models.JSONField(default=dict),
        ),
    ]