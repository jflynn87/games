# Generated by Django 2.0.4 on 2019-04-03 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0011_auto_20190401_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoredetails',
            name='toPar',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='scoredetails',
            name='today_score',
            field=models.CharField(max_length=50, null=True),
        ),
    ]