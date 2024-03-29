# Generated by Django 3.2.2 on 2021-06-17 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0070_golfer_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='device_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='golf_app.tournament'),
        ),
    ]
