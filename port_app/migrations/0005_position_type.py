# Generated by Django 2.0.4 on 2019-05-03 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('port_app', '0004_auto_20190430_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='type',
            field=models.CharField(choices=[(1, 'Public'), (2, 'Private')], default=1, max_length=50),
            preserve_default=False,
        ),
    ]
