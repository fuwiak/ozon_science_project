# Testowanie backendu po wdrożeniu na Railway

## 🚀 Szybki start

Po wdrożeniu na Railway otrzymasz URL aplikacji, np.:
```
https://your-app-name.railway.app
```

## 📋 Podstawowe testy

### 1. Health Check

Sprawdź czy aplikacja działa:

```bash
curl https://your-app-name.railway.app/health
```

**Oczekiwany wynik:**
```json
{
  "status": "healthy",
  "data_files_loaded": 34,
  "total_products": 350000,
  "cache_ready": true,
  "using_mock_data": false
}
```

### 2. Status API

Sprawdź status zaгрузки данных:

```bash
curl https://your-app-name.railway.app/api/status
```

**Oczekiwany wynik:**
```json
{
  "cache_ready": true,
  "loading": false,
  "files_loaded": 34,
  "total_products": 350000,
  "using_mock_data": false
}
```

### 3. Swagger UI

Otwórz w przeglądarce:
```
https://your-app-name.railway.app/docs
```

Możesz testować wszystkie endpointy interaktywnie!

## 🧪 Testowanie endpointów

### Produkty

#### Pobierz listę produktów
```bash
curl "https://your-app-name.railway.app/api/products?page=1&page_size=10"
```

#### Pobierz produkt po ID
```bash
curl "https://your-app-name.railway.app/api/products/PRODUCT_ID"
```

#### Filtrowanie produktów
```bash
# Po kategorii
curl "https://your-app-name.railway.app/api/products?category_level_1=Красота%20и%20здоровье&page=1&page_size=5"

# Po minimalnej liczbie ulubionych
curl "https://your-app-name.railway.app/api/products?min_favorites_count=1000&page=1&page_size=5"

# Produkty bez stanu
curl "https://your-app-name.railway.app/api/products?out_of_stock_days=15&page=1&page_size=5"
```

#### Lista kategorii
```bash
curl "https://your-app-name.railway.app/api/products/categories/list"
```

#### Lista marek
```bash
curl "https://your-app-name.railway.app/api/products/brands/list"
```

### Analityka

#### Top produkty
```bash
curl "https://your-app-name.railway.app/api/analytics/demand/top?limit=10"
```

#### Top produkty z filtrami
```bash
curl "https://your-app-name.railway.app/api/analytics/demand/top?limit=5&category=Красота%20и%20здоровье"
```

#### Trendy popytu
```bash
curl "https://your-app-name.railway.app/api/analytics/demand/trends?group_by=category"
```

#### Produkty bez stanu
```bash
curl "https://your-app-name.railway.app/api/analytics/stock/out-of-stock?min_days=15"
```

#### Metryki cenowe
```bash
curl "https://your-app-name.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15"
```

#### Szeregi czasowe
```bash
curl "https://your-app-name.railway.app/api/analytics/timeseries?period=month"
```

### Cache Administration

#### Statystyka cache
```bash
curl "https://your-app-name.railway.app/api/cache/stats"
```

#### Produkty w cache
```bash
curl "https://your-app-name.railway.app/api/cache/products?page=1&page_size=20"
```

#### Dodaj produkt
```bash
curl -X POST "https://your-app-name.railway.app/api/cache/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "brand": "Test Brand",
    "category_level_1": "Красота и здоровье",
    "favorites_count": 1000,
    "days_out_of_stock": 10
  }'
```

#### Usuń produkt
```bash
curl -X DELETE "https://your-app-name.railway.app/api/cache/products/PRODUCT_ID"
```

#### Wyczyść cache
```bash
curl -X POST "https://your-app-name.railway.app/api/cache/clear"
```

#### Przeładuj cache
```bash
curl -X POST "https://your-app-name.railway.app/api/cache/reload"
```

## 🔧 Skrypty do testowania

### Bash Script

Utwórz plik `test_remote.sh`:

```bash
#!/bin/bash

# Ustaw URL swojego backendu
API_URL="https://your-app-name.railway.app"

echo "🧪 Testowanie zdalnego API: $API_URL"
echo ""

# 1. Health check
echo "1. Health Check:"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# 2. Status
echo "2. Status:"
curl -s "$API_URL/api/status" | python3 -m json.tool
echo ""

# 3. Produkty (pierwsza strona)
echo "3. Produkty (5 sztuk):"
curl -s "$API_URL/api/products?page=1&page_size=5" | python3 -m json.tool | head -30
echo ""

# 4. Top produkty
echo "4. Top 5 produktów:"
curl -s "$API_URL/api/analytics/demand/top?limit=5" | python3 -m json.tool | head -40
echo ""

# 5. Metryki cenowe
echo "5. Metryki cenowe:"
curl -s "$API_URL/api/analytics/pricing-metrics?min_days_out_of_stock=15" | python3 -m json.tool | head -20
echo ""

# 6. Statystyka cache
echo "6. Statystyka cache:"
curl -s "$API_URL/api/cache/stats" | python3 -m json.tool
echo ""

echo "✅ Testowanie zakończone"
```

Uruchomienie:
```bash
chmod +x test_remote.sh
./test_remote.sh
```

### Python Script

Utwórz plik `test_remote.py`:

```python
import requests
import json
from typing import Dict, Any

API_URL = "https://your-app-name.railway.app"

def test_endpoint(name: str, url: str, method: str = "GET", data: Dict = None):
    """Testuje endpoint i wyświetla wynik"""
    print(f"\n{'='*50}")
    print(f"🧪 {name}")
    print(f"📍 {method} {url}")
    print(f"{'='*50}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        response.raise_for_status()
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"✅ Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return False

def main():
    print("🚀 Testowanie zdalnego API")
    print(f"🌐 URL: {API_URL}\n")
    
    # Podstawowe testy
    test_endpoint("Health Check", f"{API_URL}/health")
    test_endpoint("Status", f"{API_URL}/api/status")
    
    # Produkty
    test_endpoint("Lista produktów", f"{API_URL}/api/products?page=1&page_size=5")
    test_endpoint("Kategorie", f"{API_URL}/api/products/categories/list")
    test_endpoint("Marki", f"{API_URL}/api/products/brands/list")
    
    # Analityka
    test_endpoint("Top produkty", f"{API_URL}/api/analytics/demand/top?limit=5")
    test_endpoint("Metryki cenowe", f"{API_URL}/api/analytics/pricing-metrics?min_days_out_of_stock=15")
    test_endpoint("Produkty bez stanu", f"{API_URL}/api/analytics/stock/out-of-stock?min_days=15")
    
    # Cache
    test_endpoint("Statystyka cache", f"{API_URL}/api/cache/stats")
    
    print("\n" + "="*50)
    print("✅ Testowanie zakończone")
    print("="*50)

if __name__ == "__main__":
    main()
```

Uruchomienie:
```bash
python test_remote.py
```

### Postman Collection

Możesz zaimportować OpenAPI schema do Postman:

1. Pobierz schema:
```bash
curl https://your-app-name.railway.app/openapi.json > openapi.json
```

2. W Postman:
   - Import → File → wybierz `openapi.json`
   - Wszystkie endpointy będą dostępne

## 🌐 Testowanie w przeglądarce

### Swagger UI
```
https://your-app-name.railway.app/docs
```

### ReDoc
```
https://your-app-name.railway.app/redoc
```

## 🔍 Sprawdzanie błędów

### Sprawdź logi w Railway

1. Otwórz Railway Dashboard
2. Wybierz swój projekt
3. Kliknij "View Logs"
4. Sprawdź błędy podczas startu

### Testowanie z verbose output

```bash
curl -v https://your-app-name.railway.app/health
```

Flaga `-v` pokazuje:
- Headers request/response
- Status codes
- Czas odpowiedzi

### Sprawdzenie timeout

```bash
# Z timeout 30 sekund
curl --max-time 30 https://your-app-name.railway.app/api/products
```

## 📊 Monitoring

### Railway Metrics

W Railway Dashboard możesz zobaczyć:
- CPU usage
- Memory usage
- Network traffic
- Request count

### Health Check Endpoint

Możesz skonfigurować monitoring, który sprawdza `/health` co X minut.

## 🔐 Testowanie z autentykacją

Jeśli dodasz autentykację w przyszłości:

```bash
# Z tokenem
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app-name.railway.app/api/products
```

## 🐛 Debugging

### Sprawdź czy aplikacja działa

```bash
# Podstawowy test
curl -I https://your-app-name.railway.app/health

# Powinien zwrócić: HTTP/2 200
```

### Sprawdź CORS

Jeśli frontend nie może połączyć się z backendem:

```bash
curl -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS \
  https://your-app-name.railway.app/api/products
```

### Sprawdź czas odpowiedzi

```bash
time curl https://your-app-name.railway.app/api/products
```

## 📝 Przykładowe scenariusze testowe

### Scenariusz 1: Podstawowy flow

```bash
# 1. Sprawdź health
curl https://your-app.railway.app/health

# 2. Pobierz produkty
curl "https://your-app.railway.app/api/products?page=1&page_size=10"

# 3. Pobierz top produkty
curl "https://your-app.railway.app/api/analytics/demand/top?limit=5"

# 4. Sprawdź metryki
curl "https://your-app.railway.app/api/analytics/pricing-metrics"
```

### Scenariusz 2: Filtrowanie

```bash
# 1. Produkty w kategorii
curl "https://your-app.railway.app/api/products?category_level_1=Красота%20и%20здоровье"

# 2. Produkty z wysokim popytem
curl "https://your-app.railway.app/api/products?min_favorites_count=5000"

# 3. Produkty bez stanu
curl "https://your-app.railway.app/api/products?out_of_stock_days=30"
```

### Scenariusz 3: Cache management

```bash
# 1. Sprawdź statystyki
curl https://your-app.railway.app/api/cache/stats

# 2. Pobierz produkty z cache
curl "https://your-app.railway.app/api/cache/products?page=1&page_size=20"

# 3. Przeładuj cache
curl -X POST https://your-app.railway.app/api/cache/reload
```

## ✅ Checklist testowania

- [ ] Health check zwraca 200
- [ ] Status endpoint działa
- [ ] Swagger UI dostępny
- [ ] Produkty można pobrać
- [ ] Filtrowanie działa
- [ ] Analityka zwraca dane
- [ ] Cache endpoints działają
- [ ] CORS skonfigurowany (jeśli frontend)
- [ ] Czas odpowiedzi < 2s
- [ ] Logi w Railway bez błędów

## 🚨 Typowe problemy

### Problem: 502 Bad Gateway

**Rozwiązanie:**
- Sprawdź logi w Railway
- Upewnij się, że aplikacja nasłuchuje na `0.0.0.0`
- Sprawdź czy PORT jest ustawiony

### Problem: Timeout

**Rozwiązanie:**
- Sprawdź czy dane są załadowane
- Zwiększ timeout w Railway settings
- Sprawdź rozmiar danych

### Problem: CORS errors

**Rozwiązanie:**
- Ustaw `CORS_ORIGINS` w Railway variables
- Sprawdź konfigurację w `app/main.py`

## 📚 Dodatkowe zasoby

- Railway Logs: Dashboard → Deployments → View Logs
- Railway Metrics: Dashboard → Metrics
- API Docs: `https://your-app.railway.app/docs`

