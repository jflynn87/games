# Generated by Django 4.0 on 2022-11-06 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wc_app', '0004_team_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='picks',
            name='rank',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='picks',
            name='stage',
            field=models.CharField(choices=[('1', 'Group'), ('2', 'Knock-out')], default=None, max_length=100),
            preserve_default=False,
        ),
    ]
