# Generated by Django 2.0.2 on 2018-02-23 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0021_rename_field_query_on_mapreduce_to_query_js'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aggregationframework',
            name='render_js',
        ),
    ]