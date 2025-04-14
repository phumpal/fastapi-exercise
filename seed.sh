#!/bin/bash

API_URL="${API_URL:-http://localhost}"
MAX_RETRIES=5
RETRY_INTERVAL=3
ITEMS=("Arroz" "Birria" "Chorizo")

echo "Waiting for FastAPI to be available..."

count=0
while [ $count -lt $MAX_RETRIES ]; do
  health_status=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health")

  if [ "$health_status" == "200" ]; then
    echo "API is available!"
    break
  else
    echo "API not ready yet (status $health_status). Retrying in ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
    count=$((count+1))
  fi
done

if [ $count -eq $MAX_RETRIES ]; then
  echo "Failed to connect to API after $MAX_RETRIES attempts."
  exit 1
fi

echo "Fetching current items from API..."
existing_items=$(curl -s "${API_URL}/items/" | jq -r '.[].content')

for item in "${ITEMS[@]}"; do
  if echo "$existing_items" | grep -qx "$item"; then
    echo "Item \"$item\" already exists. Skipping."
  else
    echo "Item \"$item\" not found. Adding..."
    add_response=$(curl -s -w "%{http_code}" -o /tmp/add_response.json -X POST "${API_URL}/items/" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"${item}\"}")

    if [ "$add_response" == "200" ] || [ "$add_response" == "201" ]; then
      echo "Successfully added \"$item\"."
    else
      echo "Failed to add \"$item\". Response:"
      cat /tmp/add_response.json
    fi
  fi
done

echo "Final items in the database:"
curl -s "${API_URL}/items/" | jq .

echo "Database seeding completed!"
