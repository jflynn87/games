# Generated by Django 4.0 on 2022-08-24 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0033_accesslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='regular_week',
            field=models.BooleanField(default=False),
        ),
    ]