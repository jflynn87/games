# Generated by Django 3.1 on 2021-03-02 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0061_scoredict_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='espn_t_num',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]