from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView, UserRegisterView, UserListView, UserDetailView

urlpatterns = [
    path('customers/', CustomerListCreateView.as_view()),
    path('customers/<int:pk>/', CustomerDetailView.as_view()),
    path('register/', UserRegisterView.as_view()),
    path('', UserListView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
]