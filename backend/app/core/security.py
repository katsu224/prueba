"""
=========================================================
app/core/security.py
Utilidades de seguridad y autenticación JWT.

Provee funciones para:
- Hashear y verificar contraseñas con bcrypt
- Crear tokens JWT de acceso
- Verificar y decodificar tokens JWT
- Dependencia get_current_user() para proteger endpoints

Uso en rutas protegidas:
    from app.core.security import get_current_user
    
    @router.get("/protected")
    async def protected_route(
        current_user: User = Depends(get_current_user)
    ):
        return {"user": current_user.email}
=========================================================
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

# --- Configuración de hashing de contraseñas ---
# Usa bcrypt como algoritmo principal.
# deprecated="auto" permite migrar de algoritmos antiguos automáticamente.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Esquema OAuth2 para extraer el token del header Authorization ---
# tokenUrl apunta al endpoint de login que retorna el token.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


import hashlib

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando SHA-256 seguido de bcrypt.
    Esto soluciona el límite de 72 bytes de bcrypt.

    Args:
        password: Contraseña en texto plano.

    Returns:
        str: Hash bcrypt de la contraseña (después de SHA-256).
    """
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(digest)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    Aplica SHA-256 primero, como al hashear.

    Args:
        plain_password: Contraseña a verificar.
        hashed_password: Hash almacenado en la base de datos.

    Returns:
        bool: True si coinciden, False si no.
    """
    digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(digest, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT firmado con la clave secreta.

    Args:
        data: Datos a codificar en el payload del token.
              Normalmente incluye {"sub": user_id}.
        expires_delta: Tiempo de expiración personalizado.
                       Si no se especifica, usa el valor de config.

    Returns:
        str: Token JWT codificado.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.

    Args:
        token: Token JWT a decodificar.

    Returns:
        dict: Payload del token decodificado.

    Raises:
        HTTPException: Si el token es inválido o ha expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependencia de FastAPI que extrae y valida el usuario actual
    desde el token JWT en el header Authorization.

    Este es el punto central de autenticación. Se inyecta en
    cualquier endpoint que requiera un usuario autenticado.

    Args:
        token: Token JWT extraído del header Authorization.
        db: Sesión de base de datos.

    Returns:
        User: Objeto del usuario autenticado.

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    # Importación tardía para evitar dependencias circulares
    from app.repositories.user_repository import UserRepository

    payload = decode_access_token(token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: no contiene identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )

    return user
