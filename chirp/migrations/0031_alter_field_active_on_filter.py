# Generated by Django 2.0.2 on 2018-03-06 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chirp', '0030_add_twitter_fields_to_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filter',
            name='active',
            field=models.BooleanField(help_text='Set active to harvest tweets.You need to have twitter credentials in your account to be able to harvest tweets.'),
        ),
    ]
