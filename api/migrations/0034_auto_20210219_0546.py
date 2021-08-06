# Generated by Django 3.0.4 on 2021-02-19 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_code_standard_cml_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='machine_time_difference',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='machine_time_zone',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='machine_utc_difference',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='shift1_time_duration',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='shift2_time_duration',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='shift3_time_duration',
            field=models.FloatField(blank=True, null=True),
        ),
    ]