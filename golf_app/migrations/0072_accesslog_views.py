# Generated by Django 3.2.2 on 2021-06-19 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0071_auto_20210617_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='views',
            field=models.PositiveBigIntegerField(default=0, null=True),
        ),
    ]