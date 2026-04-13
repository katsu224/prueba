"""
=========================================================
app/schemas/movement_type.py
Schemas Pydantic para tipos de movimiento.

Los tipos de movimiento son datos maestros que se insertan
una vez con el script SQL. No se permite crearlos desde la API.
Solo se provee un schema de respuesta para listarlos.
=========================================================
"""

from uuid import UUID

from pydantic import BaseModel


class MovementTypeResponse(BaseModel):
    """Schema de respuesta con datos del tipo de movimiento."""
    id: UUID
    name: str
    direction: str
    description: str | None = None

    class Config:
        from_attributes = True
