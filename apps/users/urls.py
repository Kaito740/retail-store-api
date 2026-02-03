from django.urls import path
from .views import ListCreateCustomerView, RetrieveUpdateDestroyCustomerView

urlpatterns = [
    path('customers/',ListCreateCustomerView.as_view(),name='customer-list'),
    path('customers/<int:pk>/', RetrieveUpdateDestroyCustomerView.as_view(),name='customer-rud')
]