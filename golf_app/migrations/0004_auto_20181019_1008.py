# Generated by Django 2.0.4 on 2018-10-19 01:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0003_auto_20181018_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='golf_app.Group'),
        ),
    ]
