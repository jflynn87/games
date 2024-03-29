# Generated by Django 3.2.2 on 2021-05-27 06:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('golf_app', '0067_field_season_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='auction',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='AuctionPick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', models.CharField(blank=True, max_length=100, null=True)),
                ('score', models.PositiveBigIntegerField(default=0)),
                ('piayerName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='golf_app.field')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
