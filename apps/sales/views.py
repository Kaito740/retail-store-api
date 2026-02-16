from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SaleSerializer
from .services import sale_paid
from apps.users.models import Customer


class SaleView(APIView):
    """Crear una nueva venta.

    - POST `/sales/` crea una venta en estado PAID.
    - Requiere autenticación (Token).
    - El usuario autenticado se registra como creador de la venta.
    """

    def post(self, request):
        serializer = SaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products_data = serializer.validated_data['items']
        customer_id = request.data.get('customer_id')

        # Obtener cliente si se proporciona
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response(
                    {'error': 'Cliente no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

        try:
            sale = sale_paid(
                created_by=request.user,  # Usuario autenticado
                products_data=products_data,
                customer=customer
            )
            return Response({
                'message': 'Venta creada exitosamente',
                'sale_id': sale.id,
                'total_amount': str(sale.total_amount),
                'status': sale.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
