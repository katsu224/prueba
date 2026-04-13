"""
=========================================================
app/schemas/__init__.py
Paquete de schemas Pydantic (validación de datos).

Los schemas definen la estructura de datos para:
- Request: Datos que recibe la API (creación/actualización)
- Response: Datos que retorna la API al cliente

Separar schemas de modelos ORM es una buena práctica:
- Evita exponer campos internos (hashed_password)
- Permite validaciones específicas por operación
- Desacopla la capa de presentación de la capa de datos
=========================================================
"""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.schemas.movement_type import MovementTypeResponse
from app.schemas.inventory_movement import (
    MovementCreate,
    MovementResponse,
)
from app.schemas.kardex import (
    KardexEntry,
    KardexResponse,
    CurrentStockResponse,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "MovementTypeResponse",
    "MovementCreate",
    "MovementResponse",
    "KardexEntry",
    "KardexResponse",
    "CurrentStockResponse",
]
