import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/v1/auth/register", json={
            "email": "admin@example.com",
            "username": "admin",
            "password": "password123",
            "full_name": "Administrador"
        })
        print(response.status_code)
        print(response.json())

asyncio.run(main())
