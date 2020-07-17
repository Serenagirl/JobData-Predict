from django.urls import path
from . import views

app_name = 'test'
urlpatterns = [
    path(r'index', views.index, name='index'),
    path(r'search/<str:column>/<str:kw>',views.search,name='search'),
    path(r'show', views.show, name='show'),
    path(r'query', views.query, name='query'),
]