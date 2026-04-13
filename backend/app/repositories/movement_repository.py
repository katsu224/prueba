"""
=========================================================
app/repositories/movement_repository.py
Repositorio de acceso a datos para movimientos de inventario.

Encapsula todas las queries relacionadas con la tabla
'inventory_movements'. Este repositorio es CRÍTICO porque
contiene las queries que generan el Kardex y calculan
el stock actual.

Queries principales:
    - Crear movimiento de inventario
    - Obtener kardex (movimientos con balance acumulado)
    - Calcular stock actual de un producto
    - Detectar productos con stock bajo

Uso:
    mov_repo = MovementRepository(db_session)
    kardex = await mov_repo.get_kardex(product_id)
=========================================================
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory_movement import InventoryMovement
from app.models.movement_type import MovementType
from app.models.product import Product
from app.models.category import Category
from app.models.user import User


class MovementRepository:
    """
    Repositorio para operaciones de movimientos de inventario.

    Este repositorio contiene las queries más complejas del sistema,
    incluyendo el cálculo del Kardex con balance acumulado y
    el stock actual por producto.

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

    async def create(self, movement: InventoryMovement) -> InventoryMovement:
        """
        Registra un nuevo movimiento de inventario.

        NOTA: Los movimientos son inmutables. Una vez creados,
        no se pueden editar ni eliminar. Para correcciones,
        se debe crear un movimiento de ajuste.

        Args:
            movement: Instancia del modelo InventoryMovement.

        Returns:
            InventoryMovement creado con su ID generado.
        """
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(movement)
        return movement

    async def get_by_id(self, movement_id: UUID) -> Optional[InventoryMovement]:
        """
        Busca un movimiento por su ID con relaciones cargadas.

        Args:
            movement_id: UUID del movimiento.

        Returns:
            InventoryMovement con producto y tipo cargados, o None.
        """
        query = (
            select(InventoryMovement)
            .options(
                selectinload(InventoryMovement.product),
                selectinload(InventoryMovement.movement_type),
                selectinload(InventoryMovement.user),
            )
            .where(InventoryMovement.id == movement_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        product_id: Optional[UUID] = None,
    ) -> list[InventoryMovement]:
        """
        Obtiene movimientos con paginación y filtro por producto.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.
            product_id: Filtrar por producto (opcional).

        Returns:
            Lista de movimientos ordenados por fecha descendente.
        """
        query = (
            select(InventoryMovement)
            .options(
                selectinload(InventoryMovement.product),
                selectinload(InventoryMovement.movement_type),
                selectinload(InventoryMovement.user),
            )
        )

        if product_id:
            query = query.where(InventoryMovement.product_id == product_id)

        query = (
            query.offset(skip)
            .limit(limit)
            .order_by(InventoryMovement.movement_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_movement_types(self) -> list[MovementType]:
        """
        Obtiene todos los tipos de movimiento disponibles.

        Returns:
            Lista de todos los MovementType.
        """
        query = select(MovementType).order_by(MovementType.direction, MovementType.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_movement_type_by_id(
        self, type_id: UUID
    ) -> Optional[MovementType]:
        """
        Busca un tipo de movimiento por su ID.

        Args:
            type_id: UUID del tipo de movimiento.

        Returns:
            MovementType si existe, None si no.
        """
        query = select(MovementType).where(MovementType.id == type_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_current_stock(self, product_id: UUID) -> Decimal:
        """
        Calcula el stock actual de un producto sumando todas
        las entradas y restando todas las salidas.

        Args:
            product_id: UUID del producto.

        Returns:
            Decimal con la cantidad actual en inventario.
        """
        query = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (MovementType.direction == "IN", InventoryMovement.quantity),
                            (MovementType.direction == "OUT", -InventoryMovement.quantity),
                            else_=0,
                        )
                    ),
                    0,
                )
            )
            .select_from(InventoryMovement)
            .join(MovementType, InventoryMovement.movement_type_id == MovementType.id)
            .where(InventoryMovement.product_id == product_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_kardex(
        self,
        product_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Obtiene el Kardex completo de un producto con balance acumulado.

        Ejecuta una query con window functions para calcular el
        running balance (balance acumulado) de cada movimiento.

        Args:
            product_id: UUID del producto.
            date_from: Fecha inicial del filtro (opcional).
            date_to: Fecha final del filtro (opcional).

        Returns:
            Lista de diccionarios con los datos del kardex,
            incluyendo el balance acumulado por cada movimiento.
        """
        # Construir query base con window function para running balance
        quantity_expression = case(
            (MovementType.direction == "IN", InventoryMovement.quantity),
            (MovementType.direction == "OUT", -InventoryMovement.quantity),
            else_=0,
        )

        query = (
            select(
                InventoryMovement.id.label("movement_id"),
                InventoryMovement.movement_date,
                MovementType.name.label("movement_type"),
                MovementType.direction,
                InventoryMovement.quantity,
                InventoryMovement.unit_cost,
                (InventoryMovement.quantity * InventoryMovement.unit_cost).label("total_cost"),
                InventoryMovement.reference_number,
                InventoryMovement.notes,
                User.username.label("registered_by"),
                func.sum(quantity_expression)
                .over(
                    order_by=[
                        InventoryMovement.movement_date,
                        InventoryMovement.created_at,
                    ]
                )
                .label("running_balance"),
            )
            .select_from(InventoryMovement)
            .join(MovementType, InventoryMovement.movement_type_id == MovementType.id)
            .outerjoin(User, InventoryMovement.user_id == User.id)
            .where(InventoryMovement.product_id == product_id)
        )

        # Aplicar filtros de fecha opcionales
        if date_from:
            query = query.where(InventoryMovement.movement_date >= date_from)
        if date_to:
            query = query.where(InventoryMovement.movement_date <= date_to)

        query = query.order_by(
            InventoryMovement.movement_date,
            InventoryMovement.created_at,
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Convertir filas a diccionarios
        return [
            {
                "movement_id": row.movement_id,
                "movement_date": row.movement_date,
                "movement_type": row.movement_type,
                "direction": row.direction,
                "quantity": row.quantity,
                "unit_cost": row.unit_cost,
                "total_cost": row.total_cost,
                "reference_number": row.reference_number,
                "notes": row.notes,
                "registered_by": row.registered_by,
                "running_balance": row.running_balance,
            }
            for row in rows
        ]

    async def get_all_stock(self) -> list[dict]:
        """
        Obtiene el stock actual de TODOS los productos activos.
        Usado para el dashboard y reportes.

        Returns:
            Lista de diccionarios con el stock de cada producto.
        """
        quantity_expression = case(
            (MovementType.direction == "IN", InventoryMovement.quantity),
            (MovementType.direction == "OUT", -InventoryMovement.quantity),
            else_=0,
        )

        value_expression = case(
            (
                MovementType.direction == "IN",
                InventoryMovement.quantity * InventoryMovement.unit_cost,
            ),
            (
                MovementType.direction == "OUT",
                -(InventoryMovement.quantity * InventoryMovement.unit_cost),
            ),
            else_=0,
        )

        query = (
            select(
                Product.id.label("product_id"),
                Product.sku,
                Product.name.label("product_name"),
                Product.unit_measure,
                Product.unit_price,
                Product.reorder_point,
                Category.name.label("category_name"),
                func.coalesce(func.sum(quantity_expression), 0).label("current_quantity"),
                func.coalesce(func.sum(value_expression), 0).label("total_value"),
            )
            .select_from(Product)
            .outerjoin(Category, Product.category_id == Category.id)
            .outerjoin(InventoryMovement, Product.id == InventoryMovement.product_id)
            .outerjoin(MovementType, InventoryMovement.movement_type_id == MovementType.id)
            .where(Product.is_active == True)  # noqa: E712
            .group_by(
                Product.id,
                Product.sku,
                Product.name,
                Product.unit_measure,
                Product.unit_price,
                Product.reorder_point,
                Category.name,
            )
            .order_by(Product.name)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "product_id": row.product_id,
                "sku": row.sku,
                "product_name": row.product_name,
                "unit_measure": row.unit_measure,
                "unit_price": row.unit_price,
                "reorder_point": row.reorder_point,
                "category_name": row.category_name,
                "current_quantity": row.current_quantity,
                "total_value": row.total_value,
                "is_low_stock": row.current_quantity <= row.reorder_point,
            }
            for row in rows
        ]
