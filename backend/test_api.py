import asyncio
import httpx
from httpx import Response

BASE_URL = "http://localhost:8000/api/v1"

async def test_endpoint(client, method, url, **kwargs):
    print(f"Testing {method} {url}...")
    try:
        if method == "POST":
            response = await client.post(f"{BASE_URL}{url}", **kwargs)
        elif method == "GET":
            response = await client.get(f"{BASE_URL}{url}", **kwargs)
        elif method == "DELETE":
            response = await client.delete(f"{BASE_URL}{url}", **kwargs)
        
        if response.status_code >= 400:
            print(f"❌ Error {response.status_code}")
            print(response.json())
            return None
        print(f"✅ Success {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("\n--- LOGIN ---")
        response = await test_endpoint(client, "POST", "/auth/login", data={"username": "admin", "password": "password123"})
        if not response:
            return
        
        token = response.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get movement types to use one
        print("\n--- GET MOVEMENT TYPES ---")
        types = await test_endpoint(client, "GET", "/movements/types", headers=headers)
        movement_type_id = types[0]["id"] if types else None

        # 3. Create Category
        print("\n--- CREATE CATEGORY ---")
        cat = await test_endpoint(client, "POST", "/categories", json={"name": "Test Cat"}, headers=headers)
        if not cat: return
        cat_id = cat["id"]

        # 4. Create Product
        print("\n--- CREATE PRODUCT ---")
        prod = await test_endpoint(client, "POST", "/products", json={
            "sku": "TEST-001",
            "name": "Test Product",
            "unit_price": 10.5,
            "category_id": cat_id
        }, headers=headers)
        if not prod: return
        prod_id = prod["id"]

        # 5. Create Movement
        print("\n--- CREATE MOVEMENT ---")
        if movement_type_id:
            mov = await test_endpoint(client, "POST", "/movements", json={
                "product_id": prod_id,
                "movement_type_id": movement_type_id,
                "quantity": 50,
                "unit_cost": 10.5
            }, headers=headers)

        # 6. Delete Product
        print("\n--- DELETE PRODUCT ---")
        await test_endpoint(client, "DELETE", f"/products/{prod_id}", headers=headers)

        # 7. Delete Category
        print("\n--- DELETE CATEGORY ---")
        await test_endpoint(client, "DELETE", f"/categories/{cat_id}", headers=headers)

asyncio.run(main())
