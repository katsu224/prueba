import asyncio
from app.core.database import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

async def run_test():
    async with AsyncSessionLocal() as db:
        service = AuthService(db)
        user_data = UserCreate(
            email="admin2@example.com",
            username="admin2",
            password="password123",
            full_name="Admin"
        )
        try:
            user = await service.register(user_data)
            print("Usuario creado:", user)
        except Exception as e:
            print("Error capturado:", e.__class__.__name__, str(e))

asyncio.run(run_test())
