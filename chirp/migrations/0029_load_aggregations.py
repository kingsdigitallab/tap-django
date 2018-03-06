# Generated by Django 2.0.2 on 2018-03-06 12:24

from django.core.management import call_command
from django.core.serializers import base, python
from django.db import migrations


def load_fixture(apps, schema_editor):
    # See https://stackoverflow.com/a/39743581 for more information about the
    # implementation of this migration

    # Save the old _get_model() function
    old_get_model = python._get_model

    # Define new _get_model() function here, which utilizes the apps argument
    # to get the historical version of a model. This piece of code is directly
    # stolen from django.core.serializers.python._get_model, unchanged.
    def _get_model(model_identifier):
        try:
            return apps.get_model(model_identifier)
        except (LookupError, TypeError):
            raise base.DeserializationError(
                'Invalid model identifier: "{}"'.format(model_identifier))

    # Replace the _get_model() function on the module,
    # so loaddata can utilize it.
    python._get_model = _get_model

    try:
        # Call loaddata command
        call_command('loaddata', 'initial_aggregations.json',
                     app_label='chirp')
    finally:
        # Restore old _get_model() function
        python._get_model = old_get_model


class Migration(migrations.Migration):
    dependencies = [
        ('chirp', '0028_alter_field_query_field_on_aggregationframework'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
