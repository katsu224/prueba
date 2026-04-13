"""
=========================================================
app/api/v1/kardex.py
Endpoints del Kardex y consulta de stock.

Endpoints:
    GET /{product_id}      → Kardex completo de un producto
    GET /stock/{product_id} → Stock actual de un producto
    GET /dashboard/stock    → Stock de todos los productos
    GET /dashboard/low-stock → Productos con stock bajo

Todos los endpoints requieren autenticación JWT.
=========================================================
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.kardex import (
    CurrentStockResponse,
    KardexResponse,
    LowStockResponse,
)
from app.services.kardex_service import KardexService

router = APIRouter()


@router.get(
    "/dashboard/stock",
    response_model=List[CurrentStockResponse],
    summary="Stock de todos los productos",
    description="Obtiene el stock actual de todos los productos activos.",
)
async def get_all_stock(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Retorna el stock actual de todos los productos activos.
    Usado para el dashboard principal.
    """
    service = KardexService(db)
    return await service.get_all_stock()


@router.get(
    "/dashboard/low-stock",
    response_model=LowStockResponse,
    summary="Productos con stock bajo",
    description="Obtiene los productos por debajo del punto de reorden.",
)
async def get_low_stock(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Retorna productos con stock por debajo del punto de reorden.
    Usado para alertas del dashboard.
    """
    service = KardexService(db)
    return await service.get_low_stock()


@router.get(
    "/stock/{product_id}",
    response_model=CurrentStockResponse,
    summary="Stock de un producto",
    description="Obtiene el stock actual calculado de un producto.",
)
async def get_product_stock(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna el stock actual de un producto específico."""
    service = KardexService(db)
    return await service.get_product_stock(product_id)


@router.get(
    "/{product_id}",
    response_model=KardexResponse,
    summary="Kardex de un producto",
    description=(
        "Obtiene el Kardex completo de un producto con "
        "todos los movimientos y balance acumulado."
    ),
)
async def get_kardex(
    product_id: UUID,
    date_from: Optional[datetime] = Query(
        None,
        description="Fecha inicial del filtro (ISO 8601)",
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Fecha final del filtro (ISO 8601)",
    ),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Retorna el Kardex completo de un producto.

    El Kardex muestra cada movimiento (entrada/salida) con:
    - Tipo de movimiento
    - Cantidad y costo unitario
    - Balance acumulado (running balance)
    - Usuario que lo registró
    - Referencia y notas

    Se puede filtrar por rango de fechas con date_from y date_to.
    """
    service = KardexService(db)
    return await service.get_kardex(
        product_id=product_id,
        date_from=date_from,
        date_to=date_to,
    )
