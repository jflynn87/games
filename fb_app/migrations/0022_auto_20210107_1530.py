# Generated by Django 3.1 on 2021-01-07 06:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0021_playoffscores_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playoffscores',
            name='data',
        ),
        migrations.RemoveField(
            model_name='playoffstats',
            name='picks',
        ),
        migrations.AddField(
            model_name='playoffstats',
            name='data',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='playoffstats',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fb_app.games'),
        ),
    ]
