from django.urls import path

from .views import (FilterDetailView, FilterListView, get_filters, get_tweets,
                    get_words, perform_aggregation)

urlpatterns = [
    path('', FilterListView.as_view()),
    path('filters/<int:pk>/', FilterDetailView.as_view(),
         name='filter-detail'),
    path('filters/<int:filter_id>/aggregation/<int:aggregation_id>/',
         perform_aggregation, name='perform-aggregation'),
    path('filters/<int:filter_id>/tweets/<int:page>/',
         get_tweets, name='get-tweets'),
    path('filters/<int:filter_id>/words/',
         get_words, name='get-words'),
    path('filters', get_filters)
]
