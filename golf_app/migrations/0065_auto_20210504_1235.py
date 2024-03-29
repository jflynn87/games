# Generated by Django 3.1.7 on 2021-05-04 03:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('golf_app', '0064_field_partner_owgr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='map_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='field',
            name='partner_golfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='partner_golfer', to='golf_app.golfer'),
        ),
        migrations.AlterField(
            model_name='field',
            name='partner_owgr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='field',
            name='pic_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='field',
            name='rank',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
