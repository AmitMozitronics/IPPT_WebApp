# Generated by Django 3.0.4 on 2021-01-04 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_machine_machine_total_shift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='machine_total_shift',
            field=models.IntegerField(),
        ),
    ]