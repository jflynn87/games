# Generated by Django 2.0.4 on 2020-02-01 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0029_auto_20200119_1844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pgawebscores',
            old_name='score',
            new_name='rank',
        ),
        migrations.RenameField(
            model_name='pgawebscores',
            old_name='status',
            new_name='round_score',
        ),
        migrations.RenameField(
            model_name='pgawebscores',
            old_name='total',
            new_name='thru',
        ),
        migrations.AddField(
            model_name='pgawebscores',
            name='change',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='pgawebscores',
            name='total_score',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
