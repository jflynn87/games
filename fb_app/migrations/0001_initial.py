# Generated by Django 2.0.4 on 2019-03-03 12:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Games',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eid', models.CharField(max_length=30)),
                ('opening', models.CharField(max_length=10, null=True)),
                ('spread', models.CharField(max_length=10, null=True)),
                ('final', models.BooleanField(default=False)),
                ('home_score', models.PositiveIntegerField(null=True)),
                ('away_score', models.PositiveIntegerField(null=True)),
                ('qtr', models.CharField(max_length=5, null=True)),
                ('tie', models.BooleanField(default=False)),
                ('date', models.DateField(null=True)),
                ('time', models.CharField(max_length=20, null=True)),
                ('day', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='MikeScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Picks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pick_num', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.League')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mike_abbr', models.CharField(max_length=4, null=True)),
                ('nfl_abbr', models.CharField(max_length=4, null=True)),
                ('long_name', models.CharField(max_length=30, null=True)),
                ('typo_name', models.CharField(blank=True, max_length=30, null=True)),
                ('typo_name1', models.CharField(blank=True, max_length=30, null=True)),
                ('wins', models.PositiveIntegerField(default=0)),
                ('losses', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('nfl_abbr',),
            },
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(max_length=30)),
                ('week', models.PositiveIntegerField()),
                ('game_cnt', models.PositiveIntegerField()),
                ('current', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WeekScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(null=True)),
                ('projected_score', models.PositiveIntegerField(null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Player')),
                ('week', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Week')),
            ],
        ),
        migrations.AddField(
            model_name='picks',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='fb_app.Player'),
        ),
        migrations.AddField(
            model_name='picks',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picksteam', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='picks',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Week'),
        ),
        migrations.AddField(
            model_name='mikescore',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Player'),
        ),
        migrations.AddField(
            model_name='mikescore',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Week'),
        ),
        migrations.AddField(
            model_name='games',
            name='away',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='games',
            name='dog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dog', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='games',
            name='fav',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fav', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='games',
            name='home',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='games',
            name='loser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='loser', to='fb_app.Teams'),
        ),
        migrations.AddField(
            model_name='games',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_app.Week'),
        ),
        migrations.AddField(
            model_name='games',
            name='winner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='winner', to='fb_app.Teams'),
        ),
        migrations.AlterIndexTogether(
            name='picks',
            index_together={('week', 'player')},
        ),
        migrations.AlterIndexTogether(
            name='games',
            index_together={('week', 'home', 'away')},
        ),
    ]
