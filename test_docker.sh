#!/bin/bash
echo "🔨 Budowanie obrazu Docker..."
docker build -t ozon-pricing-api .

echo ""
echo "✅ Obraz zbudowany!"
echo ""
echo "🚀 Aby uruchomić lokalnie:"
echo "docker run -p 8000:8000 -e DATA_DIR=/app/data ozon-pricing-api"
