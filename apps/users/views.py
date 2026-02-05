"""Vistas relacionadas con usuarios y clientes.

Este módulo expone vistas simples basadas en clases de DRF para:
- Listar/Crear `Customer`
- Obtener/Actualizar/Eliminar un `Customer`
- Registrar usuarios
- Listar usuarios
- Obtener/Actualizar/Eliminar usuarios

Comentarios: el proyecto es intencionalmente simple; las vistas usan
querysets básicos y serializers definidos en `apps.users.serializers`.
"""

from django.contrib.auth.models import User
from .models import Customer
from .serializers import CustomerSerializer, UserReadSerializer, UserRegisterSerializer, UserUpdateSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from django.db.models.deletion import ProtectedError


class CustomerListCreateView(ListCreateAPIView):
    """Lista todos los `Customer` y permite crear nuevos.

    - GET `/customers/` devuelve lista de clientes.
    - POST `/customers/` crea un cliente (usa `CustomerSerializer`).
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetailView(RetrieveUpdateDestroyAPIView):
    """Recupera, actualiza o elimina un `Customer` por `pk`.

    - GET `/customers/<pk>/` devuelve el cliente.
    - PUT/PATCH actualiza.
    - DELETE borra el registro.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UserRegisterView(CreateAPIView):
    """Registra un nuevo `User`.

    - POST `/register/` crea un usuario usando `UserRegisterSerializer`.
    El serializer se encarga de hashear el password.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class UserListView(ListAPIView):
    """Lista usuarios existentes.

    - GET `/` devuelve usuarios (read-only serializer).
    """
    queryset = User.objects.all()
    serializer_class = UserReadSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación segura de usuarios.

    - Para operaciones de escritura (PUT/PATCH) se utiliza
      `UserUpdateSerializer`.
    - Para lectura se usa `UserReadSerializer`.
    - `perform_destroy` captura `ProtectedError` y en vez de
      eliminar marca al usuario como inactivo.
    """
    queryset = User.objects.all()
    serializer_class = UserReadSerializer

    def get_serializer_class(self):
        """Selecciona el serializer según el método HTTP.

        Protege los campos sensibles al exponer solo lectura por defecto.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserReadSerializer
    
    def perform_destroy(self, instance):
        """Intento de eliminación: si falla por relaciones protegidas,
        se desactiva el usuario en su lugar.
        """
        try:
            instance.delete()
        except ProtectedError:
            # No eliminar para preservar integridad de datos
            instance.is_active = False
            instance.save()