"""Vistas relacionadas con usuarios y clientes.

Este módulo expone vistas simples basadas en clases de DRF para:
- Listar/Crear `Customer` (clientes)
- Login de usuarios/empleados
- Listar usuarios existentes (solo lectura)

NOTA IMPORTANTE: Este es un sistema para una tienda de juguetes minorista local.
Los usuarios/empleados son creados EXCLUSIVAMENTE por el superusuario (jefe/admin)
en el panel administrativo de Django. No existe registro público de usuarios.
Los empleados solo pueden hacer login para registrar ventas.

Comentarios: el proyecto es intencionalmente simple; las vistas usan
querysets básicos y serializers definidos en `apps.users.serializers`.
"""

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models.deletion import ProtectedError
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Customer
from .serializers import CustomerSerializer, UserReadSerializer, UserUpdateSerializer


class CustomerListCreateView(ListCreateAPIView):
    """Lista todos los `Customer` y permite crear nuevos.

    - GET `/customers/` devuelve lista de clientes.
      Filtros: ?phone= (búsqueda parcial)
    - POST `/customers/` crea un cliente (usa `CustomerSerializer`).
    """
    serializer_class = CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.all()
        
        # Filtro por teléfono (búsqueda parcial)
        phone = self.request.query_params.get('phone')
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        
        return queryset


class CustomerDetailView(RetrieveUpdateDestroyAPIView):
    """Recupera, actualiza o elimina un `Customer` por `pk`.

    - GET `/customers/<pk>/` devuelve el cliente.
    - PUT/PATCH actualiza.
    - DELETE borra el registro.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UserListView(ListAPIView):
    """Lista usuarios existentes.

    - GET `/` devuelve usuarios (read-only serializer).
    - NOTA: Los usuarios solo pueden ser creados por el superusuario
      en el panel administrativo de Django.
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
    - NOTA: Solo el superusuario puede crear usuarios nuevos
      desde el panel administrativo.
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


class LoginView(APIView):
    """Login de usuario/empleado y generación de token de autenticación.

    - POST `/login/` recibe username y password.
    - Devuelve token si las credenciales son válidas.
    - No requiere autenticación previa (AllowAny).
    - NOTA: Los usuarios deben ser creados previamente por el superusuario
      en el panel administrativo de Django.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username y password son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })

        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
