"""
=========================================================
app/services/kardex_service.py
Servicio de generación del Kardex y consulta de stock.

Contiene la lógica de negocio para:
- Generar el Kardex completo de un producto con balance acumulado
- Consultar el stock actual de un producto
- Obtener el resumen de stock de todos los productos
- Detectar productos con stock bajo

El Kardex es el reporte central del sistema. Muestra cada
movimiento de un producto con su balance acumulado (running
balance), permitiendo rastrear cómo llegó el inventario
a su nivel actual.

Uso:
    kardex_service = KardexService(db_session)
    kardex = await kardex_service.get_kardex(product_id)
=========================================================
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.movement_repository import MovementRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.kardex import (
    CurrentStockResponse,
    KardexEntry,
    KardexResponse,
    LowStockResponse,
)


class KardexService:
    """
    Servicio para generación de Kardex y consultas de stock.

    Atributos:
        movement_repo: Repositorio de movimientos.
        product_repo: Repositorio de productos.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.movement_repo = MovementRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_kardex(
        self,
        product_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> KardexResponse:
        """
        Genera el Kardex completo de un producto.

        Incluye todos los movimientos ordenados por fecha con
        el balance acumulado (running balance) después de cada
        movimiento.

        Args:
            product_id: UUID del producto.
            date_from: Fecha inicial del filtro (opcional).
            date_to: Fecha final del filtro (opcional).

        Returns:
            KardexResponse con todos los movimientos y balance.

        Raises:
            NotFoundError: Si el producto no existe.
        """
        # Verificar que el producto existe
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto", str(product_id))

        # Obtener los movimientos del kardex con balance acumulado
        kardex_data = await self.movement_repo.get_kardex(
            product_id=product_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Obtener stock actual
        current_stock = await self.movement_repo.get_current_stock(product_id)

        # Convertir datos a schemas
        entries = [KardexEntry(**entry) for entry in kardex_data]

        return KardexResponse(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            unit_measure=product.unit_measure,
            current_stock=current_stock,
            entries=entries,
        )

    async def get_product_stock(self, product_id: UUID) -> CurrentStockResponse:
        """
        Obtiene el stock actual de un producto específico.

        Args:
            product_id: UUID del producto.

        Returns:
            CurrentStockResponse con el stock calculado.

        Raises:
            NotFoundError: Si el producto no existe.
        """
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto", str(product_id))

        current_qty = await self.movement_repo.get_current_stock(product_id)

        return CurrentStockResponse(
            product_id=product.id,
            sku=product.sku,
            product_name=product.name,
            category_name=product.category.name if product.category else None,
            unit_measure=product.unit_measure,
            unit_price=product.unit_price,
            reorder_point=product.reorder_point,
            current_quantity=current_qty,
            total_value=current_qty * product.unit_price,
            is_low_stock=current_qty <= product.reorder_point,
        )

    async def get_all_stock(self) -> list[CurrentStockResponse]:
        """
        Obtiene el stock actual de todos los productos activos.
        Usado para el dashboard principal.

        Returns:
            Lista de CurrentStockResponse de cada producto.
        """
        stock_data = await self.movement_repo.get_all_stock()
        return [CurrentStockResponse(**item) for item in stock_data]

    async def get_low_stock(self) -> LowStockResponse:
        """
        Obtiene los productos con stock por debajo del punto de reorden.
        Usado para alertas y el dashboard.

        Returns:
            LowStockResponse con la lista y conteo de productos.
        """
        all_stock = await self.movement_repo.get_all_stock()
        low_stock_items = [
            CurrentStockResponse(**item)
            for item in all_stock
            if item["is_low_stock"]
        ]

        return LowStockResponse(
            count=len(low_stock_items),
            products=low_stock_items,
        )
