"""
=========================================================
app/models/product.py
Modelo ORM para la tabla 'products'.

Representa un producto del catálogo maestro de inventario.
Contiene información estática del producto como SKU, nombre,
precio y punto de reorden.

NOTA IMPORTANTE: El stock actual NO se almacena en esta tabla.
Se calcula dinámicamente desde la tabla de movimientos de
inventario (principio de inmutabilidad del Kardex).

Tabla: products
Relaciones:
    - category: Categoría a la que pertenece
    - movements: Movimientos de inventario del producto
=========================================================
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    """
    Modelo de producto del inventario.

    Atributos:
        id: Identificador único UUID
        category_id: FK a la categoría del producto
        sku: Código único del producto (Stock Keeping Unit)
        name: Nombre del producto
        description: Descripción detallada
        unit_price: Precio unitario de referencia
        unit_measure: Unidad de medida (unidad, kg, litro, etc.)
        reorder_point: Cantidad mínima antes de reabastecer
        is_active: Si el producto está activo (soft delete)
        created_at: Fecha de creación
        updated_at: Fecha de última modificación
    """

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del producto",
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK a la categoría del producto",
    )
    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Código único del producto (SKU)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nombre del producto",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada del producto",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Precio unitario de referencia",
    )
    unit_measure: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unidad",
        comment="Unidad de medida (unidad, kg, litro, etc.)",
    )
    reorder_point: Mapped[int] = mapped_column(
        Integer,
        default=10,
        comment="Cantidad mínima antes de reabastecer",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Estado activo del producto (soft delete)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Fecha de creación",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Fecha de última modificación",
    )

    # --- Relaciones ---
    category = relationship(
        "Category",
        back_populates="products",
        lazy="selectin",
    )
    movements = relationship(
        "InventoryMovement",
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"
