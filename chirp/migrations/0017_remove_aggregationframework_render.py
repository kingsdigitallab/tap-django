# Generated by Django 2.0.2 on 2018-02-23 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0016_add_javascript_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aggregationframework',
            name='render',
        ),
    ]
