# Generated by Django 3.0.7 on 2020-08-09 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0040_field_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='rank',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
