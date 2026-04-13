import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # auth/login doesn't have a trailing slash in the router prefix, but router itself might.
        # Let's check auth.py
        r = await client.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "password123"})
        r.raise_for_status()
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login OK")

        r = await client.post(f"{BASE_URL}/categories/", json={"name": "Test Python Cat"}, headers=headers)
        r.raise_for_status()
        cat_id = r.json()["id"]
        print("Category OK", cat_id)

        r = await client.post(f"{BASE_URL}/products/", json={
            "sku": "SKU-999", "name": "Prod", "unit_price": 50, "category_id": cat_id
        }, headers=headers)
        r.raise_for_status()
        prod_id = r.json()["id"]
        print("Product OK", prod_id)

        r = await client.get(f"{BASE_URL}/movements/types/", headers=headers)
        r.raise_for_status()
        types = r.json()
        print("Types OK")

        if types:
            r = await client.post(f"{BASE_URL}/movements/", json={
                "product_id": prod_id, "movement_type_id": types[0]["id"], "quantity": 10
            }, headers=headers)
            r.raise_for_status()
            print("Movement OK")
        
        r = await client.delete(f"{BASE_URL}/products/{prod_id}", headers=headers)
        r.raise_for_status()
        print("Delete Product OK")

        r = await client.delete(f"{BASE_URL}/categories/{cat_id}", headers=headers)
        r.raise_for_status()
        print("Delete Category OK")

asyncio.run(main())
