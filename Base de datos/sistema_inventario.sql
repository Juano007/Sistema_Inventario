USE sistema_inventario;

CREATE TABLE inventario_almacen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    capacidad INT NOT NULL
);

CREATE TABLE inventario_producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio_compra DECIMAL(10, 2) NOT NULL,
    precio_venta DECIMAL(10, 2) NOT NULL,
    cantidad INT NOT NULL,
    almacen_id INT,
    estado VARCHAR(20) DEFAULT 'disponible',
    imagen VARCHAR(255),
    es_beneficio_sci BOOLEAN DEFAULT FALSE,
    fecha_limite_exportacion DATE,
    FOREIGN KEY (almacen_id) REFERENCES inventario_almacen(id)
);

CREATE TABLE inventario_proveedor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE inventario_productoproveedor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    proveedor_id INT,
    FOREIGN KEY (producto_id) REFERENCES inventario_producto(id),
    FOREIGN KEY (proveedor_id) REFERENCES inventario_proveedor(id)
);

CREATE TABLE inventario_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    cliente VARCHAR(255) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente',
    estado_pago VARCHAR(20) DEFAULT 'pendiente'
);

CREATE TABLE inventario_detallepedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES inventario_pedido(id),
    FOREIGN KEY (producto_id) REFERENCES inventario_producto(id)
);

CREATE TABLE inventario_venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    cliente VARCHAR(255) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    pedido_id INT UNIQUE,
    FOREIGN KEY (pedido_id) REFERENCES inventario_pedido(id)
);

CREATE TABLE inventario_detalleventa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES inventario_venta(id),
    FOREIGN KEY (producto_id) REFERENCES inventario_producto(id)
);

CREATE TABLE inventario_exportacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    fecha_exportacion DATE NOT NULL,
    pais_destino VARCHAR(100) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES inventario_venta(id)
);

CREATE TABLE inventario_devolucion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    fecha_devolucion DATE NOT NULL,
    motivo TEXT NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES inventario_venta(id)
);

CREATE TABLE inventario_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE inventario_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY user_id_group_id_unique (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES inventario_user (id),
    FOREIGN KEY (group_id) REFERENCES auth_group (id)
);

CREATE TABLE inventario_user_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY user_id_permission_id_unique (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES inventario_user (id),
    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
);