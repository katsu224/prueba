"""
=========================================================
app/models/movement_type.py
Modelo ORM para la tabla 'movement_types'.

Representa los tipos de movimiento de inventario.
Cada tipo define si es una ENTRADA ('IN') o SALIDA ('OUT').

Tipos predefinidos:
    IN:  COMPRA, DEVOLUCION_CLIENTE, AJUSTE_POSITIVO, PRODUCCION
    OUT: VENTA, DEVOLUCION_PROVEEDOR, AJUSTE_NEGATIVO, MERMA

Tabla: movement_types
Relaciones:
    - movements: Movimientos de este tipo
=========================================================
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MovementType(Base):
    """
    Modelo de tipo de movimiento de inventario.

    Atributos:
        id: Identificador único UUID
        name: Nombre del tipo (COMPRA, VENTA, etc.)
        direction: Dirección del movimiento ('IN' o 'OUT')
        description: Descripción del tipo de movimiento
    """

    __tablename__ = "movement_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del tipo de movimiento",
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Nombre del tipo de movimiento",
    )
    direction: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Dirección: 'IN' (entrada) o 'OUT' (salida)",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción del tipo de movimiento",
    )

    # --- Relaciones ---
    movements = relationship(
        "InventoryMovement",
        back_populates="movement_type",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<MovementType(id={self.id}, name={self.name}, direction={self.direction})>"
