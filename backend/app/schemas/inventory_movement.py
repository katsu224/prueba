"""
=========================================================
app/schemas/inventory_movement.py
Schemas Pydantic para movimientos de inventario.

Define los modelos de validación para:
- MovementCreate: Registrar un nuevo movimiento
- MovementResponse: Datos del movimiento en respuestas

NOTA: La cantidad siempre es positiva. La dirección
(entrada/salida) la determina el tipo de movimiento.
=========================================================
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.movement_type import MovementTypeResponse
from app.schemas.product import ProductResponse


class MovementCreate(BaseModel):
    """
    Schema para registrar un nuevo movimiento de inventario.
    La cantidad debe ser positiva; la dirección la define el tipo.
    """
    product_id: UUID = Field(
        ...,
        description="ID del producto involucrado",
    )
    movement_type_id: UUID = Field(
        ...,
        description="ID del tipo de movimiento (COMPRA, VENTA, etc.)",
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Cantidad de unidades (siempre positiva)",
        examples=[100],
    )
    unit_cost: Decimal = Field(
        default=0,
        ge=0,
        description="Costo unitario al momento del movimiento",
        examples=[25.50],
    )
    reference_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Número de referencia (factura, orden, etc.)",
        examples=["FAC-2026-001"],
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notas adicionales del movimiento",
        examples=["Compra de reabastecimiento mensual"],
    )
    movement_date: Optional[datetime] = Field(
        None,
        description="Fecha del movimiento (si no se especifica, usa la actual)",
    )


class MovementResponse(BaseModel):
    """Schema de respuesta con datos completos del movimiento."""
    id: UUID
    product_id: UUID
    movement_type_id: UUID
    user_id: Optional[UUID] = None
    quantity: Decimal
    unit_cost: Decimal
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    movement_date: datetime
    created_at: datetime
    product: Optional[ProductResponse] = None
    movement_type: Optional[MovementTypeResponse] = None

    class Config:
        from_attributes = True
