"""
=========================================================
app/schemas/kardex.py
Schemas Pydantic para el Kardex y stock actual.

Define los modelos de respuesta para:
- KardexEntry: Una línea del kardex (un movimiento con balance)
- KardexResponse: Kardex completo de un producto
- CurrentStockResponse: Stock actual de un producto
- LowStockResponse: Productos por debajo del punto de reorden
=========================================================
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class KardexEntry(BaseModel):
    """
    Representa una línea individual del Kardex.
    Incluye los datos del movimiento y el balance acumulado.
    """
    movement_id: UUID
    movement_date: datetime
    movement_type: str = Field(
        ...,
        description="Nombre del tipo de movimiento (COMPRA, VENTA, etc.)",
    )
    direction: str = Field(
        ...,
        description="Dirección: 'IN' (entrada) o 'OUT' (salida)",
    )
    quantity: Decimal = Field(
        ...,
        description="Cantidad del movimiento",
    )
    unit_cost: Decimal = Field(
        ...,
        description="Costo unitario del movimiento",
    )
    total_cost: Decimal = Field(
        ...,
        description="Costo total (quantity * unit_cost)",
    )
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    registered_by: Optional[str] = Field(
        None,
        description="Username del usuario que registró",
    )
    running_balance: Decimal = Field(
        ...,
        description="Balance acumulado después de este movimiento",
    )


class KardexResponse(BaseModel):
    """
    Respuesta completa del Kardex para un producto.
    Incluye datos del producto y todas las líneas del kardex.
    """
    product_id: UUID
    product_name: str
    sku: str
    unit_measure: str
    current_stock: Decimal = Field(
        ...,
        description="Stock actual calculado",
    )
    entries: List[KardexEntry] = Field(
        default_factory=list,
        description="Lista de movimientos ordenados por fecha",
    )


class CurrentStockResponse(BaseModel):
    """
    Stock actual de un producto con datos resumidos.
    Se calcula dinámicamente desde los movimientos.
    """
    product_id: UUID
    sku: str
    product_name: str
    category_name: Optional[str] = None
    unit_measure: str
    unit_price: Decimal
    reorder_point: int
    current_quantity: Decimal = Field(
        ...,
        description="Cantidad actual en inventario",
    )
    total_value: Decimal = Field(
        ...,
        description="Valor total del inventario de este producto",
    )
    is_low_stock: bool = Field(
        ...,
        description="True si está por debajo del punto de reorden",
    )


class LowStockResponse(BaseModel):
    """Lista de productos con stock bajo."""
    count: int = Field(
        ...,
        description="Cantidad de productos con stock bajo",
    )
    products: List[CurrentStockResponse] = Field(
        default_factory=list,
        description="Productos por debajo del punto de reorden",
    )
