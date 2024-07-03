from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search_result", views.search_result, name="search_result"),
    path("graphs", views.graphs, name="graphs")
]