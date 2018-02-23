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
        return context


class FilterListView(ListView, LoginRequiredMixin):
    model = Filter


@api_view(['GET'])
def get_filters(request):
    filters = [{'id': f.id, 'label': f.label, 'active': f.active}
               for f in Filter.objects.all()]
    return Response(filters)


@api_view(['GET'])
def perform_aggregation(request, filter_id, aggregation_id):
    f = Filter.objects.get(id=filter_id)
    a = AggregationFramework.objects.get(id=aggregation_id)
    response = a.perform(f)

    return Response(response)
