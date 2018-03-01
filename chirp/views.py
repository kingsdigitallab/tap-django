import json
import re

from bson import json_util
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AggregationFramework, Filter


class FilterDetailView(DetailView):
    model = Filter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = None
        context['query'] = query

        if 'query-field' in self.request.GET:
            if 'query-value' in self.request.GET:
                regex = re.compile(self.request.GET['query-value'])
                query = {self.request.GET['query-field']: regex}

                context['query'] = query

        f = Filter.objects.get(id=self.object.id)
        context['tweets'] = f.get_tweets(query=query)

        return context


class FilterListView(ListView, LoginRequiredMixin):
    model = Filter


@api_view(['GET'])
def get_filters(request):
    filters = [{'id': f.id, 'label': f.label, 'active': f.active}
               for f in Filter.objects.all()]
    return Response(filters)


@api_view(['GET'])
def get_tweets(request, filter_id):
    f = Filter.objects.get(id=filter_id)
    query = None

    if 'query-field' in request.GET:
        if 'query-value' in request.GET:
            query = {}
            query = {request.GET['query-field']: request.GET['query-value']}

    tweets = [
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in f.get_tweets(query=query)
    ]

    return Response(tweets)


@api_view(['GET'])
def get_words(request, filter_id):
    f = Filter.objects.get(id=filter_id)

    return Response(f.get_words())


@api_view(['GET'])
def perform_aggregation(request, filter_id, aggregation_id):
    f = Filter.objects.get(id=filter_id)
    a = AggregationFramework.objects.get(id=aggregation_id)
    response = a.perform(f)

    return Response(response)
