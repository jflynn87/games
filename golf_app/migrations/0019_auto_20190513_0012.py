# Generated by Django 2.0.4 on 2019-05-12 15:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('golf_app', '0018_picks_auto'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bonusdetails',
            unique_together={('tournament', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='scoredetails',
            unique_together={('user', 'pick')},
        ),
    ]
