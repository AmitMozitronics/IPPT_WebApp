# Generated by Django 3.0.4 on 2020-12-23 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='MachineLocalServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_id', models.CharField(max_length=20, unique=True)),
                ('site_server', models.CharField(choices=[('local', 'LOCAL'), ('server', 'SERVER')], max_length=20)),
            ],
        ),
    ]