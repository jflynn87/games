# Generated by Django 2.0.4 on 2019-04-29 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('port_app', '0002_position'),
    ]

    operations = [
        migrations.RenameField(
            model_name='position',
            old_name='close_dat',
            new_name='close_date',
        ),
    ]
