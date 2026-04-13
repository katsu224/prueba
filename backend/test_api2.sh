#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

echo "--- LOGIN ---"
TOKEN=$(curl -sX POST $BASE_URL/auth/login -d "username=admin&password=password123" | jq -r .access_token)
echo "Token: $TOKEN"

echo "--- GET CATEGORIES ---"
curl -s -X GET $BASE_URL/categories -H "Authorization: Bearer $TOKEN"

echo " "
echo "--- CREATE CATEGORY ---"
curl -s -X POST $BASE_URL/categories -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name": "Test Cat 3"}'

