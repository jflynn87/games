# Generated by Django 4.0 on 2022-09-08 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0035_seasonpicks'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='email_picks',
            field=models.BooleanField(default=False),
        ),
    ]