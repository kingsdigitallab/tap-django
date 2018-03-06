from apscheduler.jobstores.base import JobLookupError
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.text import slugify
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter,
                               PolymorphicParentModelAdmin)

from .apscheduler import scheduler
from .fields import JavaScriptWidget
from .models import Aggregation, AggregationFramework, Filter, MapReduce, User
from .twitter import harvest


class AggregationFrameworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AggregationFrameworkForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field.endswith('_js'):
                self.fields[field].widget = JavaScriptWidget(
                    attrs={'class': 'js'})


class AggregationFrameworkChildAdmin(PolymorphicChildModelAdmin):
    base_form = AggregationFrameworkForm
    exclude = ['slug', 'user']
    list_display = ['title', 'user', 'modified']

    def save_model(self, request, obj, form, change):
        obj.slug = slugify(obj.title)
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Aggregation)
class AggregationAdmin(AggregationFrameworkChildAdmin):
    base_model = Aggregation


@admin.register(MapReduce)
class MapReduceAdmin(AggregationFrameworkChildAdmin):
    base_model = MapReduce


@admin.register(AggregationFramework)
class AggregationFrameworkAdmin(PolymorphicParentModelAdmin):
    base_model = AggregationFramework
    child_models = [Aggregation, MapReduce]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    exclude = ['user']
    filter_horizontal = ['aggregations']
    list_display = ['title', 'active', 'follow', 'track', 'locations',
                    'number_of_tweets', 'sentiment_avg', 'uid', 'user',
                    'modified']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

        if obj.active:
            if obj.user.has_twitter_credentials:
                scheduler.add_job(harvest, 'interval', args=[obj], id=obj.uid,
                                  minutes=1, max_instances=1,
                                  replace_existing=True)
        else:
            try:
                scheduler.remove_job(obj.uid)
            except JobLookupError:
                pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('has_twitter_credentials',)

    base_fieldsets = BaseUserAdmin.fieldsets
    fieldsets = base_fieldsets[:2] + (
        ('Twitter', {
            'fields': ('twitter_api_key', 'twitter_api_secret',
                       'twitter_access_token', 'twitter_access_token_secret'),
            'description': ('Set up twitter credentials at '
                            'https://apps.twitter.com/')
        }),
    ) + base_fieldsets[2:]
