# Generated by Django 2.0.4 on 2019-01-19 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0005_auto_20190119_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoredetails',
            name='toPar',
            field=models.CharField(max_length=10, null=True),
        ),
    ]