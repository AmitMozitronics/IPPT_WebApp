# Generated by Django 3.0.4 on 2021-02-25 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_auto_20210225_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='machine_version',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
