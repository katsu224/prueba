"""
=========================================================
app/models/inventory_movement.py
Modelo ORM para la tabla 'inventory_movements'.

Este es el CORAZÓN del sistema Kardex. Cada registro
representa un movimiento de inventario (entrada o salida).

PRINCIPIO DE INMUTABILIDAD:
Los registros de movimientos NUNCA se editan ni eliminan.
Si se comete un error, se registra un movimiento de ajuste
para corregirlo. Esto garantiza la trazabilidad completa
del inventario.

Tabla: inventory_movements
Relaciones:
    - product: Producto afectado por el movimiento
    - movement_type: Tipo de movimiento (COMPRA, VENTA, etc.)
    - user: Usuario que registró el movimiento
=========================================================
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InventoryMovement(Base):
    """
    Modelo de movimiento de inventario (registro del Kardex).

    Atributos:
        id: Identificador único UUID
        product_id: FK al producto involucrado
        movement_type_id: FK al tipo de movimiento
        user_id: FK al usuario que registró el movimiento
        quantity: Cantidad de unidades movidas (siempre positiva)
        unit_cost: Costo unitario al momento del movimiento
        reference_number: Número de referencia (factura, orden, etc.)
        notes: Notas adicionales del movimiento
        movement_date: Fecha en que ocurrió el movimiento
        created_at: Fecha de creación del registro
    """

    __tablename__ = "inventory_movements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del movimiento",
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="FK al producto involucrado",
    )
    movement_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("movement_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="FK al tipo de movimiento",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK al usuario que registró",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad de unidades (siempre positiva)",
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Costo unitario al momento del movimiento",
    )
    reference_number: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Número de referencia (factura, orden, etc.)",
    )
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionales del movimiento",
    )
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="Fecha en que ocurrió el movimiento",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Fecha de creación del registro",
    )

    # --- Relaciones ---
    product = relationship(
        "Product",
        back_populates="movements",
        lazy="selectin",
    )
    movement_type = relationship(
        "MovementType",
        back_populates="movements",
        lazy="selectin",
    )
    user = relationship(
        "User",
        back_populates="movements",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryMovement(id={self.id}, "
            f"product_id={self.product_id}, "
            f"quantity={self.quantity})>"
        )
