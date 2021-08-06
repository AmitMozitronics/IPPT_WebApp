# Generated by Django 3.0.2 on 2020-02-10 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200126_0735'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftDataSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift', models.CharField(default='1', max_length=1)),
                ('shift_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='pipedata',
            name='shift',
            field=models.CharField(default='1', max_length=1),
        ),
    ]
