#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

echo "--- LOGIN ---"
TOKEN=$(curl -s -X POST $BASE_URL/auth/login -d "username=admin&password=password123" | jq -r .access_token)
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Login failed"
    exit 1
fi
echo "Token: $TOKEN"

echo "--- GET MOVEMENT TYPES ---"
curl -s -X GET $BASE_URL/movements/types -H "Authorization: Bearer $TOKEN" > mov_types.json

echo "--- CREATE CATEGORY ---"
CAT_RES=$(curl -s -X POST $BASE_URL/categories -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name": "Test Cat"}')
echo $CAT_RES
CAT_ID=$(echo $CAT_RES | jq -r .id)

echo "--- CREATE PRODUCT ---"
PROD_RES=$(curl -s -X POST $BASE_URL/products -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"sku\": \"TEST-002\", \"name\": \"Test Product 2\", \"unit_price\": 10.5, \"category_id\": \"$CAT_ID\"}")
echo $PROD_RES
PROD_ID=$(echo $PROD_RES | jq -r .id)

echo "--- DELETE PRODUCT ---"
curl -s -X DELETE $BASE_URL/products/$PROD_ID -H "Authorization: Bearer $TOKEN"

echo "--- LIST PRODUCTS ---"
curl -s -X GET $BASE_URL/products -H "Authorization: Bearer $TOKEN"

echo "--- DELETE CATEGORY ---"
curl -s -X DELETE $BASE_URL/categories/$CAT_ID -H "Authorization: Bearer $TOKEN"

