#encoding: utf-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list_event/', views.list_event, name='list_event'),
    url(r'^deal_event/(?P<pk>\d+)/', views.deal_event, name='deal_event'),
    url(r'^list_file/', views.list_file, name='list_file'),
    url(r'^recover_file/(?P<pk>\d+)/', views.recover_file, name='recover_file'),
    url(r'^ignore_file/(?P<pk>\d+)/', views.ignore_file, name='ignore_file'),
    url(r'^setting/', views.setting, name='setting')
]
