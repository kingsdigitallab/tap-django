# Generated by Django 2.0.2 on 2018-02-21 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0011_aggregationframework_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aggregationframework',
            old_name='label',
            new_name='title',
        ),
    ]
