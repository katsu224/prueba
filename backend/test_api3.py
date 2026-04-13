import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def test_endpoint(client, method, url, **kwargs):
    print(f"Testing {method} {url}...")
    try:
        response = await client.request(method, f"{BASE_URL}{url}", follow_redirects=True, **kwargs)
        if response.status_code >= 400:
            print(f"❌ Error {response.status_code}")
            print(response.text)
            return None
        print(f"✅ Success {response.status_code}")
        return response.json() if response.content else None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        response = await test_endpoint(client, "POST", "/auth/login", data={"username": "admin", "password": "password123"})
        if not response: return
        token = response.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Categories
        cat = await test_endpoint(client, "POST", "/categories/", json={"name": "Test Cat Python"}, headers=headers)
        if not cat: return
        cat_id = cat["id"]

        # Products
        prod = await test_endpoint(client, "POST", "/products/", json={
            "sku": "TEST-004", "name": "Python Prod", "unit_price": 5.0, "category_id": cat_id
        }, headers=headers)
        if not prod: return
        prod_id = prod["id"]

        # Movement types
        types = await test_endpoint(client, "GET", "/movements/types", headers=headers)
        
        if types:
            # Create Movement
            await test_endpoint(client, "POST", "/movements/", json={
                "product_id": prod_id, "movement_type_id": types[0]["id"], "quantity": 10
            }, headers=headers)

        # Delete product
        await test_endpoint(client, "DELETE", f"/products/{prod_id}", headers=headers)
        # Delete category
        await test_endpoint(client, "DELETE", f"/categories/{cat_id}", headers=headers)

asyncio.run(main())
