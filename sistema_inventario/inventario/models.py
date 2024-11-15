from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=20)

class Almacen(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    capacidad = models.IntegerField()
    tipo = models.CharField(max_length=50, choices=[('general', 'General'), ('refrigerado', 'Refrigerado'), ('seguridad', 'Alta Seguridad')])

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    almacen = models.ForeignKey(Almacen, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, default='disponible')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    es_beneficio_sci = models.BooleanField(default=False)
    fecha_limite_exportacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'proveedor')

class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='pendiente')
    estado_pago = models.CharField(max_length=20, default='pendiente')

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class Exportacion(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    fecha_exportacion = models.DateField()
    pais_destino = models.CharField(max_length=100)

class Devolucion(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    fecha_devolucion = models.DateField()
    motivo = models.TextField()