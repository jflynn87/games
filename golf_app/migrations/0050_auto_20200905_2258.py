# Generated by Django 3.1 on 2020-09-05 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0049_auto_20200903_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusdetails',
            name='best_in_group_bonus',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bonusdetails',
            name='playoff_bonus',
            field=models.BigIntegerField(default=0),
        ),
    ]
