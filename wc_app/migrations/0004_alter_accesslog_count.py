# Generated by Django 4.0 on 2022-11-19 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wc_app', '0003_totalscore_accesslog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesslog',
            name='count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
