# Generated by Django 3.2.2 on 2021-08-22 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0075_countrypicks_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusdetails',
            name='bonus_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bonusdetails',
            name='bonus_type',
            field=models.CharField(choices=[('1', 'winning golfer'), ('2', 'no cuts'), ('3', 'weekly winner'), ('4', 'playoff'), ('5', 'best in group'), ('6', 'trifecta'), ('7', 'manual')], max_length=100, null=True),
        ),
    ]
