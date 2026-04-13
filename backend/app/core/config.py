"""
=========================================================
app/core/config.py
Configuración central de la aplicación.

Utiliza Pydantic Settings para cargar y validar variables
de entorno desde el archivo .env. Todas las configuraciones
de la aplicación se centralizan aquí para mantener un
único punto de verdad.

Uso:
    from app.core.config import settings
    print(settings.DATABASE_URL)
=========================================================
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.

    Atributos:
        APP_NAME: Nombre de la aplicación
        DEBUG: Modo debug activado/desactivado
        API_V1_PREFIX: Prefijo para las rutas de la API v1
        DATABASE_URL: URL de conexión a PostgreSQL (Supabase)
        SUPABASE_URL: URL del proyecto en Supabase
        SUPABASE_KEY: Clave anónima de Supabase
        SECRET_KEY: Clave secreta para firmar tokens JWT
        ALGORITHM: Algoritmo de encriptación para JWT
        ACCESS_TOKEN_EXPIRE_MINUTES: Tiempo de expiración del token
        CORS_ORIGINS: Lista de orígenes permitidos para CORS
    """

    # --- Aplicación ---
    APP_NAME: str = "Sistema de Inventario Kardex"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Base de datos ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/inventory"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # --- JWT ---
    SECRET_KEY: str = "clave-secreta-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "https://prueba-black-chi.vercel.app"]

    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración.
# Se importa en toda la app como: from app.core.config import settings
settings = Settings()
