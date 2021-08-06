# Generated by Django 3.0.4 on 2020-12-13 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_lastsearchtime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lastsearchtime',
            name='last_date_time',
        ),
        migrations.AddField(
            model_name='lastsearchtime',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lastsearchtime',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lastsearchtime',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lastsearchtime',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lastsearchtime',
            name='machine_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lastsearchtime',
            name='username',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
