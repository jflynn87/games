# Generated by Django 2.0.4 on 2020-02-01 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0030_auto_20200201_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgawebscores',
            name='change',
            field=models.CharField(max_length=100, null=True),
        ),
    ]