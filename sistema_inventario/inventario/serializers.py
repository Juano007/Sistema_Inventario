from rest_framework import serializers
from .models import User, Almacen, Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta, Exportacion, Devolucion, ProductoProveedor

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoProveedorSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)

    class Meta:
        model = ProductoProveedor
        fields = ['proveedor']

class ProductoSerializer(serializers.ModelSerializer):
    proveedores = ProductoProveedorSerializer(many=True, read_only=True, source='productoproveedor_set')
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'

    def create(self, validated_data):
        proveedores_data = self.context['request'].data.get('proveedores', [])
        producto = Producto.objects.create(**validated_data)
        for proveedor_id in proveedores_data:
            ProductoProveedor.objects.create(producto=producto, proveedor_id=proveedor_id)
        return producto

    def update(self, instance, validated_data):
        proveedores_data = self.context['request'].data.get('proveedores', [])
        instance = super().update(instance, validated_data)
        instance.productoproveedor_set.all().delete()
        for proveedor_id in proveedores_data:
            ProductoProveedor.objects.create(producto=instance, proveedor_id=proveedor_id)
        return instance

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario']

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'

    def create(self, validated_data):
        detalles_data = self.context['request'].data.get('detalles', [])
        pedido = Pedido.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        return pedido

    def update(self, instance, validated_data):
        detalles_data = self.context['request'].data.get('detalles', [])
        instance = super().update(instance, validated_data)
        instance.detalles.all().delete()
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=instance, **detalle_data)
        return instance

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario']

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = '__all__'

    def create(self, validated_data):
        detalles_data = self.context['request'].data.get('detalles', [])
        venta = Venta.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)
        return venta

    def update(self, instance, validated_data):
        detalles_data = self.context['request'].data.get('detalles', [])
        instance = super().update(instance, validated_data)
        instance.detalles.all().delete()
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=instance, **detalle_data)
        return instance

class ExportacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exportacion
        fields = '__all__'

class DevolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devolucion
        fields = '__all__'