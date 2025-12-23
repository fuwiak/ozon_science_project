# 🚀 Szybki przegląd endpointów dla n8n

**Base URL:** `https://ozonscienceproject-production.up.railway.app`

## 📋 Wszystkie dostępne endpointy

### 🔹 Bazowe
- `GET /` - Informacja o API
- `GET /health` - Health check
- `GET /api/status` - Status danych
- `GET /docs` - Swagger UI (interaktywna dokumentacja)

### 📦 Produkty (`/api/products`)
- `GET /api/products` - Wyszukiwanie z filtrami
- `GET /api/products/{id}` - Szczegóły produktu
- `GET /api/products/categories/list` - Lista kategorii
- `GET /api/products/brands/list` - Lista marek

### 📈 Analityka (`/api/analytics`)
- `GET /api/analytics/demand/top` - Top produkty
- `GET /api/analytics/demand/trends` - Trendy popytu
- `GET /api/analytics/stock/out-of-stock` - Produkty bez stanu
- `GET /api/analytics/timeseries` - Szeregi czasowe
- `GET /api/analytics/pricing-metrics` - Metryki cenowe

### 🗄️ Cache (`/api/cache`)
- `GET /api/cache/stats` - Statystyki
- `GET /api/cache/products` - Lista produktów
- `GET /api/cache/products/{id}` - Pobierz produkt
- `POST /api/cache/products` - Dodaj produkt
- `PUT /api/cache/products/{id}` - Aktualizuj produkt
- `DELETE /api/cache/products/{id}` - Usuń produkt
- `DELETE /api/cache/products` - Masowe usuwanie
- `POST /api/cache/clear` - Wyczyść cache
- `POST /api/cache/reload` - Przeładuj cache

### 🔌 n8n (`/api/n8n`)
- `GET /api/n8n/workflows` - Lista workflows
- `POST /api/n8n/workflows/{id}/toggle` - Przełącz workflow
- `POST /api/n8n/workflows/{id}/execute` - Uruchom workflow
- `GET /api/n8n/workflows/{id}` - Informacje o workflow
- `POST /api/n8n/test-connection` - Test połączenia

### 🤖 Telegram (`/api/telegram`)
- `POST /api/telegram/command` - Obsługa komend
- `POST /api/telegram/webhook` - Webhook
- `POST /api/telegram/bot/settings` - Ustawienia bota
- `GET /api/telegram/bot/status` - Status bota
- `POST /api/telegram/bot/send-message` - Wyślij wiadomość
- `POST /api/telegram/bot/set-menu` - Ustaw menu

## 🎯 Najpopularniejsze endpointy dla n8n

1. **Top produkty:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=10
   ```

2. **Produkty bez stanu:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=30
   ```

3. **Metryki cenowe:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15
   ```

4. **Wyszukiwanie produktów:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products?category_level_1=Красота%20и%20здоровье&page=1&page_size=20
   ```

5. **Status:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/status
   ```

## 📖 Pełna dokumentacja

Zobacz `N8N_ENDPOINTS.md` dla szczegółowych przykładów i parametrów.

## 🔗 Swagger UI

Interaktywna dokumentacja: https://ozonscienceproject-production.up.railway.app/docs
