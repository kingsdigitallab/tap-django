# Generated by Django 2.0.2 on 2018-02-21 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0012_rename_field_label_on_aggregationframework_to_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='filter',
            old_name='label',
            new_name='title',
        ),
    ]
