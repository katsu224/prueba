"""
=========================================================
app/services/category_service.py
Servicio de gestión de categorías de productos.

Contiene la lógica de negocio para:
- Crear categorías validando unicidad del nombre
- Listar categorías con paginación
- Actualizar y eliminar categorías

Uso:
    cat_service = CategoryService(db_session)
    category = await cat_service.create(CategoryCreate(name="Electrónicos"))
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, NotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    """
    Servicio de lógica de negocio para categorías.

    Atributos:
        category_repo: Repositorio de categorías.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.category_repo = CategoryRepository(db)

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[CategoryResponse]:
        """
        Obtiene todas las categorías con paginación.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.

        Returns:
            Lista de CategoryResponse.
        """
        categories = await self.category_repo.get_all(skip=skip, limit=limit)
        return [CategoryResponse.model_validate(c) for c in categories]

    async def get_by_id(self, category_id: UUID) -> CategoryResponse:
        """
        Obtiene una categoría por su ID.

        Args:
            category_id: UUID de la categoría.

        Returns:
            CategoryResponse con los datos.

        Raises:
            NotFoundError: Si la categoría no existe.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundError("Categoría", str(category_id))
        return CategoryResponse.model_validate(category)

    async def create(self, data: CategoryCreate) -> CategoryResponse:
        """
        Crea una nueva categoría.

        Args:
            data: Datos validados de la categoría.

        Returns:
            CategoryResponse de la categoría creada.

        Raises:
            DuplicateError: Si ya existe una categoría con ese nombre.
        """
        # Verificar unicidad del nombre
        existing = await self.category_repo.get_by_name(data.name)
        if existing:
            raise DuplicateError("Categoría", "nombre", data.name)

        category = Category(
            name=data.name,
            description=data.description,
        )
        created = await self.category_repo.create(category)
        return CategoryResponse.model_validate(created)

    async def update(
        self, category_id: UUID, data: CategoryUpdate
    ) -> CategoryResponse:
        """
        Actualiza una categoría existente.

        Args:
            category_id: UUID de la categoría a actualizar.
            data: Datos a actualizar (campos opcionales).

        Returns:
            CategoryResponse actualizada.

        Raises:
            NotFoundError: Si la categoría no existe.
            DuplicateError: Si el nuevo nombre ya está en uso.
        """
        # Verificar que la categoría existe
        existing = await self.category_repo.get_by_id(category_id)
        if not existing:
            raise NotFoundError("Categoría", str(category_id))

        # Si se cambia el nombre, verificar unicidad
        if data.name and data.name != existing.name:
            name_taken = await self.category_repo.get_by_name(data.name)
            if name_taken:
                raise DuplicateError("Categoría", "nombre", data.name)

        updated = await self.category_repo.update(
            category_id, data.model_dump(exclude_unset=True)
        )
        return CategoryResponse.model_validate(updated)

    async def delete(self, category_id: UUID) -> bool:
        """
        Elimina una categoría.

        Args:
            category_id: UUID de la categoría a eliminar.

        Returns:
            True si se eliminó correctamente.

        Raises:
            NotFoundError: Si la categoría no existe.
        """
        existing = await self.category_repo.get_by_id(category_id)
        if not existing:
            raise NotFoundError("Categoría", str(category_id))

        return await self.category_repo.delete(category_id)
