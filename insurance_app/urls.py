from django.urls import path
from . import views

urlpatterns = [
    # Ana sayfa: Müşteri listesi (URL: /)
    path('', views.customer_list, name='customer_list'),
    
    # Ekstra Müşteri Listesi Yolu: Filtreleme butonları /customer-list/ adresine yönleniyorsa bu kullanılır.
    path('customer-list/', views.customer_list, name='list_page'), 
    
    # Müşteri Ekleme (URL: /customer-add/)
    path('customer-add/', views.create_customer, name='add_customer'),
    
    # Müşteri Detayı: Bir müşterinin detayını görmek için bu gereklidir (URL: /customer/123/)
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Referanslar (URL: /referanslar/)
    path('referanslar/', views.referanslar_view, name='referanslar'),
    path('referanslar/search/', views.referanslar_search, name='referanslar_search'),
]
