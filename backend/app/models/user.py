"""
=========================================================
app/models/user.py
Modelo ORM para la tabla 'users'.

Representa un usuario del sistema con credenciales para
autenticación JWT. Incluye campos para control de acceso
(is_active, is_admin) y timestamps de auditoría.

Tabla: users
Relaciones:
    - inventory_movements: Movimientos registrados por el usuario
=========================================================
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    Modelo de usuario del sistema.

    Atributos:
        id: Identificador único UUID
        email: Correo electrónico (único)
        username: Nombre de usuario (único)
        hashed_password: Contraseña hasheada con bcrypt
        full_name: Nombre completo del usuario
        is_active: Si el usuario está activo (soft delete)
        is_admin: Si el usuario tiene permisos de administrador
        created_at: Fecha de creación
        updated_at: Fecha de última modificación
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del usuario",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Correo electrónico único",
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Nombre de usuario único",
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Contraseña hasheada con bcrypt",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre completo del usuario",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Estado activo del usuario",
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Si el usuario es administrador",
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
    movements = relationship(
        "InventoryMovement",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
