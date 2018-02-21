from apscheduler.jobstores.base import JobLookupError
from django.contrib import admin

from .apscheduler import scheduler
from .models import Aggregation, Filter, MapReduce
from .twitter import harvest


@admin.register(Aggregation)
class AggregationAdmin(admin.ModelAdmin):
    exclude = ['user']
    list_display = ['label', 'user', 'modified']


@admin.register(MapReduce)
class MapReduceAdmin(admin.ModelAdmin):
    exclude = ['user']
    list_display = ['label', 'user', 'modified']


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    exclude = ['user']
    filter_horizontal = ['aggregations']
    list_display = ['label', 'active', 'follow', 'track', 'locations',
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
