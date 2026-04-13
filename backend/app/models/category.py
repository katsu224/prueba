"""
=========================================================
app/models/category.py
Modelo ORM para la tabla 'categories'.

Representa una categoría o familia de productos.
Permite organizar los productos en grupos lógicos
para facilitar la búsqueda y reportes.

Tabla: categories
Relaciones:
    - products: Productos que pertenecen a esta categoría
=========================================================
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    """
    Modelo de categoría de productos.

    Atributos:
        id: Identificador único UUID
        name: Nombre de la categoría (único)
        description: Descripción opcional
        created_at: Fecha de creación
        updated_at: Fecha de última modificación
    """

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la categoría",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Nombre de la categoría (único)",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción de la categoría",
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
    products = relationship(
        "Product",
        back_populates="category",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"
