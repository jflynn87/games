# Generated by Django 2.0.4 on 2019-06-10 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0020_auto_20190524_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='playerID',
            field=models.CharField(max_length=100, null=True),
        ),
    ]