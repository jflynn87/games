# Generated by Django 3.1.7 on 2021-04-21 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0063_auto_20210421_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='partner_owgr',
            field=models.IntegerField(null=True),
        ),
    ]
