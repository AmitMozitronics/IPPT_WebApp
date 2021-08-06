# Generated by Django 3.0.2 on 2020-03-19 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_machinestatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetarialIssueShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift_date', models.CharField(max_length=8, unique=True)),
                ('shift_1', models.CharField(blank=True, max_length=30, null=True)),
                ('shift_2', models.CharField(blank=True, max_length=30, null=True)),
                ('shift_3', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
    ]
