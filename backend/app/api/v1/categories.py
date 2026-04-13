"""
=========================================================
app/api/v1/categories.py
Endpoints de gestión de categorías.

Endpoints:
    GET    /           → Listar categorías
    GET    /{id}       → Obtener categoría por ID
    POST   /           → Crear categoría
    PUT    /{id}       → Actualizar categoría
    DELETE /{id}       → Eliminar categoría

Todos los endpoints requieren autenticación JWT.
=========================================================
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter()


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Listar categorías",
    description="Obtiene todas las categorías con paginación.",
)
async def get_categories(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna todas las categorías paginadas."""
    service = CategoryService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Obtener categoría",
    description="Obtiene una categoría por su ID.",
)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna una categoría específica."""
    service = CategoryService(db)
    return await service.get_by_id(category_id)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría de productos.",
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva categoría.

    - **name**: Nombre único de la categoría
    - **description**: Descripción opcional
    """
    service = CategoryService(db)
    return await service.create(data)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Actualizar categoría",
    description="Actualiza una categoría existente.",
)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Actualiza los datos de una categoría."""
    service = CategoryService(db)
    return await service.update(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría",
    description="Elimina una categoría por su ID.",
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Elimina una categoría. Los productos asociados quedarán sin categoría."""
    service = CategoryService(db)
    await service.delete(category_id)
