"""
=========================================================
app/api/v1/products.py
Endpoints de gestión de productos.

Endpoints:
    GET    /           → Listar productos (con filtros)
    GET    /{id}       → Obtener producto por ID
    POST   /           → Crear producto
    PUT    /{id}       → Actualizar producto
    DELETE /{id}       → Desactivar producto (soft delete)

Todos los endpoints requieren autenticación JWT.
NOTA: DELETE no elimina permanentemente, solo desactiva
el producto para mantener la integridad del Kardex.
=========================================================
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter()


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Listar productos",
    description="Obtiene productos con filtros opcionales y paginación.",
)
async def get_products(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    category_id: Optional[UUID] = Query(None, description="Filtrar por categoría"),
    is_active: Optional[bool] = Query(True, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Retorna productos filtrados y paginados.

    - **category_id**: Filtra por UUID de la categoría
    - **is_active**: True = activos, False = inactivos, None = todos
    """
    service = ProductService(db)
    return await service.get_all(
        skip=skip, limit=limit, category_id=category_id, is_active=is_active
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener producto",
    description="Obtiene un producto por su ID.",
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna un producto específico con su categoría."""
    service = ProductService(db)
    return await service.get_by_id(product_id)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Registra un nuevo producto en el catálogo.",
)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Crea un nuevo producto.

    - **sku**: Código único del producto (obligatorio)
    - **name**: Nombre del producto (obligatorio)
    - **unit_price**: Precio unitario (obligatorio)
    - **category_id**: Categoría del producto (opcional)
    """
    service = ProductService(db)
    return await service.create(data)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar producto",
    description="Actualiza un producto existente.",
)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Actualiza los datos de un producto (no incluye el SKU)."""
    service = ProductService(db)
    return await service.update(product_id, data)


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Desactivar producto",
    description="Desactiva un producto (soft delete). No se elimina permanentemente.",
)
async def deactivate_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Desactiva un producto (soft delete).
    El producto no se elimina para mantener la integridad
    del Kardex y los movimientos históricos.
    """
    service = ProductService(db)
    return await service.deactivate(product_id)
