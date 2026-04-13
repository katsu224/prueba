"""
=========================================================
app/services/product_service.py
Servicio de gestión de productos del inventario.

Contiene la lógica de negocio para:
- Crear productos validando SKU único
- Listar productos con filtros
- Actualizar productos
- Desactivar productos (soft delete)

Reglas de negocio:
- El SKU debe ser único en todo el sistema
- Los productos NO se eliminan, se desactivan (soft delete)
  para mantener la integridad del Kardex histórico
- Un producto desactivado no aparece en listados por defecto

Uso:
    prod_service = ProductService(db_session)
    product = await prod_service.create(ProductCreate(...))
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, NotFoundError
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse


class ProductService:
    """
    Servicio de lógica de negocio para productos.

    Atributos:
        product_repo: Repositorio de productos.
        category_repo: Repositorio de categorías (para validaciones).
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.product_repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
    ) -> list[ProductResponse]:
        """
        Obtiene productos con filtros y paginación.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.
            category_id: Filtrar por categoría.
            is_active: Filtrar por estado.

        Returns:
            Lista de ProductResponse.
        """
        products = await self.product_repo.get_all(
            skip=skip,
            limit=limit,
            category_id=category_id,
            is_active=is_active,
        )
        return [ProductResponse.model_validate(p) for p in products]

    async def get_by_id(self, product_id: UUID) -> ProductResponse:
        """
        Obtiene un producto por su ID.

        Args:
            product_id: UUID del producto.

        Returns:
            ProductResponse con los datos.

        Raises:
            NotFoundError: Si el producto no existe.
        """
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto", str(product_id))
        return ProductResponse.model_validate(product)

    async def create(self, data: ProductCreate) -> ProductResponse:
        """
        Crea un nuevo producto.

        Valida que el SKU sea único y que la categoría exista
        (si se especifica). El stock inicial es 0; se debe
        registrar un movimiento de COMPRA para agregar stock.

        Args:
            data: Datos validados del producto.

        Returns:
            ProductResponse del producto creado.

        Raises:
            DuplicateError: Si el SKU ya existe.
            NotFoundError: Si la categoría no existe.
        """
        # Verificar unicidad del SKU
        existing = await self.product_repo.get_by_sku(data.sku)
        if existing:
            raise DuplicateError("Producto", "SKU", data.sku)

        # Verificar que la categoría existe (si se especifica)
        if data.category_id:
            category = await self.category_repo.get_by_id(data.category_id)
            if not category:
                raise NotFoundError("Categoría", str(data.category_id))

        product = Product(
            category_id=data.category_id,
            sku=data.sku,
            name=data.name,
            description=data.description,
            unit_price=data.unit_price,
            unit_measure=data.unit_measure,
            reorder_point=data.reorder_point,
        )

        created = await self.product_repo.create(product)
        return ProductResponse.model_validate(created)

    async def update(
        self, product_id: UUID, data: ProductUpdate
    ) -> ProductResponse:
        """
        Actualiza un producto existente.

        Args:
            product_id: UUID del producto a actualizar.
            data: Datos a actualizar (campos opcionales).

        Returns:
            ProductResponse actualizado.

        Raises:
            NotFoundError: Si el producto no existe.
        """
        existing = await self.product_repo.get_by_id(product_id)
        if not existing:
            raise NotFoundError("Producto", str(product_id))

        # Si se cambia la categoría, verificar que existe
        if data.category_id:
            category = await self.category_repo.get_by_id(data.category_id)
            if not category:
                raise NotFoundError("Categoría", str(data.category_id))

        updated = await self.product_repo.update(
            product_id, data.model_dump(exclude_unset=True)
        )
        return ProductResponse.model_validate(updated)

    async def deactivate(self, product_id: UUID) -> ProductResponse:
        """
        Desactiva un producto (soft delete).

        Los productos no se eliminan permanentemente para
        mantener la integridad del Kardex histórico.

        Args:
            product_id: UUID del producto.

        Returns:
            ProductResponse del producto desactivado.

        Raises:
            NotFoundError: Si el producto no existe.
        """
        existing = await self.product_repo.get_by_id(product_id)
        if not existing:
            raise NotFoundError("Producto", str(product_id))

        deactivated = await self.product_repo.deactivate(product_id)
        return ProductResponse.model_validate(deactivated)
