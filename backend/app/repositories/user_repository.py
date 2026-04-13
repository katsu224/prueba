"""
=========================================================
app/repositories/user_repository.py
Repositorio de acceso a datos para usuarios.

Encapsula todas las operaciones de base de datos
relacionadas con la tabla 'users'. Provee métodos
para buscar, crear y actualizar usuarios.

Uso:
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_email("admin@test.com")
=========================================================
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """
    Repositorio para operaciones CRUD de usuarios.

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

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Busca un usuario por su ID.

        Args:
            user_id: UUID del usuario.

        Returns:
            User si existe, None si no.
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su correo electrónico.

        Args:
            email: Correo electrónico del usuario.

        Returns:
            User si existe, None si no.
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por su nombre de usuario.

        Args:
            username: Nombre de usuario.

        Returns:
            User si existe, None si no.
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            user: Instancia del modelo User a persistir.

        Returns:
            User creado con su ID generado.
        """
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Obtiene una lista paginada de usuarios.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros a retornar.

        Returns:
            Lista de usuarios.
        """
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
