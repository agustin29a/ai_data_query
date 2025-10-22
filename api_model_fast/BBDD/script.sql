-- Tabla CLIENTES
CREATE TABLE CLIENTES (
    id SERIAL PRIMARY KEY,
    dni_ruc VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    fecha_nacimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla METODOS_PAGO
CREATE TABLE METODOS_PAGO (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla TARJETAS
CREATE TABLE TARJETAS (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    entidad_emisora VARCHAR(100),
    credito BOOLEAN DEFAULT FALSE,
    debito BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla PLANES_PAGO
CREATE TABLE PLANES_PAGO (
    id SERIAL PRIMARY KEY,
    tarjeta_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    cuotas INTEGER NOT NULL,
    interes DECIMAL(5,2) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (tarjeta_id) REFERENCES TARJETAS(id)
);

-- Tabla CATEGORIAS
CREATE TABLE CATEGORIAS (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_padre_id INTEGER,
    FOREIGN KEY (categoria_padre_id) REFERENCES CATEGORIAS(id)
);

-- Tabla PRODUCTOS
CREATE TABLE PRODUCTOS (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER NOT NULL,
    marca VARCHAR(100),
    talla VARCHAR(10),
    color VARCHAR(50),
    precio_venta DECIMAL(10,2) NOT NULL,
    precio_costo DECIMAL(10,2) NOT NULL,
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 5,
    imagen_url VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (categoria_id) REFERENCES CATEGORIAS(id)
);

-- Tabla DESCUENTOS
CREATE TABLE DESCUENTOS (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo_descuento VARCHAR(20) CHECK (tipo_descuento IN ('PORCENTAJE', 'MONTO_FIJO')),
    valor_descuento DECIMAL(10,2) NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    maximo_usos INTEGER DEFAULT NULL,
    usos_actuales INTEGER DEFAULT 0,
    minimo_compra DECIMAL(10,2) DEFAULT 0,
    aplica_todo_catalogo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla intermedia PRODUCTO_DESCUENTO
CREATE TABLE PRODUCTO_DESCUENTO (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    descuento_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id) ON DELETE CASCADE,
    FOREIGN KEY (descuento_id) REFERENCES DESCUENTOS(id) ON DELETE CASCADE,
    UNIQUE(producto_id, descuento_id)
);

-- Tabla PROVEEDORES
CREATE TABLE PROVEEDORES (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(255) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

-- Tabla COMPRAS
CREATE TABLE COMPRAS (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL,
    fecha_compra DATE NOT NULL,
    numero_documento VARCHAR(50) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'PAGADA', 'CANCELADA')),
    FOREIGN KEY (proveedor_id) REFERENCES PROVEEDORES(id)
);

-- Tabla DETALLE_COMPRA
CREATE TABLE DETALLE_COMPRA (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES COMPRAS(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id)
);

-- Tabla COMPROBANTES_VENTA
CREATE TABLE COMPROBANTES_VENTA (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    numero_serie VARCHAR(4) NOT NULL,
    numero_comprobante VARCHAR(8) NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    igv DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    tipo_comprobante VARCHAR(20) DEFAULT 'BOLETA' CHECK (tipo_comprobante IN ('BOLETA', 'FACTURA')),
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'PAGADA', 'CANCELADA')),
    FOREIGN KEY (cliente_id) REFERENCES CLIENTES(id),
    UNIQUE(numero_serie, numero_comprobante)
);

-- Tabla DETALLE_VENTA
CREATE TABLE DETALLE_VENTA (
    id SERIAL PRIMARY KEY,
    comprobante_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    descuento_id INTEGER,
    FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTES_VENTA(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id),
    FOREIGN KEY (descuento_id) REFERENCES DESCUENTOS(id)
);

-- Tabla TRANSACCIONES
CREATE TABLE TRANSACCIONES (
    id SERIAL PRIMARY KEY,
    comprobante_id INTEGER NOT NULL,
    metodo_pago_id INTEGER NOT NULL,
    tarjeta_id INTEGER,
    plan_pago_id INTEGER,
    monto DECIMAL(10,2) NOT NULL,
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_operacion VARCHAR(50),
    ultimos_digitos VARCHAR(4),
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'COMPLETADA', 'RECHAZADA', 'REVERSADA')),
    FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTES_VENTA(id),
    FOREIGN KEY (metodo_pago_id) REFERENCES METODOS_PAGO(id),
    FOREIGN KEY (tarjeta_id) REFERENCES TARJETAS(id),
    FOREIGN KEY (plan_pago_id) REFERENCES PLANES_PAGO(id)
);

-- Tabla INVENTARIO_MOVIMIENTOS
CREATE TABLE INVENTARIO_MOVIMIENTOS (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE')),
    cantidad INTEGER NOT NULL,
    stock_anterior INTEGER NOT NULL,
    stock_nuevo INTEGER NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_productos_categoria ON PRODUCTOS(categoria_id);
CREATE INDEX idx_productos_activo ON PRODUCTOS(activo);
CREATE INDEX idx_comprobantes_cliente ON COMPROBANTES_VENTA(cliente_id);
CREATE INDEX idx_comprobantes_fecha ON COMPROBANTES_VENTA(fecha_emision);
CREATE INDEX idx_detalle_venta_comprobante ON DETALLE_VENTA(comprobante_id);
CREATE INDEX idx_detalle_venta_producto ON DETALLE_VENTA(producto_id);
CREATE INDEX idx_descuentos_fechas ON DESCUENTOS(fecha_inicio, fecha_fin);
CREATE INDEX idx_descuentos_activo ON DESCUENTOS(activo);
CREATE INDEX idx_producto_descuento ON PRODUCTO_DESCUENTO(producto_id, descuento_id);
CREATE INDEX idx_inventario_producto ON INVENTARIO_MOVIMIENTOS(producto_id);
CREATE INDEX idx_inventario_fecha ON INVENTARIO_MOVIMIENTOS(fecha_movimiento);

-- Comentarios en tablas
COMMENT ON TABLE clientes IS 'Almacena información personal de clientes como nombres, apellidos, contactos y datos demográficos. Usada para consultas de clientes, filtros por nombre, búsqueda por DNI/RUC.';

COMMENT ON TABLE metodos_pago IS 'Catálogo de métodos de pago disponibles (efectivo, tarjetas, transferencias). Usada en transacciones para definir forma de pago.';

COMMENT ON TABLE tarjetas IS 'Catálogo de tarjetas de crédito/débito aceptadas. Usada para filtros por tipo de tarjeta y configuración de planes de pago.';

COMMENT ON TABLE planes_pago IS 'Define planes de pago con cuotas e intereses para tarjetas específicas. Usada en transacciones con tarjeta para calcular cuotas.';

COMMENT ON TABLE categorias IS 'Estructura jerárquica de categorías para organizar productos. Usada para navegación, filtros y reportes por categoría.';

COMMENT ON TABLE productos IS 'Contiene catálogo de productos con precios, stock, categorías. Usada para consultas de inventario, precios, búsqueda por SKU o nombre.';

COMMENT ON TABLE descuentos IS 'Configuración de promociones y descuentos con fechas, límites y condiciones. Usada en ventas y cálculos de precios.';

COMMENT ON TABLE producto_descuento IS 'Tabla intermedia que relaciona productos con descuentos. Usada para aplicar descuentos específicos a productos.';

COMMENT ON TABLE proveedores IS 'Registro de proveedores con información de contacto. Usada en compras y gestión de inventario.';

COMMENT ON TABLE compras IS 'Registra las compras realizadas por la empresa a los proveedores. Cada registro representa una venta efectuada por un proveedor hacia la empresa, incluyendo su documento comercial, fecha, total y estado. Usada para el control de inventario, análisis de compras y seguimiento de las ventas realizadas por los proveedores.';

COMMENT ON TABLE detalle_compra IS 'Contiene el detalle de los productos vendidos por los proveedores a la empresa en cada operación de compra. Cada registro representa un producto que el proveedor entregó, con su cantidad, precio y subtotal. Usada para análisis de ventas por proveedor, actualización de stock e historial de compras.';

COMMENT ON TABLE comprobantes_venta IS 'Registra los comprobantes de venta emitidos por la empresa cuando un cliente realiza una compra. Cada comprobante representa una compra efectuada por un cliente, incluyendo boletas y facturas. Usada para reportes fiscales, control de ventas y análisis de compras realizadas por los clientes.';

COMMENT ON TABLE detalle_venta IS 'Contiene el detalle de los productos comprados por los clientes en cada comprobante de venta. Cada registro representa un producto adquirido, su cantidad, precio y descuentos aplicados. Usada para análisis de productos más comprados, comportamiento de compra y control de stock.';

COMMENT ON TABLE transacciones IS 'Registro de transacciones de pago con métodos y estados. Usada para conciliación y seguimiento de pagos.';

COMMENT ON TABLE inventario_movimientos IS 'Auditoría de movimientos de inventario con stock anterior y nuevo. Usada para trazabilidad y control de stock.';

-- Comentarios en columnas de CLIENTES
COMMENT ON COLUMN clientes.dni_ruc IS 'Documento de identidad único para búsquedas y validaciones';
COMMENT ON COLUMN clientes.nombres IS 'Nombres del cliente para búsquedas y filtros por nombre';
COMMENT ON COLUMN clientes.apellidos IS 'Apellidos del cliente para ordenamiento y búsquedas completas';
COMMENT ON COLUMN clientes.email IS 'Email para comunicación y marketing, validar formato único';
COMMENT ON COLUMN clientes.telefono IS 'Teléfono para contacto urgente y verificación';
COMMENT ON COLUMN clientes.direccion IS 'Dirección completa para envíos y facturación';
COMMENT ON COLUMN clientes.fecha_nacimiento IS 'Fecha de nacimiento para segmentación por edad';
COMMENT ON COLUMN clientes.fecha_registro IS 'Fecha de registro para análisis de clientes nuevos';
COMMENT ON COLUMN clientes.activo IS 'Estado del cliente para filtrar clientes activos/inactivos';

-- Comentarios en columnas de METODOS_PAGO
COMMENT ON COLUMN metodos_pago.nombre IS 'Nombre del método de pago para mostrar en interfaces';
COMMENT ON COLUMN metodos_pago.descripcion IS 'Descripción detallada del método de pago';
COMMENT ON COLUMN metodos_pago.activo IS 'Estado para habilitar/deshabilitar métodos de pago';

-- Comentarios en columnas de TARJETAS
COMMENT ON COLUMN tarjetas.nombre IS 'Nombre de la tarjeta (Visa, MasterCard, etc.)';
COMMENT ON COLUMN tarjetas.entidad_emisora IS 'Banco o entidad emisora de la tarjeta';
COMMENT ON COLUMN tarjetas.credito IS 'Indica si es tarjeta de crédito para filtros';
COMMENT ON COLUMN tarjetas.debito IS 'Indica si es tarjeta de débito para filtros';
COMMENT ON COLUMN tarjetas.activo IS 'Estado para habilitar/deshabilitar tarjetas';

-- Comentarios en columnas de PLANES_PAGO
COMMENT ON COLUMN planes_pago.tarjeta_id IS 'Referencia a la tarjeta para filtros por tipo';
COMMENT ON COLUMN planes_pago.nombre IS 'Nombre del plan (3 cuotas sin interés, etc.)';
COMMENT ON COLUMN planes_pago.cuotas IS 'Número de cuotas para cálculos de pago';
COMMENT ON COLUMN planes_pago.interes IS 'Tasa de interés aplicable al plan';
COMMENT ON COLUMN planes_pago.activo IS 'Estado del plan de pago';

-- Comentarios en columnas de CATEGORIAS
COMMENT ON COLUMN categorias.nombre IS 'Nombre de la categoría para navegación y filtros';
COMMENT ON COLUMN categorias.descripcion IS 'Descripción de la categoría para SEO y displays';
COMMENT ON COLUMN categorias.categoria_padre_id IS 'Referencia padre para estructura jerárquica';

-- Comentarios en columnas de PRODUCTOS
COMMENT ON COLUMN productos.sku IS 'Código único para búsquedas y control de inventario';
COMMENT ON COLUMN productos.nombre IS 'Nombre del producto para displays y búsquedas';
COMMENT ON COLUMN productos.descripcion IS 'Descripción detallada para páginas de producto';
COMMENT ON COLUMN productos.categoria_id IS 'Categoría para filtros y organización';
COMMENT ON COLUMN productos.marca IS 'Marca del producto para filtros por marca';
COMMENT ON COLUMN productos.talla IS 'Talla para productos de ropa/calzado';
COMMENT ON COLUMN productos.color IS 'Color del producto para variantes';
COMMENT ON COLUMN productos.precio_venta IS 'Precio de venta para cálculos y filtros por rango';
COMMENT ON COLUMN productos.precio_costo IS 'Precio de costo para cálculos de margen';
COMMENT ON COLUMN productos.stock_actual IS 'Stock actual para control de inventario y disponibilidad';
COMMENT ON COLUMN productos.stock_minimo IS 'Stock mínimo para alertas de reposición';
COMMENT ON COLUMN productos.imagen_url IS 'URL de imagen para displays y catálogos';
COMMENT ON COLUMN productos.activo IS 'Estado para habilitar/deshabilitar productos';

-- Comentarios en columnas de DESCUENTOS
COMMENT ON COLUMN descuentos.nombre IS 'Nombre del descuento para identificación';
COMMENT ON COLUMN descuentos.descripcion IS 'Descripción detallada de la promoción';
COMMENT ON COLUMN descuentos.tipo_descuento IS 'Tipo: PORCENTAJE o MONTO_FIJO para cálculos';
COMMENT ON COLUMN descuentos.valor_descuento IS 'Valor del descuento para aplicar en ventas';
COMMENT ON COLUMN descuentos.fecha_inicio IS 'Fecha de inicio para validar vigencia';
COMMENT ON COLUMN descuentos.fecha_fin IS 'Fecha de fin para validar vigencia';
COMMENT ON COLUMN descuentos.activo IS 'Estado del descuento';
COMMENT ON COLUMN descuentos.maximo_usos IS 'Límite máximo de usos, NULL para ilimitado';
COMMENT ON COLUMN descuentos.usos_actuales IS 'Contador de usos actuales para control';
COMMENT ON COLUMN descuentos.minimo_compra IS 'Mínimo de compra requerido para aplicar';
COMMENT ON COLUMN descuentos.aplica_todo_catalogo IS 'Indica si aplica a todo el catálogo';
COMMENT ON COLUMN descuentos.created_at IS 'Fecha de creación del descuento';
COMMENT ON COLUMN descuentos.updated_at IS 'Fecha de última actualización';

-- Comentarios en columnas de PRODUCTO_DESCUENTO
COMMENT ON COLUMN producto_descuento.producto_id IS 'Producto que tiene el descuento aplicado';
COMMENT ON COLUMN producto_descuento.descuento_id IS 'Descuento aplicado al producto';
COMMENT ON COLUMN producto_descuento.created_at IS 'Fecha de asociación producto-descuento';

-- Comentarios en columnas de PROVEEDORES
COMMENT ON COLUMN proveedores.ruc IS 'RUC único para identificación fiscal';
COMMENT ON COLUMN proveedores.razon_social IS 'Razón social para documentos legales';
COMMENT ON COLUMN proveedores.direccion IS 'Dirección para contactos y envíos';
COMMENT ON COLUMN proveedores.telefono IS 'Teléfono para contactos urgentes';
COMMENT ON COLUMN proveedores.email IS 'Email para comunicación formal';

-- Comentarios en columnas de COMPRAS
COMMENT ON COLUMN compras.proveedor_id IS 'Proveedor que realizó la venta de productos o servicios a la empresa.';
COMMENT ON COLUMN compras.fecha_compra IS 'Fecha en la que el proveedor vendió los productos o se registró la compra por parte de la empresa.';
COMMENT ON COLUMN compras.numero_documento IS 'Número del comprobante emitido por el proveedor (factura o recibo) en su venta a la empresa.';
COMMENT ON COLUMN compras.total IS 'Importe total vendido por el proveedor a la empresa en esta transacción.';
COMMENT ON COLUMN compras.estado IS 'Estado de la venta del proveedor o de la compra registrada: PENDIENTE, PAGADA o CANCELADA.';

-- Comentarios en columnas de DETALLE_COMPRA
COMMENT ON COLUMN detalle_compra.compra_id IS 'Compra asociada a la venta del proveedor. Relaciona los productos vendidos con su comprobante de compra.';
COMMENT ON COLUMN detalle_compra.producto_id IS 'Producto que el proveedor vendió a la empresa en esta operación.';
COMMENT ON COLUMN detalle_compra.cantidad IS 'Cantidad de unidades que el proveedor vendió a la empresa.';
COMMENT ON COLUMN detalle_compra.precio_unitario IS 'Precio unitario al que el proveedor vendió el producto a la empresa.';
COMMENT ON COLUMN detalle_compra.subtotal IS 'Subtotal correspondiente a los productos vendidos por el proveedor (cantidad × precio_unitario).';

-- Comentarios en columnas de COMPROBANTES_VENTA
COMMENT ON COLUMN comprobantes_venta.cliente_id IS 'Cliente que realizó la compra. Referencia a la tabla de clientes.';
COMMENT ON COLUMN comprobantes_venta.numero_serie IS 'Serie del comprobante para la numeración de las compras realizadas por los clientes.';
COMMENT ON COLUMN comprobantes_venta.numero_comprobante IS 'Número único del comprobante de compra o venta emitido al cliente.';
COMMENT ON COLUMN comprobantes_venta.fecha_emision IS 'Fecha en la que el cliente realizó la compra o se emitió el comprobante de venta.';
COMMENT ON COLUMN comprobantes_venta.subtotal IS 'Importe subtotal de la compra realizada por el cliente antes de impuestos.';
COMMENT ON COLUMN comprobantes_venta.igv IS 'Impuesto general a las ventas (IGV) aplicado sobre la compra del cliente.';
COMMENT ON COLUMN comprobantes_venta.total IS 'Total a pagar por el cliente (subtotal + IGV) correspondiente a su compra.';
COMMENT ON COLUMN comprobantes_venta.tipo_comprobante IS 'Tipo de comprobante de compra o venta emitido: BOLETA o FACTURA.';
COMMENT ON COLUMN comprobantes_venta.estado IS 'Estado del comprobante de compra: PENDIENTE, PAGADA o CANCELADA.';

-- Comentarios en columnas de DETALLE_VENTA

COMMENT ON COLUMN detalle_venta.comprobante_id IS
'Comprobante de venta asociado a la compra realizada por el cliente.';

COMMENT ON COLUMN detalle_venta.producto_id IS
'Producto que el cliente compró o adquirió en la venta.';

COMMENT ON COLUMN detalle_venta.cantidad IS
'Cantidad de unidades compradas del producto por el cliente.';

COMMENT ON COLUMN detalle_venta.precio_unitario IS
'Precio unitario del producto comprado por el cliente al momento de la venta.';

COMMENT ON COLUMN detalle_venta.descuento IS
'Monto de descuento aplicado a la compra del cliente para este producto.';

COMMENT ON COLUMN detalle_venta.subtotal IS
'Subtotal correspondiente al producto comprado (cantidad × precio - descuento).';

COMMENT ON COLUMN detalle_venta.descuento_id IS
'Referencia al descuento aplicado en la compra del cliente, para auditoría.';

-- Comentarios en columnas de TRANSACCIONES
COMMENT ON COLUMN transacciones.comprobante_id IS 'Comprobante asociado a la transacción';
COMMENT ON COLUMN transacciones.metodo_pago_id IS 'Método de pago utilizado';
COMMENT ON COLUMN transacciones.tarjeta_id IS 'Tarjeta utilizada (si aplica)';
COMMENT ON COLUMN transacciones.plan_pago_id IS 'Plan de pago aplicado (si aplica)';
COMMENT ON COLUMN transacciones.monto IS 'Monto de la transacción para conciliación';
COMMENT ON COLUMN transacciones.fecha_transaccion IS 'Fecha y hora de la transacción';
COMMENT ON COLUMN transacciones.numero_operacion IS 'Número de operación para referencias';
COMMENT ON COLUMN transacciones.ultimos_digitos IS 'Últimos 4 dígitos de tarjeta para seguridad';
COMMENT ON COLUMN transacciones.estado IS 'Estado: PENDIENTE, COMPLETADA, etc.';

-- Comentarios en columnas de INVENTARIO_MOVIMIENTOS
COMMENT ON COLUMN inventario_movimientos.producto_id IS 'Producto afectado por el movimiento';
COMMENT ON COLUMN inventario_movimientos.tipo_movimiento IS 'Tipo: ENTRADA, SALIDA, AJUSTE';
COMMENT ON COLUMN inventario_movimientos.cantidad IS 'Cantidad movida para cálculos';
COMMENT ON COLUMN inventario_movimientos.stock_anterior IS 'Stock antes del movimiento para auditoría';
COMMENT ON COLUMN inventario_movimientos.stock_nuevo IS 'Stock después del movimiento';
COMMENT ON COLUMN inventario_movimientos.fecha_movimiento IS 'Fecha y hora del movimiento';
COMMENT ON COLUMN inventario_movimientos.motivo IS 'Motivo del movimiento para trazabilidad';
COMMENT ON COLUMN inventario_movimientos.usuario_id IS 'Usuario que realizó el movimiento';