"""
=========================================================
app/api/v1/router.py
Router principal de la API v1.

Agrupa todos los sub-routers de la versión 1 de la API.
Se incluye en main.py con el prefijo /api/v1.

Endpoints disponibles:
    /api/v1/auth/...       → Autenticación
    /api/v1/categories/... → Categorías
    /api/v1/products/...   → Productos
    /api/v1/movements/...  → Movimientos de inventario
    /api/v1/kardex/...     → Kardex y stock
=========================================================
"""

from fastapi import APIRouter

from app.api.v1 import auth, categories, products, movements, kardex

# Router principal v1 que agrupa todos los sub-routers
api_router = APIRouter()

# Registrar cada módulo de rutas con su prefijo y tag
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticación"],
)
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categorías"],
)
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Productos"],
)
api_router.include_router(
    movements.router,
    prefix="/movements",
    tags=["Movimientos"],
)
api_router.include_router(
    kardex.router,
    prefix="/kardex",
    tags=["Kardex"],
)
