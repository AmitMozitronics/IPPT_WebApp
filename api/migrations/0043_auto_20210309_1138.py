# Generated by Django 3.0.4 on 2021-03-09 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_auto_20210309_1135'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pipedataprocessed',
            unique_together={('machine_id', 'site_local_time')},
        ),
    ]
