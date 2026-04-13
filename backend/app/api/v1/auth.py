"""
=========================================================
app/api/v1/auth.py
Endpoints de autenticación.

Endpoints:
    POST /register → Registrar nuevo usuario
    POST /login    → Iniciar sesión y obtener token JWT
    GET  /me       → Obtener datos del usuario autenticado

Las rutas son "delgadas": solo parsean la entrada,
llaman al servicio y retornan la respuesta.
=========================================================
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario en el sistema.",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Registra un nuevo usuario.

    - **email**: Correo electrónico único
    - **username**: Nombre de usuario único
    - **password**: Contraseña (mínimo 6 caracteres)
    - **full_name**: Nombre completo (opcional)
    """
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT.",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Inicia sesión con username/email y contraseña.

    Retorna un token JWT que debe incluirse en el header
    Authorization de las siguientes peticiones:
    `Authorization: Bearer <token>`
    """
    auth_service = AuthService(db)
    return await auth_service.login(form_data.username, form_data.password)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Retorna los datos del usuario autenticado.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Retorna los datos del usuario autenticado.
    Requiere token JWT válido.
    """
    return UserResponse.model_validate(current_user)


from app.schemas.user import RefreshTokenRequest

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acceso",
    description="Genera un nuevo par de tokens usando un refresh token válido.",
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Renueva la sesión devolviendo un nuevo access token y refresh token.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_token(data.refresh_token)
