# Generated by Django 3.1 on 2021-01-19 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0056_golfer_cbs_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='golfer',
            old_name='cbs_number',
            new_name='espn_number',
        ),
    ]