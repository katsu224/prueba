-- =========================================================
-- SCHEMA: Sistema de Inventario con Kardex
-- Base de datos: PostgreSQL (Supabase)
-- Descripción: Script completo para crear todas las tablas,
--              vistas, índices, triggers y datos iniciales
--              del sistema de inventario con Kardex.
-- Autor: Generado automáticamente
-- Fecha: 2026-04-13
-- =========================================================

-- ---------------------------------------------------------
-- 1. Extensión para generación de UUID
-- ---------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------
-- 2. Tabla de Usuarios (para autenticación JWT)
-- Almacena las credenciales y datos básicos de los usuarios
-- del sistema.
-- ---------------------------------------------------------
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 3. Tabla de Categorías
-- Clasificación de productos por tipo o familia.
-- ---------------------------------------------------------
CREATE TABLE categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 4. Tabla de Productos
-- Catálogo maestro de productos con información estática.
-- El stock actual NO se almacena aquí, se calcula desde
-- los movimientos (principio de inmutabilidad del Kardex).
-- ---------------------------------------------------------
CREATE TABLE products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    unit_price NUMERIC(12, 2) NOT NULL DEFAULT 0,
    unit_measure TEXT NOT NULL DEFAULT 'unidad',
    reorder_point INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 5. Tabla de Tipos de Movimiento
-- Define los tipos de entrada/salida posibles.
-- direction: 'IN' = entrada, 'OUT' = salida
-- ---------------------------------------------------------
CREATE TABLE movement_types (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    direction TEXT NOT NULL CHECK (direction IN ('IN', 'OUT')),
    description TEXT
);

-- ---------------------------------------------------------
-- 6. Tabla de Movimientos de Inventario (EL KARDEX)
-- Registro inmutable de cada movimiento de stock.
-- NUNCA se editan ni eliminan registros aquí.
-- Para correcciones, se crea un movimiento de ajuste.
-- ---------------------------------------------------------
CREATE TABLE inventory_movements (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    movement_type_id UUID NOT NULL REFERENCES movement_types(id) ON DELETE RESTRICT,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    quantity NUMERIC(12, 4) NOT NULL CHECK (quantity > 0),
    unit_cost NUMERIC(12, 2) NOT NULL DEFAULT 0,
    reference_number TEXT,
    notes TEXT,
    movement_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- ÍNDICES para optimización de consultas
-- =========================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_movements_product ON inventory_movements(product_id);
CREATE INDEX idx_movements_date ON inventory_movements(movement_date);
CREATE INDEX idx_movements_type ON inventory_movements(movement_type_id);
CREATE INDEX idx_movements_user ON inventory_movements(user_id);

-- =========================================================
-- VISTA: Stock actual por producto
-- Calcula el inventario actual sumando todas las entradas
-- y restando todas las salidas de cada producto.
-- =========================================================
CREATE OR REPLACE VIEW current_stock AS
SELECT
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    p.unit_measure,
    p.unit_price,
    p.reorder_point,
    c.name AS category_name,
    COALESCE(
        SUM(
            CASE
                WHEN mt.direction = 'IN' THEN im.quantity
                WHEN mt.direction = 'OUT' THEN -im.quantity
                ELSE 0
            END
        ), 0
    ) AS current_quantity,
    COALESCE(
        SUM(
            CASE
                WHEN mt.direction = 'IN' THEN im.quantity * im.unit_cost
                WHEN mt.direction = 'OUT' THEN -(im.quantity * im.unit_cost)
                ELSE 0
            END
        ), 0
    ) AS total_value
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN inventory_movements im ON p.id = im.product_id
LEFT JOIN movement_types mt ON im.movement_type_id = mt.id
WHERE p.is_active = TRUE
GROUP BY p.id, p.sku, p.name, p.unit_measure, p.unit_price, p.reorder_point, c.name;

-- =========================================================
-- VISTA: Kardex detallado por producto
-- Muestra cada movimiento con su balance acumulado
-- (running balance) calculado con window functions.
-- =========================================================
CREATE OR REPLACE VIEW kardex_detail AS
SELECT
    im.id AS movement_id,
    im.product_id,
    p.sku,
    p.name AS product_name,
    mt.name AS movement_type,
    mt.direction,
    im.quantity,
    im.unit_cost,
    (im.quantity * im.unit_cost) AS total_cost,
    im.reference_number,
    im.notes,
    im.movement_date,
    u.username AS registered_by,
    -- Balance acumulado (running total) por producto
    SUM(
        CASE
            WHEN mt.direction = 'IN' THEN im.quantity
            WHEN mt.direction = 'OUT' THEN -im.quantity
            ELSE 0
        END
    ) OVER (
        PARTITION BY im.product_id
        ORDER BY im.movement_date, im.created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_balance
FROM inventory_movements im
JOIN products p ON im.product_id = p.id
JOIN movement_types mt ON im.movement_type_id = mt.id
LEFT JOIN users u ON im.user_id = u.id
ORDER BY im.product_id, im.movement_date;

-- =========================================================
-- DATOS INICIALES: Tipos de movimiento predefinidos
-- =========================================================
INSERT INTO movement_types (name, direction, description) VALUES
    ('COMPRA', 'IN', 'Entrada por compra a proveedor'),
    ('DEVOLUCION_CLIENTE', 'IN', 'Entrada por devolución de cliente'),
    ('AJUSTE_POSITIVO', 'IN', 'Ajuste positivo por inventario físico'),
    ('PRODUCCION', 'IN', 'Entrada por producción interna'),
    ('VENTA', 'OUT', 'Salida por venta a cliente'),
    ('DEVOLUCION_PROVEEDOR', 'OUT', 'Salida por devolución a proveedor'),
    ('AJUSTE_NEGATIVO', 'OUT', 'Ajuste negativo por inventario físico'),
    ('MERMA', 'OUT', 'Salida por producto dañado o caducado'),
    ('CONSUMO_INTERNO', 'OUT', 'Salida por uso interno de la empresa');

-- =========================================================
-- FUNCIÓN Y TRIGGER: Actualización automática de updated_at
-- Se ejecuta automáticamente al modificar un registro.
-- =========================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger para tabla users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para tabla products
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para tabla categories
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
