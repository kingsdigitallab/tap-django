# Generated by Django 2.0.2 on 2018-02-23 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0017_remove_aggregationframework_render'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aggregation',
            name='pipeline_js',
        ),
    ]
