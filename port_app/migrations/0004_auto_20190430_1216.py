# Generated by Django 2.0.4 on 2019-04-30 03:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('port_app', '0003_auto_20190429_2322'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCY',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='position',
            name='ccy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port_app.CCY'),
        ),
    ]
