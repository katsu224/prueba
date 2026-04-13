"""
=========================================================
app/services/auth_service.py
Servicio de autenticación y gestión de usuarios.

Contiene la lógica de negocio para:
- Registrar nuevos usuarios
- Autenticar usuarios (login)
- Generar tokens JWT

Reglas de negocio:
- El email y username deben ser únicos
- La contraseña se hashea con bcrypt antes de almacenar
- El token JWT incluye el user_id en el campo "sub"

Uso:
    auth_service = AuthService(db_session)
    token = await auth_service.login("admin", "password123")
=========================================================
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, DuplicateError
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    hash_password, 
    verify_password,
    verify_refresh_token
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, TokenResponse, UserResponse


class AuthService:
    """
    Servicio de autenticación.

    Orquesta la lógica de registro y login de usuarios,
    delegando el acceso a datos al UserRepository.

    Atributos:
        user_repo: Repositorio de usuarios.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> UserResponse:
        """
        Registra un nuevo usuario en el sistema.

        Valida que el email y username no estén en uso,
        hashea la contraseña y crea el usuario.

        Args:
            user_data: Datos del nuevo usuario validados por Pydantic.

        Returns:
            UserResponse con los datos del usuario creado.

        Raises:
            DuplicateError: Si el email o username ya existen.
        """
        # Verificar que el email no esté en uso
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise DuplicateError("Usuario", "email", user_data.email)

        # Verificar que el username no esté en uso
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise DuplicateError("Usuario", "username", user_data.username)

        # Crear el usuario con la contraseña hasheada
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )

        created_user = await self.user_repo.create(user)
        return UserResponse.model_validate(created_user)

    async def login(self, username: str, password: str) -> TokenResponse:
        """
        Autentica un usuario y genera un token JWT.

        Busca al usuario por username, verifica la contraseña
        y genera un token de acceso.

        Args:
            username: Nombre de usuario.
            password: Contraseña en texto plano.

        Returns:
            TokenResponse con el token JWT y datos del usuario.

        Raises:
            AuthenticationError: Si las credenciales son inválidas.
        """
        # Buscar usuario por username
        user = await self.user_repo.get_by_username(username)

        # Si no existe, intentar buscar por email
        if not user:
            user = await self.user_repo.get_by_email(username)

        # Validar que el usuario existe y la contraseña es correcta
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Usuario o contraseña incorrectos")

        # Validar que el usuario está activo
        if not user.is_active:
            raise AuthenticationError("Usuario desactivado")

        # Generar tokens JWT con el user_id en el campo "sub"
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Renueva el access token usando un refresh token válido.
        """
        from uuid import UUID
        user_id = verify_refresh_token(refresh_token)
        
        if not user_id:
            raise AuthenticationError("Refresh token inválido")
            
        user = await self.user_repo.get_by_id(UUID(user_id))
        
        if not user or not user.is_active:
            raise AuthenticationError("Usuario no encontrado o inactivo")
            
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
