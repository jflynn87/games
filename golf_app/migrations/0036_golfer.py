# Generated by Django 3.0.3 on 2020-03-11 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0035_auto_20200303_2256'),
    ]

    operations = [
        migrations.CreateModel(
            name='Golfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('golfer_pga_num', models.CharField(max_length=100)),
                ('golfer_name', models.CharField(max_length=100)),
                ('pic_link', models.CharField(blank=True, max_length=500, null=True)),
                ('flag_link', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]
