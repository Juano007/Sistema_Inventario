# inventario/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register_user, ProductoViewSet, AlmacenViewSet, ProveedorViewSet, PedidoViewSet, VentaViewSet, ExportacionViewSet, DevolucionViewSet, dashboard

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'almacenes', AlmacenViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'exportaciones', ExportacionViewSet)
router.register(r'devoluciones', DevolucionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]