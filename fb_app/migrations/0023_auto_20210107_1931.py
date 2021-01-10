# Generated by Django 3.1 on 2021-01-07 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0022_auto_20210107_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playoffstats',
            name='def_special_teams_tds',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='passing_yards',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='points_on_fg',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='rushing_yards',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='sacks',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='takeaways',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_one_passing',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_one_receiver',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_one_runner',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_two_passing',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_two_receiver',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='team_two_runner',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playoffstats',
            name='total_points_scored',
            field=models.IntegerField(null=True),
        ),
    ]