# Generated by Django 3.1 on 2021-01-02 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0016_pickperformance'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayoffPicks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rushing_yards', models.PositiveIntegerField()),
                ('passing_yards', models.PositiveIntegerField()),
                ('total_points_scored', models.PositiveIntegerField()),
                ('points_on_fg', models.PositiveIntegerField()),
                ('takeaways', models.PositiveIntegerField()),
                ('sacks', models.PositiveIntegerField()),
                ('def_special_teams_tds', models.PositiveIntegerField()),
                ('team_one_runner', models.PositiveIntegerField()),
                ('team_one_receiver', models.PositiveIntegerField()),
                ('team_one_passing', models.PositiveIntegerField()),
                ('team_two_runner', models.PositiveIntegerField()),
                ('team_two_receiver', models.PositiveIntegerField()),
                ('team_two_passing', models.PositiveIntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.games')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.player')),
                ('winning_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.teams')),
            ],
        ),
    ]
