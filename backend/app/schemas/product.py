"""
=========================================================
app/schemas/product.py
Schemas Pydantic para productos del inventario.

Define los modelos de validación para:
- ProductCreate: Registrar nuevo producto
- ProductUpdate: Actualizar producto existente
- ProductResponse: Datos del producto en respuestas
=========================================================
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse


class ProductCreate(BaseModel):
    """
    Schema para crear un nuevo producto.
    El SKU es obligatorio y debe ser único en el sistema.
    """
    category_id: Optional[UUID] = Field(
        None,
        description="ID de la categoría del producto",
    )
    sku: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Código único del producto (SKU)",
        examples=["PROD-001"],
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nombre del producto",
        examples=["Teclado mecánico RGB"],
    )
    description: Optional[str] = Field(
        None,
        description="Descripción detallada del producto",
        examples=["Teclado mecánico con iluminación RGB y switches Cherry MX"],
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Precio unitario de referencia",
        examples=[59.99],
    )
    unit_measure: str = Field(
        default="unidad",
        max_length=50,
        description="Unidad de medida",
        examples=["unidad", "kg", "litro"],
    )
    reorder_point: int = Field(
        default=10,
        ge=0,
        description="Cantidad mínima antes de reabastecer",
        examples=[10],
    )


class ProductUpdate(BaseModel):
    """
    Schema para actualizar un producto.
    Todos los campos son opcionales (actualización parcial).
    """
    category_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    unit_measure: Optional[str] = Field(None, max_length=50)
    reorder_point: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema de respuesta con datos del producto."""
    id: UUID
    category_id: Optional[UUID] = None
    sku: str
    name: str
    description: Optional[str] = None
    unit_price: Decimal
    unit_measure: str
    reorder_point: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
