# Generated by Django 3.0.4 on 2020-11-11 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20201109_0739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='local_timezone',
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='b',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='c',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='count',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='d',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='e',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='mid',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='ps',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='site_time',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='ts',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='pipedata',
            name='weight',
            field=models.TextField(),
        ),
    ]
