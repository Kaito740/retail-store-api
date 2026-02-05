"""Serializers para la app `users`.

Contiene serializers mínimos para `Customer` y `User`.
Diseñado para un proyecto simple: read-only serializers para
exposición y serializers separados para registro/actualización.
"""

from rest_framework.serializers import ModelSerializer
from .models import Customer
from django.contrib.auth.models import User


class CustomerSerializer(ModelSerializer):
    """Serializer para `Customer`.

    Campos:
    - `id` (read-only)
    - `name`, `phone` (lectura/escritura)
    """
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone']
        read_only_fields = ['id']


class UserReadSerializer(ModelSerializer):
    """Serializer de solo-lectura para `User`.

    Usado para devolver información pública del usuario sin
    exponer campos sensibles ni permitir modificaciones.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active'
        ]


class UserRegisterSerializer(ModelSerializer):
    """Serializer para registro de nuevos usuarios.

    - `password` está en `extra_kwargs` como `write_only` para que
      no se devuelva en respuestas.
    - `create()` utiliza `create_user()` para asegurar el hashing
      correcto de la contraseña.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        """Crea y devuelve un `User` usando `create_user`.

        `validated_data` debe contener `username`, `password` y `email`.
        Se delega en Django para gestionar hashing y defaults.
        """
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(ModelSerializer):
    """Serializer para actualizar datos no sensibles de `User`.

    Solo permite cambiar `first_name`, `last_name` y `email`.
    `id` es read-only para evitar reasignaciones accidentales.
    """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']