# Generated by Django 2.0.4 on 2020-01-19 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0028_auto_20200119_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cut_score',
            field=models.CharField(max_length=100, null=True),
        ),
    ]