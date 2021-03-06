# Generated by Django 2.0.4 on 2019-08-12 02:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fb_app', '0002_auto_20190401_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='week',
            name='season',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='week',
            name='season_model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fb_app.Season'),
        ),
    ]
