from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from .serializers import SaleSerializer, SaleReadSerializer
from .services import sale_paid, sale_cancelled
from .models import Sale
from apps.users.models import Customer


class SaleListCreateView(generics.ListCreateAPIView):
    """Lista y crea ventas.

    - GET `/sales/` lista todas las ventas con filtros opcionales.
      Filtros: ?status=, ?customer_id=, ?date_from=, ?date_to=
    - POST `/sales/` crea una nueva venta en estado PAID.
    """
    queryset = Sale.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaleSerializer
        return SaleReadSerializer

    def get_queryset(self):
        queryset = Sale.objects.all().prefetch_related('items', 'items__product')
        
        # Filtro por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        # Filtro por cliente
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filtro por fecha desde
        date_from = self.request.query_params.get('date_from')
        if date_from:
            parsed_date = parse_date(date_from)
            if parsed_date:
                queryset = queryset.filter(created_at__date__gte=parsed_date)
        
        # Filtro por fecha hasta
        date_to = self.request.query_params.get('date_to')
        if date_to:
            parsed_date = parse_date(date_to)
            if parsed_date:
                queryset = queryset.filter(created_at__date__lte=parsed_date)
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = SaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products_data = serializer.validated_data['items']
        customer = serializer.validated_data.get('customer')

        try:
            sale = sale_paid(
                created_by=request.user,
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


class SaleDetailView(APIView):
    """Detalle y operaciones de una venta específica.

    - GET `/sales/<pk>/` devuelve los detalles de la venta.
    - PATCH `/sales/<pk>/cancel/` cancela la venta.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        sale = get_object_or_404(Sale.objects.prefetch_related('items', 'items__product'), pk=pk)
        serializer = SaleReadSerializer(sale)
        return Response(serializer.data)

    def patch(self, request, pk):
        action = request.data.get('action')
        
        if action == 'cancel':
            try:
                sale = sale_cancelled(sale_id=pk)
                return Response({
                    'message': 'Venta cancelada exitosamente',
                    'sale_id': sale.id,
                    'status': sale.status
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Acción no válida. Use action=cancel'},
                status=status.HTTP_400_BAD_REQUEST
            )
