"""
=========================================================
app/main.py
Punto de entrada principal de la aplicación FastAPI.

Configura:
- La instancia de FastAPI con metadatos
- Middleware CORS para permitir peticiones del frontend
- Handler global de excepciones de dominio
- Registro del router principal de la API v1
- Evento de startup para verificar la conexión a BD

Para ejecutar:
    uvicorn app.main:app --reload --port 8000

Documentación automática disponible en:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc:      http://localhost:8000/redoc
=========================================================
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError


# --- Evento de ciclo de vida ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al apagar el servidor.
    """
    # Startup
    print(f"🚀 Iniciando {settings.APP_NAME}...")
    print(f"📄 Documentación: http://localhost:8000/docs")
    print(f"🔗 API v1: http://localhost:8000{settings.API_V1_PREFIX}")
    yield
    # Shutdown
    print(f"🛑 Apagando {settings.APP_NAME}...")


# --- Crear instancia de FastAPI ---
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST para gestión de inventario con Kardex. "
        "Permite registrar productos, movimientos de entrada/salida, "
        "y consultar el Kardex completo con balance acumulado."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- Middleware CORS ---
# Permite que el frontend de React se comunique con este backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Handler global de excepciones de dominio ---
# Convierte las excepciones de dominio (NotFoundError, DuplicateError, etc.)
# en respuestas HTTP con el código y mensaje apropiado.
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """
    Handler global para excepciones de dominio.

    Intercepta cualquier excepción que herede de AppError
    y la convierte en una respuesta JSON con el código HTTP
    y mensaje correspondiente.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": type(exc).__name__,
        },
    )


# --- Registrar routers ---
# Incluir el router principal de la API v1 con el prefijo configurado.
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# --- Endpoint raíz ---
@app.get(
    "/",
    tags=["Sistema"],
    summary="Estado del sistema",
    description="Verifica que la API está funcionando correctamente.",
)
async def root():
    """
    Endpoint raíz que retorna el estado del sistema.
    Útil para health checks.
    """
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Health check",
    description="Verifica la salud del sistema.",
)
async def health_check():
    """
    Health check básico del sistema.
    Retorna OK si el servidor está respondiendo.
    """
    return {"status": "healthy"}
