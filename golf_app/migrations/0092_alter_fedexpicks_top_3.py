# Generated by Django 4.0 on 2022-09-12 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0091_fedexpicks_top_3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fedexpicks',
            name='top_3',
            field=models.BooleanField(default=False, null=True),
        ),
    ]