# Generated by Django 3.2.2 on 2021-05-27 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0068_auto_20210527_1531'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auctionpick',
            old_name='piayerName',
            new_name='playerName',
        ),
    ]
