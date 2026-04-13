"""
=========================================================
app/models/__init__.py
Paquete de modelos ORM (SQLAlchemy).

Importa todos los modelos para que SQLAlchemy los registre
en los metadatos de la Base declarativa. Esto es necesario
para que Alembic detecte los modelos al generar migraciones.

Cada modelo representa una tabla en la base de datos.
=========================================================
"""

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.movement_type import MovementType
from app.models.inventory_movement import InventoryMovement

# Exportar todos los modelos para acceso conveniente
__all__ = [
    "User",
    "Category",
    "Product",
    "MovementType",
    "InventoryMovement",
]
