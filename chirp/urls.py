from django.urls import path

from .views import (FilterDetailView, FilterListView, get_filters,
                    perform_aggregation)

urlpatterns = [
    path('', FilterListView.as_view()),
    path('filters/<int:pk>/', FilterDetailView.as_view(),
         name='filter-detail'),
    path('filters/<int:filter_id>/aggregation/<int:aggregation_id>/',
         perform_aggregation, name='perform-aggregation'),
    path('filters', get_filters)
]
