"""
=========================================================
app/services/__init__.py
Paquete de servicios (capa de lógica de negocio).

Los servicios contienen TODA la lógica de negocio de la
aplicación. Son el puente entre las rutas (API) y los
repositorios (datos).

Reglas de los servicios:
    - NO importan FastAPI (HTTPException, Request, etc.)
    - Lanzan excepciones de dominio (NotFoundError, etc.)
    - Reciben datos ya validados por Pydantic
    - Orquestan llamadas a uno o más repositorios
    - Aplican reglas de negocio (validaciones, cálculos)
=========================================================
"""

from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.services.movement_service import MovementService
from app.services.kardex_service import KardexService

__all__ = [
    "AuthService",
    "CategoryService",
    "ProductService",
    "MovementService",
    "KardexService",
]
