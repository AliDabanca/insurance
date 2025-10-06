# insurance_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
     path('customer-list/', views.customer_list, name='customer_list'),
    path('customer-add/', views.create_customer, name='add_customer'),
    path('referanslar/', views.referanslar_view, name='referanslar'),
    path('referanslar/search/', views.referanslar_search, name='referanslar_search'),
]