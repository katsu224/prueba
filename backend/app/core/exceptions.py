"""
=========================================================
app/core/exceptions.py
Excepciones personalizadas del dominio de negocio.

Define excepciones específicas que se lanzan en la capa
de servicios y se traducen a respuestas HTTP apropiadas
en el handler global de excepciones (registrado en main.py).

Principio: Las capas de servicio y repositorio NO deben
importar HTTPException de FastAPI. En su lugar, lanzan
estas excepciones de dominio.

Uso:
    from app.core.exceptions import NotFoundError
    raise NotFoundError("Producto", product_id)
=========================================================
"""


class AppError(Exception):
    """
    Excepción base de la aplicación.
    Todas las excepciones de dominio heredan de esta clase.

    Atributos:
        message: Mensaje descriptivo del error.
        status_code: Código HTTP sugerido para la respuesta.
    """

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """
    Se lanza cuando un recurso no se encuentra en la base de datos.
    Código HTTP: 404
    """

    def __init__(self, entity: str, entity_id: str = ""):
        detail = f"{entity} no encontrado"
        if entity_id:
            detail = f"{entity} con ID '{entity_id}' no encontrado"
        super().__init__(message=detail, status_code=404)


class DuplicateError(AppError):
    """
    Se lanza cuando se intenta crear un recurso que ya existe.
    Ejemplo: SKU duplicado, email ya registrado.
    Código HTTP: 409
    """

    def __init__(self, entity: str, field: str, value: str):
        detail = f"{entity} con {field} '{value}' ya existe"
        super().__init__(message=detail, status_code=409)


class BusinessRuleError(AppError):
    """
    Se lanza cuando se viola una regla de negocio.
    Ejemplo: Stock insuficiente para una salida.
    Código HTTP: 422
    """

    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)


class AuthenticationError(AppError):
    """
    Se lanza cuando las credenciales son inválidas.
    Código HTTP: 401
    """

    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppError):
    """
    Se lanza cuando el usuario no tiene permisos suficientes.
    Código HTTP: 403
    """

    def __init__(self, message: str = "No tiene permisos para realizar esta acción"):
        super().__init__(message=message, status_code=403)
