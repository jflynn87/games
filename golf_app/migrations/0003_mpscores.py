# Generated by Django 2.0.4 on 2019-03-28 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0002_field_withdrawn'),
    ]

    operations = [
        migrations.CreateModel(
            name='mpScores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bracket', models.CharField(max_length=5)),
                ('round', models.PositiveIntegerField()),
                ('match_num', models.CharField(max_length=5)),
                ('result', models.CharField(max_length=10)),
                ('score', models.CharField(max_length=10)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='golf_app.Field')),
            ],
        ),
    ]
