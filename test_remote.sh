#!/bin/bash

# Ustaw URL swojego backendu Railway
API_URL="${RAILWAY_URL:-https://your-app-name.railway.app}"

echo "🧪 Testowanie zdalnego API"
echo "🌐 URL: $API_URL"
echo ""

# Sprawdź czy URL jest ustawiony
if [[ "$API_URL" == "https://your-app-name.railway.app" ]]; then
    echo "⚠️  UWAGA: Ustaw zmienną RAILWAY_URL lub edytuj skrypt!"
    echo "   Przykład: RAILWAY_URL=https://your-app.railway.app ./test_remote.sh"
    echo ""
fi

# 1. Health check
echo "1️⃣  Health Check:"
curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/health"
echo ""

# 2. Status
echo "2️⃣  Status:"
curl -s "$API_URL/api/status" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/api/status"
echo ""

# 3. Produkty (pierwsza strona)
echo "3️⃣  Produkty (5 sztuk):"
curl -s "$API_URL/api/products?page=1&page_size=5" | python3 -m json.tool 2>/dev/null | head -30 || curl -s "$API_URL/api/products?page=1&page_ ""

# 4. Top produkty
echo "4️⃣  Top 5 produktów:"
curl -s "$API_URL/api/analytics/demand/top?limit=5" | python3 -m json.tool 2>/dev/null | head -40 || curl -s "$API_URL/api/analytics/demand/top?limit=5" | head -40
echo ""

# 5. Metrykiwe
echo "5️⃣  Metryki cenowe:"
curl -s "$API_URL/api/analytics/pricing-metrics?min_days_out_of_stock=15" | python3 -m json.tool 2>/dev/null | head -20 || curl -s "$API_URL/api/analytics/pricing-metrics?min_days_out_of_stock=15" | head -20
echo ""

# 6. Statystyka cache
ec6️⃣  Statystyka cache:"
curl -s "$API_URL/api/cache/stats" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/api/cache/stats"
echo ""

echo "✅ Testowanie zakończone"
