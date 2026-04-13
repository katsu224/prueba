"""
=========================================================
app/api/v1/movements.py
Endpoints de movimientos de inventario.

Endpoints:
    GET  /types    → Listar tipos de movimiento disponibles
    GET  /         → Listar movimientos (con filtros)
    GET  /{id}     → Obtener movimiento por ID
    POST /         → Registrar nuevo movimiento

Todos los endpoints requieren autenticación JWT.
Los movimientos son INMUTABLES: no hay PUT ni DELETE.
=========================================================
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.inventory_movement import MovementCreate, MovementResponse
from app.schemas.movement_type import MovementTypeResponse
from app.services.movement_service import MovementService

router = APIRouter()


@router.get(
    "/types",
    response_model=List[MovementTypeResponse],
    summary="Listar tipos de movimiento",
    description="Obtiene todos los tipos de movimiento disponibles (COMPRA, VENTA, etc.).",
)
async def get_movement_types(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Retorna los tipos de movimiento disponibles.
    Cada tipo tiene una dirección: IN (entrada) o OUT (salida).
    """
    service = MovementService(db)
    return await service.get_movement_types()


@router.get(
    "/",
    response_model=List[MovementResponse],
    summary="Listar movimientos",
    description="Obtiene movimientos de inventario con filtros y paginación.",
)
async def get_movements(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros"),
    product_id: Optional[UUID] = Query(None, description="Filtrar por producto"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna movimientos de inventario filtrados y paginados."""
    service = MovementService(db)
    return await service.get_all(skip=skip, limit=limit, product_id=product_id)


@router.get(
    "/{movement_id}",
    response_model=MovementResponse,
    summary="Obtener movimiento",
    description="Obtiene un movimiento de inventario por su ID.",
)
async def get_movement(
    movement_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna un movimiento específico con producto y tipo cargados."""
    service = MovementService(db)
    return await service.get_by_id(movement_id)


@router.post(
    "/",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimiento",
    description=(
        "Registra un nuevo movimiento de inventario. "
        "Para salidas (OUT), se valida que haya stock suficiente."
    ),
)
async def create_movement(
    data: MovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registra un nuevo movimiento de inventario.

    - **product_id**: ID del producto (obligatorio)
    - **movement_type_id**: ID del tipo de movimiento (obligatorio)
    - **quantity**: Cantidad (positiva, obligatoria)
    - **unit_cost**: Costo unitario (opcional, default 0)
    - **reference_number**: Número de factura/orden (opcional)
    - **notes**: Notas adicionales (opcional)

    IMPORTANTE: Para movimientos de salida (VENTA, MERMA, etc.),
    se valida que el stock actual sea suficiente.
    """
    service = MovementService(db)
    return await service.create(data, user_id=current_user.id)
