# Generated by Django 2.0.4 on 2020-02-01 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0031_auto_20200201_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoredetails',
            name='sod_position',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
