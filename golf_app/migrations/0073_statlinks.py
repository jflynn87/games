# Generated by Django 3.2.2 on 2021-07-21 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0072_accesslog_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatLinks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('link', models.URLField()),
            ],
        ),
    ]