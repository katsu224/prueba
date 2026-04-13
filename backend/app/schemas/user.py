"""
=========================================================
app/schemas/user.py
Schemas Pydantic para usuarios y autenticación.

Define los modelos de validación para:
- UserCreate: Registro de nuevo usuario
- UserLogin: Inicio de sesión
- UserResponse: Datos del usuario en respuestas
- TokenResponse: Token JWT retornado al autenticarse
=========================================================
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Schema para crear un nuevo usuario.
    Se valida que el email y username sean únicos en el servicio.
    """
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Correo electrónico del usuario",
        examples=["admin@inventario.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre de usuario único",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Contraseña (mínimo 6 caracteres)",
        examples=["password123"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Nombre completo del usuario",
        examples=["Juan Pérez"],
    )


class UserLogin(BaseModel):
    """
    Schema para inicio de sesión.
    Acepta username o email con contraseña.
    """
    username: str = Field(
        ...,
        description="Nombre de usuario o email",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        description="Contraseña del usuario",
        examples=["password123"],
    )


class UserResponse(BaseModel):
    """
    Schema de respuesta con datos del usuario.
    NUNCA incluye la contraseña hasheada.
    """
    id: UUID
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Schema de respuesta con el token JWT.
    Retornado al hacer login exitoso.
    """
    access_token: str = Field(
        ...,
        description="Token JWT de acceso",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token (siempre 'bearer')",
    )
    user: UserResponse = Field(
        ...,
        description="Datos del usuario autenticado",
    )
