"""
=========================================================
app/core/database.py
Configuración de la conexión a la base de datos.

Establece la conexión asíncrona a PostgreSQL (Supabase)
usando SQLAlchemy con el driver asyncpg. Provee:
- Engine asíncrono para conexiones
- SessionLocal factory para crear sesiones
- Base declarativa para los modelos ORM
- Dependencia get_db() para inyección en FastAPI

Uso en rutas:
    from app.core.database import get_db
    
    @router.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        ...
=========================================================
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Motor asíncrono de SQLAlchemy.
# echo=True imprime las queries SQL en consola (solo en debug).
# pool_pre_ping verifica que la conexión está activa antes de usarla.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Factory para crear sesiones de base de datos.
# expire_on_commit=False permite acceder a atributos después del commit.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Clase base declarativa para todos los modelos ORM.
    Todos los modelos deben heredar de esta clase.
    """
    pass


async def get_db():
    """
    Dependencia de FastAPI que provee una sesión de base de datos.

    Crea una sesión asíncrona, la entrega al endpoint que la solicita,
    y la cierra automáticamente al terminar (incluso si hay errores).

    Yields:
        AsyncSession: Sesión de base de datos activa.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
