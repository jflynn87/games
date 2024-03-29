# Generated by Django 3.1 on 2021-07-27 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('golf_app', '0073_statlinks'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryPicks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=30)),
                ('score', models.PositiveBigIntegerField(default=0)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='golf_app.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
