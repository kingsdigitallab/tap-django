# Generated by Django 2.0.2 on 2018-02-21 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0013_rename_field_label_on_filter_to_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregationframework',
            name='render',
            field=models.TextField(blank=True, help_text='Enter valid JavaScript', null=True),
        ),
    ]
