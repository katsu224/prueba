"""
=========================================================
app/schemas/category.py
Schemas Pydantic para categorías de productos.

Define los modelos de validación para:
- CategoryCreate: Crear nueva categoría
- CategoryUpdate: Actualizar categoría existente
- CategoryResponse: Datos de categoría en respuestas
=========================================================
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Schema para crear una nueva categoría."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre de la categoría (debe ser único)",
        examples=["Electrónicos"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción de la categoría",
        examples=["Productos electrónicos y accesorios"],
    )


class CategoryUpdate(BaseModel):
    """
    Schema para actualizar una categoría.
    Todos los campos son opcionales (actualización parcial).
    """
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Nuevo nombre de la categoría",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Nueva descripción",
    )


class CategoryResponse(BaseModel):
    """Schema de respuesta con datos de la categoría."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
