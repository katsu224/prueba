import asyncio
from app.core.database import engine, Base
from app.models import *

async def init_models():
    async with engine.begin() as conn:
        print("Borrando tablas viejas si existen...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creando tablas...")
        await conn.run_sync(Base.metadata.create_all)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    asyncio.run(init_models())
