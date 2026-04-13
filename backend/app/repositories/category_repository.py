"""
=========================================================
app/repositories/category_repository.py
Repositorio de acceso a datos para categorías.

Encapsula todas las operaciones de base de datos
relacionadas con la tabla 'categories'.

Uso:
    cat_repo = CategoryRepository(db_session)
    categories = await cat_repo.get_all()
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    """
    Repositorio para operaciones CRUD de categorías.

    Atributos:
        db: Sesión asíncrona de SQLAlchemy.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Category]:
        """
        Obtiene todas las categorías con paginación.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.

        Returns:
            Lista de categorías.
        """
        query = select(Category).offset(skip).limit(limit).order_by(Category.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """
        Busca una categoría por su ID.

        Args:
            category_id: UUID de la categoría.

        Returns:
            Category si existe, None si no.
        """
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        """
        Busca una categoría por su nombre.

        Args:
            name: Nombre de la categoría.

        Returns:
            Category si existe, None si no.
        """
        query = select(Category).where(Category.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, category: Category) -> Category:
        """
        Crea una nueva categoría.

        Args:
            category: Instancia del modelo Category.

        Returns:
            Category creada con su ID generado.
        """
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def update(self, category_id: UUID, data: dict) -> Optional[Category]:
        """
        Actualiza una categoría existente.

        Args:
            category_id: UUID de la categoría a actualizar.
            data: Diccionario con los campos a actualizar.

        Returns:
            Category actualizada o None si no existe.
        """
        # Filtrar campos None para no sobrescribir con nulos
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(category_id)

        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(category_id)

    async def delete(self, category_id: UUID) -> bool:
        """
        Elimina una categoría por su ID.

        Args:
            category_id: UUID de la categoría a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        result = await self.db.execute(
            delete(Category).where(Category.id == category_id)
        )
        await self.db.flush()
        return result.rowcount > 0
