# Generated by Django 3.1 on 2020-10-11 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0054_tournament_saved_cut_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='saved_cut_round',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='saved_round',
            field=models.IntegerField(null=True),
        ),
    ]