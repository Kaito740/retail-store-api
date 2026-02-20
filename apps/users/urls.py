from django.urls import path
from .views import (
    CustomerListCreateView,
    CustomerDetailView,
    UserListView,
    UserDetailView,
    LoginView,
    LogoutView
)

urlpatterns = [
    # Clientes
    path('customers/', CustomerListCreateView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),

    # Autenticación
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    # Usuarios - Solo lectura para empleados, el superusuario gestiona en admin
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
