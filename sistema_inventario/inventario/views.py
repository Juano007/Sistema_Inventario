from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Producto, Almacen, Proveedor, Pedido, Venta, Exportacion, Devolucion, DetalleVenta
from .serializers import UserSerializer, ProductoSerializer, AlmacenSerializer, ProveedorSerializer, PedidoSerializer, VentaSerializer, ExportacionSerializer, DevolucionSerializer
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def low_stock(self, request):
        threshold = request.query_params.get('threshold', 10)
        productos = Producto.objects.filter(cantidad__lte=threshold)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def adjust_stock(self, request, pk=None):
        producto = self.get_object()
        cantidad = request.data.get('cantidad', 0)
        producto.cantidad += int(cantidad)
        producto.save()
        return Response({'message': 'Stock adjusted successfully'})

class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def productos(self, request, pk=None):
        almacen = self.get_object()
        productos = Producto.objects.filter(almacen=almacen)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def complete_order(self, request, pk=None):
        pedido = self.get_object()
        pedido.estado = 'completado'
        pedido.save()
        return Response({'message': 'Order completed successfully'})

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        venta = serializer.save()
        for detalle in venta.detalles.all():
            producto = detalle.producto
            producto.cantidad -= detalle.cantidad
            producto.save()

    @action(detail=False, methods=['GET'])
    def sales_report(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        ventas = Venta.objects.filter(fecha__range=[start_date, end_date])
        total_ventas = ventas.aggregate(total=Sum('total'))['total']
        return Response({
            'total_ventas': total_ventas,
            'numero_ventas': ventas.count()
        })

class ExportacionViewSet(viewsets.ModelViewSet):
    queryset = Exportacion.objects.all()
    serializer_class = ExportacionSerializer
    permission_classes = [IsAuthenticated]

class DevolucionViewSet(viewsets.ModelViewSet):
    queryset = Devolucion.objects.all()
    serializer_class = DevolucionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        devolucion = serializer.save()
        venta = devolucion.venta
        for detalle in venta.detalles.all():
            producto = detalle.producto
            producto.cantidad += detalle.cantidad
            producto.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    time_range = request.GET.get('time_range', '7d')
    
    if time_range == '7d':
        start_date = datetime.now() - timedelta(days=7)
    elif time_range == '30d':
        start_date = datetime.now() - timedelta(days=30)
    elif time_range == '90d':
        start_date = datetime.now() - timedelta(days=90)
    else:
        return Response({'error': 'Invalid time range'}, status=400)

    total_productos = Producto.objects.count()
    total_ventas = Venta.objects.filter(fecha__gte=start_date).aggregate(Sum('total'))['total__sum'] or 0
    total_pedidos = Pedido.objects.filter(fecha__gte=start_date).count()
    valor_inventario = Producto.objects.aggregate(total=Sum(F('cantidad') * F('precio_venta')))['total'] or 0

    ventas_mensuales = Venta.objects.filter(fecha__gte=start_date) \
        .annotate(month=TruncMonth('fecha')) \
        .values('month') \
        .annotate(ventas=Sum('total'), ganancias=Sum(F('total') - F('pedido__detalles__precio_unitario') * F('pedido__detalles__cantidad'))) \
        .order_by('month')

    productos_mas_vendidos = DetalleVenta.objects.filter(venta__fecha__gte=start_date) \
        .values('producto__nombre') \
        .annotate(ventas=Sum('cantidad')) \
        .order_by('-ventas')[:5]

    clientes_top = Venta.objects.filter(fecha__gte=start_date) \
        .values('cliente') \
        .annotate(compras=Sum('total')) \
        .order_by('-compras')[:5]

    ganancias_netas = sum(venta['ganancias'] for venta in ventas_mensuales)
    
    crecimiento_ventas = 0
    if len(ventas_mensuales) > 1:
        primer_mes = ventas_mensuales[0]['ventas']
        ultimo_mes = ventas_mensuales[-1]['ventas']
        crecimiento_ventas = ((ultimo_mes - primer_mes) / primer_mes) * 100 if primer_mes > 0 else 0

    data = {
        'total_productos': total_productos,
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'valor_inventario': valor_inventario,
        'ventas_mensuales': list(ventas_mensuales),
        'productos_mas_vendidos': list(productos_mas_vendidos),
        'clientes_top': list(clientes_top),
        'ganancias_netas': ganancias_netas,
        'crecimiento_ventas': crecimiento_ventas,
    }

    return Response(data)