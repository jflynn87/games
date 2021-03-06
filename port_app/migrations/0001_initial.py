# Generated by Django 2.0.4 on 2019-04-18 04:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MarketData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=200)),
                ('ccy', models.CharField(max_length=10)),
                ('date_time', models.DateTimeField()),
                ('type', models.CharField(max_length=100)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('total_pos', models.IntegerField()),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port_app.MarketData')),
            ],
        ),
    ]
