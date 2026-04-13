"""
=========================================================
app/repositories/product_repository.py
Repositorio de acceso a datos para productos.

Encapsula todas las operaciones de base de datos
relacionadas con la tabla 'products'. Incluye búsqueda
por SKU y filtrado por categoría.

Uso:
    prod_repo = ProductRepository(db_session)
    product = await prod_repo.get_by_sku("PROD-001")
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product


class ProductRepository:
    """
    Repositorio para operaciones CRUD de productos.

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

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
    ) -> list[Product]:
        """
        Obtiene productos con paginación y filtros opcionales.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.
            category_id: Filtrar por categoría (opcional).
            is_active: Filtrar por estado activo (default: True).

        Returns:
            Lista de productos filtrados y paginados.
        """
        query = select(Product).options(selectinload(Product.category))

        # Aplicar filtros opcionales
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        if category_id:
            query = query.where(Product.category_id == category_id)

        query = query.offset(skip).limit(limit).order_by(Product.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Busca un producto por su ID con su categoría cargada.

        Args:
            product_id: UUID del producto.

        Returns:
            Product con categoría cargada, o None.
        """
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Busca un producto por su SKU (código único).

        Args:
            sku: Código SKU del producto.

        Returns:
            Product si existe, None si no.
        """
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.sku == sku)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, product: Product) -> Product:
        """
        Crea un nuevo producto.

        Args:
            product: Instancia del modelo Product.

        Returns:
            Product creado con su ID generado.
        """
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def update(self, product_id: UUID, data: dict) -> Optional[Product]:
        """
        Actualiza un producto existente.

        Args:
            product_id: UUID del producto a actualizar.
            data: Diccionario con los campos a actualizar.

        Returns:
            Product actualizado o None si no existe.
        """
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(product_id)

        await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(product_id)

    async def deactivate(self, product_id: UUID) -> Optional[Product]:
        """
        Desactiva un producto (soft delete).
        No se eliminan productos para mantener la integridad
        del Kardex y los movimientos históricos.

        Args:
            product_id: UUID del producto.

        Returns:
            Product desactivado o None.
        """
        return await self.update(product_id, {"is_active": False})
