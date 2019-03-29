# Generated by Django 2.0.4 on 2019-03-28 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0003_mpscores'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpscores',
            name='pick',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='golf_app.Picks'),
        ),
        migrations.RemoveField(
            model_name='mpscores',
            name='player',
        ),
        migrations.AlterUniqueTogether(
            name='mpscores',
            unique_together={('pick', 'round')},
        ),
    ]
