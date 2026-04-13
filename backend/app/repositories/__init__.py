"""
=========================================================
app/repositories/__init__.py
Paquete de repositorios (capa de acceso a datos).

Los repositorios encapsulan TODAS las operaciones de base
de datos (queries SQL/ORM). Ninguna otra capa debe
ejecutar queries directamente.

Patrón Repository:
    - Reciben una sesión de base de datos en el constructor
    - Proveen métodos CRUD y queries específicas
    - Retornan modelos ORM o None
    - NO contienen lógica de negocio
    - NO lanzan excepciones HTTP (usan excepciones de dominio)
=========================================================
"""

from app.repositories.user_repository import UserRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.movement_repository import MovementRepository

__all__ = [
    "UserRepository",
    "CategoryRepository",
    "ProductRepository",
    "MovementRepository",
]
