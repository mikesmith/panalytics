from django.urls import path

from . import views

urlpatterns = [
    path('a.js', views.script, name='script'),
    path('a.gif', views.collect, name='collect'),
]
