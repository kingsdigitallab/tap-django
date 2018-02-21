from django.urls import path

from .views import FilterDetailView, FilterListView, get_filters

urlpatterns = [
    path('', FilterListView.as_view()),
    path('filters/<int:pk>/', FilterDetailView.as_view(),
         name='filter-detail'),
    path('filters', get_filters)
]
