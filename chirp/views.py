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

        query = _get_query(self.request)
        context['query'] = query

        f = Filter.objects.get(id=self.object.id)
        context['tweets'] = f.get_tweets(query=query)

        return context


def _get_query(request):
    if 'query-field' in request.GET:
        if 'query-value' in request.GET:
            regex = re.compile(request.GET['query-value'])
            query = {request.GET['query-field']: regex}

            return query

    return None


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
    query = _get_query(request)

    tweets = [
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in f.get_tweets(query=query)
    ]

    return Response(tweets)


@api_view(['GET'])
def get_words(request, filter_id):
    f = Filter.objects.get(id=filter_id)

    return Response(f.get_words(query=_get_query(request)))


@api_view(['GET'])
def perform_aggregation(request, filter_id, aggregation_id):
    f = Filter.objects.get(id=filter_id)
    a = AggregationFramework.objects.get(id=aggregation_id)
    response = a.perform(f, query=_get_query(request))
    return Response(response)
