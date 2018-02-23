from apscheduler.jobstores.base import JobLookupError
from django import forms
from django.contrib import admin

from .apscheduler import scheduler
from .fields import JavaScriptWidget
from .models import Aggregation, Filter, MapReduce
from .twitter import harvest


class AggregationFrameworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AggregationFrameworkForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field.endswith('_js'):
                self.fields[field].widget = JavaScriptWidget(
                    attrs={'class': 'js'})


@admin.register(Aggregation)
class AggregationAdmin(admin.ModelAdmin):
    exclude = ['user']
    form = AggregationFrameworkForm
    list_display = ['title', 'user', 'modified']


@admin.register(MapReduce)
class MapReduceAdmin(admin.ModelAdmin):
    exclude = ['user']
    form = AggregationFrameworkForm
    list_display = ['title', 'user', 'modified']


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
            scheduler.add_job(harvest, 'interval', args=[obj], id=obj.uid,
                              minutes=1, max_instances=1,
                              replace_existing=True)
        else:
            try:
                scheduler.remove_job(obj.uid)
            except JobLookupError:
                pass
