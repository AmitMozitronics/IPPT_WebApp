# Generated by Django 3.0.4 on 2020-03-31 06:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_metarialissueshift'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeshiftduration',
            name='shift_1_downtime',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='pipeshiftduration',
            name='shift_2_downtime',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='pipeshiftduration',
            name='shift_3_downtime',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AlterField(
            model_name='metarialissueshift',
            name='shift_1',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metarialissueshift',
            name='shift_2',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metarialissueshift',
            name='shift_3',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metarialissueshift',
            name='shift_date',
            field=models.DateField(unique=True),
        ),
        migrations.AlterField(
            model_name='pipeshiftduration',
            name='shift_1',
            field=models.DurationField(default=datetime.timedelta(0, 28800)),
        ),
        migrations.AlterField(
            model_name='pipeshiftduration',
            name='shift_2',
            field=models.DurationField(default=datetime.timedelta(0, 28800)),
        ),
        migrations.AlterField(
            model_name='pipeshiftduration',
            name='shift_3',
            field=models.DurationField(default=datetime.timedelta(0, 28800)),
        ),
        migrations.AlterField(
            model_name='pipeshiftduration',
            name='shift_date',
            field=models.DateField(unique=True),
        ),
        migrations.CreateModel(
            name='PipeDataProcessed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_id', models.CharField(max_length=100)),
                ('basic_metarial', models.CharField(blank=True, max_length=100, null=True)),
                ('standard_type_classification', models.CharField(blank=True, max_length=100, null=True)),
                ('pressure_type_specification', models.CharField(blank=True, max_length=100, null=True)),
                ('outer_diameter', models.IntegerField(blank=True, null=True)),
                ('outer_diameter_unit', models.CharField(blank=True, max_length=100, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('length_unit', models.CharField(blank=True, max_length=100, null=True)),
                ('timestamp', models.BigIntegerField()),
                ('count', models.IntegerField(blank=True, null=True)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('maxweight', models.IntegerField(blank=True, null=True)),
                ('minweight', models.IntegerField(blank=True, null=True)),
                ('weightgain', models.IntegerField(blank=True, null=True)),
                ('weightloss', models.IntegerField(blank=True, null=True)),
                ('pass_status', models.CharField(blank=True, max_length=100, null=True)),
                ('site_time', models.DateTimeField()),
                ('shift', models.CharField(max_length=1)),
            ],
            options={
                'ordering': ['-timestamp'],
                'unique_together': {('machine_id', 'timestamp')},
            },
        ),
    ]