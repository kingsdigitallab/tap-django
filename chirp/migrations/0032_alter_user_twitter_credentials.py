# Generated by Django 2.0.6 on 2018-06-20 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0031_alter_field_active_on_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='twitter_access_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='twitter_access_token_secret',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='twitter_api_key',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='twitter_api_secret',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]