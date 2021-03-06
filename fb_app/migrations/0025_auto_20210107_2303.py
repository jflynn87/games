# Generated by Django 3.1 on 2021-01-07 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0024_auto_20210107_2251'),
    ]

    operations = [
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_one_passing',
            new_name='away_passing',
        ),
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_one_receiver',
            new_name='away_receiver',
        ),
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_one_runner',
            new_name='away_runner',
        ),
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_two_passing',
            new_name='home_passing',
        ),
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_two_receiver',
            new_name='home_receiver',
        ),
        migrations.RenameField(
            model_name='playoffscores',
            old_name='team_two_runner',
            new_name='home_runner',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_one_passing',
            new_name='away_passing',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_one_receiver',
            new_name='away_receiver',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_one_runner',
            new_name='away_runner',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_two_passing',
            new_name='home_passing',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_two_receiver',
            new_name='home_receiver',
        ),
        migrations.RenameField(
            model_name='playoffstats',
            old_name='team_two_runner',
            new_name='home_runner',
        ),
    ]
