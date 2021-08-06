# Generated by Django 3.0.4 on 2021-03-08 14:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_machine_machine_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipedataprocessed',
            name='site_local_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]