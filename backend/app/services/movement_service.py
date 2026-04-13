"""
=========================================================
app/services/movement_service.py
Servicio de gestión de movimientos de inventario.

Contiene la lógica de negocio para:
- Registrar movimientos de inventario (entradas/salidas)
- Validar stock suficiente para salidas
- Listar movimientos con filtros
- Listar tipos de movimiento

Reglas de negocio:
- La cantidad debe ser positiva (la dirección la define el tipo)
- Para movimientos de salida, el stock actual debe ser >= cantidad
- Los movimientos son inmutables (nunca se editan ni eliminan)
- Cada movimiento se asocia al usuario que lo registra

Uso:
    mov_service = MovementService(db_session)
    movement = await mov_service.create(MovementCreate(...), user_id)
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.inventory_movement import InventoryMovement
from app.repositories.movement_repository import MovementRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory_movement import MovementCreate, MovementResponse
from app.schemas.movement_type import MovementTypeResponse


class MovementService:
    """
    Servicio de lógica de negocio para movimientos de inventario.

    Atributos:
        movement_repo: Repositorio de movimientos.
        product_repo: Repositorio de productos (para validaciones).
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.movement_repo = MovementRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_movement_types(self) -> list[MovementTypeResponse]:
        """
        Obtiene todos los tipos de movimiento disponibles.

        Returns:
            Lista de MovementTypeResponse.
        """
        types = await self.movement_repo.get_movement_types()
        return [MovementTypeResponse.model_validate(t) for t in types]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        product_id: Optional[UUID] = None,
    ) -> list[MovementResponse]:
        """
        Obtiene movimientos con paginación y filtro por producto.

        Args:
            skip: Registros a saltar.
            limit: Máximo de registros.
            product_id: Filtrar por producto.

        Returns:
            Lista de MovementResponse.
        """
        movements = await self.movement_repo.get_all(
            skip=skip, limit=limit, product_id=product_id
        )
        return [MovementResponse.model_validate(m) for m in movements]

    async def get_by_id(self, movement_id: UUID) -> MovementResponse:
        """
        Obtiene un movimiento por su ID.

        Args:
            movement_id: UUID del movimiento.

        Returns:
            MovementResponse con los datos completos.

        Raises:
            NotFoundError: Si el movimiento no existe.
        """
        movement = await self.movement_repo.get_by_id(movement_id)
        if not movement:
            raise NotFoundError("Movimiento", str(movement_id))
        return MovementResponse.model_validate(movement)

    async def create(
        self,
        data: MovementCreate,
        user_id: Optional[UUID] = None,
    ) -> MovementResponse:
        """
        Registra un nuevo movimiento de inventario.

        Valida que:
        1. El producto existe y está activo
        2. El tipo de movimiento existe
        3. Si es salida, hay stock suficiente

        Args:
            data: Datos del movimiento validados por Pydantic.
            user_id: UUID del usuario que registra el movimiento.

        Returns:
            MovementResponse del movimiento creado.

        Raises:
            NotFoundError: Si el producto o tipo de movimiento no existe.
            BusinessRuleError: Si no hay stock suficiente para una salida.
        """
        # 1. Verificar que el producto existe y está activo
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundError("Producto", str(data.product_id))
        if not product.is_active:
            raise BusinessRuleError(
                f"El producto '{product.name}' está desactivado. "
                "No se pueden registrar movimientos."
            )

        # 2. Verificar que el tipo de movimiento existe
        movement_type = await self.movement_repo.get_movement_type_by_id(
            data.movement_type_id
        )
        if not movement_type:
            raise NotFoundError("Tipo de movimiento", str(data.movement_type_id))

        # 3. Si es salida (OUT), verificar stock suficiente
        if movement_type.direction == "OUT":
            current_stock = await self.movement_repo.get_current_stock(
                data.product_id
            )
            if current_stock < data.quantity:
                raise BusinessRuleError(
                    f"Stock insuficiente para '{product.name}'. "
                    f"Stock actual: {current_stock}, "
                    f"cantidad solicitada: {data.quantity}"
                )

        # 4. Crear el movimiento
        movement = InventoryMovement(
            product_id=data.product_id,
            movement_type_id=data.movement_type_id,
            user_id=user_id,
            quantity=data.quantity,
            unit_cost=data.unit_cost,
            reference_number=data.reference_number,
            notes=data.notes,
            movement_date=data.movement_date,
        )

        created = await self.movement_repo.create(movement)

        # Recargar con relaciones
        full_movement = await self.movement_repo.get_by_id(created.id)
        return MovementResponse.model_validate(full_movement)
