# Wszystkie dostępne endpointy API dla n8n

**Base URL:** `https://ozonscienceproject-production.up.railway.app`

## 📋 Spis treści

1. [Bazowe endpointy](#bazowe-endpointy)
2. [Produkty](#produkty)
3. [Analityka](#analityka)
4. [Cache Administration](#cache-administration)
5. [n8n Integration](#n8n-integration)
6. [Telegram Integration](#telegram-integration)

---

## 🔹 Bazowe endpointy

### `GET /`
Informacja o API

**URL:** `https://ozonscienceproject-production.up.railway.app/`

**Response:**
```json
{
  "message": "OZON Dynamic Pricing API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "products": "/api/products",
    "analytics": "/api/analytics",
    "n8n": "/api/n8n"
  }
}
```

### `GET /health`
Health check - sprawdza czy API działa

**URL:** `https://ozonscienceproject-production.up.railway.app/health`

**Response:**
```json
{
  "status": "healthy",
  "data_files_loaded": 34,
  "total_products": 350000,
  "cache_ready": true,
  "using_mock_data": false
}
```

### `GET /api/status`
Status zaгрузки данных

**URL:** `https://ozonscienceproject-production.up.railway.app/api/status`

**Response:**
```json
{
  "cache_ready": true,
  "loading": false,
  "files_loaded": 34,
  "total_products": 350000,
  "using_mock_data": false,
  "message": "✅ Используются реальные данные"
}
```

### `GET /docs`
Swagger UI - interaktywna dokumentacja

**URL:** `https://ozonscienceproject-production.up.railway.app/docs`

---

## 📦 Produkty

### `GET /api/products`
Wyszukiwanie produktów z filtrami i paginacją

**URL:** `https://ozonscienceproject-production.up.railway.app/api/products`

**Query Parameters:**
- `category_level_1` (optional) - Kategoria 1 poziomu
- `category_level_2` (optional) - Kategoria 2 poziomu
- `category_level_3` (optional) - Kategoria 3 poziomu
- `category_level_4` (optional) - Kategoria 4 poziomu
- `brand` (optional) - Marka
- `min_favorites_count` (optional) - Minimalna liczba ulubionych
- `period_start` (optional) - Data rozpoczęcia (YYYY-MM-DD)
- `period_end` (optional) - Data zakończenia (YYYY-MM-DD)
- `out_of_stock_days` (optional) - Minimalna liczba dni bez stanu
- `page` (default: 1) - Numer strony
- `page_size` (default: 50) - Rozmiar strony

**Przykłady:**

1. **Wszystkie produkty (pierwsza strona):**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products?page=1&page_size=10
   ```

2. **Produkty w kategorii:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products?category_level_1=Красота%20и%20здоровье&page=1&page_size=20
   ```

3. **Produkty z wysokim popytem:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products?min_favorites_count=5000&page=1&page_size=10
   ```

4. **Produkty bez stanu:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products?out_of_stock_days=15&page=1&page_size=10
   ```

**Response:**
```json
{
  "products": [...],
  "total": 1000,
  "page": 1,
  "page_size": 10,
  "total_pages": 100
}
```

### `GET /api/products/{product_id}`
Pobierz szczegóły produktu po ID

**URL:** `https://ozonscienceproject-production.up.railway.app/api/products/{product_id}`

**Przykład:**
```
GET https://ozonscienceproject-production.up.railway.app/api/products/abc123def456
```

### `GET /api/products/categories/list`
Lista wszystkich kategorii poziomu 1

**URL:** `https://ozonscienceproject-production.up.railway.app/api/products/categories/list`

**Response:**
```json
["Красота и здоровье", "Электроника", "Одежда и обувь", ...]
```

### `GET /api/products/brands/list`
Lista wszystkich marek

**URL:** `https://ozonscienceproject-production.up.railway.app/api/products/brands/list`

**Query Parameters:**
- `category` (optional) - Filtruj po kategorii

**Przykłady:**

1. **Wszystkie marki:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products/brands/list
   ```

2. **Marki w kategorii:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/products/brands/list?category=Красота%20и%20здоровье
   ```

**Response:**
```json
["Brand 1", "Brand 2", "Brand 3", ...]
```

---

## 📈 Analityka

### `GET /api/analytics/demand/top`
Top N produktów według popytu (liczba ulubionych)

**URL:** `https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top`

**Query Parameters:**
- `limit` (default: 10) - Liczba produktów (1-1000)
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce
- `period_start` (optional) - Data rozpoczęcia (YYYY-MM-DD)
- `period_end` (optional) - Data zakończenia (YYYY-MM-DD)

**Przykłady:**

1. **Top 10 produktów:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=10
   ```

2. **Top 20 produktów w kategorii:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=20&category=Красота%20и%20здоровье
   ```

**Response:**
```json
[
  {
    "product_id": "abc123",
    "product_name": "Product Name",
    "brand": "Brand",
    "category_level_1": "Category",
    "favorites_count": 25000,
    "period_start": "2024-01-01",
    "period_end": "2024-01-31",
    "rank": 1
  },
  ...
]
```

### `GET /api/analytics/demand/trends`
Trendy popytu

**URL:** `https://ozonscienceproject-production.up.railway.app/api/analytics/demand/trends`

**Query Parameters:**
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce
- `group_by` (default: "category") - Grupowanie: `category`, `brand`, `period`

**Przykłady:**

1. **Trendy po kategoriach:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/trends?group_by=category
   ```

2. **Trendy po markach:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/trends?group_by=brand
   ```

**Response:**
```json
[
  {
    "period": "2024-01",
    "total_favorites": 1000000,
    "unique_products": 5000,
    "avg_favorites_per_product": 200,
    "category": "Красота и здоровье"
  },
  ...
]
```

### `GET /api/analytics/stock/out-of-stock`
Produkty bez stanu

**URL:** `https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock`

**Query Parameters:**
- `min_days` (default: 15) - Minimalna liczba dni bez stanu
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce
- `period_start` (optional) - Data rozpoczęcia (YYYY-MM-DD)
- `period_end` (optional) - Data zakończenia (YYYY-MM-DD)

**Przykłady:**

1. **Produkty bez stanu 15+ dni:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=15
   ```

2. **Krytyczne produkty (30+ dni):**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=30
   ```

**Response:**
```json
[
  {
    "product_id": "abc123",
    "product_name": "Product Name",
    "brand": "Brand",
    "category_level_1": "Category",
    "last_in_stock": "2024-01-15",
    "days_out_of_stock": 45,
    "favorites_count": 25000,
    "priority_score": 92
  },
  ...
]
```

### `GET /api/analytics/timeseries`
Szeregi czasowe dodania do ulubionych

**URL:** `https://ozonscienceproject-production.up.railway.app/api/analytics/timeseries`

**Query Parameters:**
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce
- `group_by` (optional) - Grupowanie: `category`, `brand`
- `period` (default: "month") - Okres: `day`, `week`, `month`

**Przykłady:**

1. **Szeregi czasowe po miesiącach:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/timeseries?period=month
   ```

2. **Po tygodniach, pogrupowane po kategoriach:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/timeseries?period=week&group_by=category
   ```

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "value": 1000,
      "category": "Красота и здоровье"
    },
    ...
  ],
  "group_by": "category"
}
```

### `GET /api/analytics/pricing-metrics`
Metryki dla dynamicznego cenowania

**URL:** `https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics`

**Query Parameters:**
- `min_days_out_of_stock` (default: 15) - Minimalna liczba dni bez stanu
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce

**Przykłady:**

1. **Wszystkie metryki:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15
   ```

2. **Metryki dla kategorii:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?category=Красота%20и%20здоровье&min_days_out_of_stock=20
   ```

**Response:**
```json
{
  "metrics": [
    {
      "product_id": "abc123",
      "product_name": "Product Name",
      "brand": "Brand",
      "category_level_1": "Category",
      "demand_level": "high",
      "favorites_count": 25000,
      "days_out_of_stock": 45,
      "priority_score": 92,
      "recommendation": "Высокий приоритет: высокий спрос, рекомендуется пополнить в ближайшее время."
    },
    ...
  ],
  "total": 100
}
```

---

## 🗄️ Cache Administration

### `GET /api/cache/stats`
Statystyki cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/stats`

**Response:**
```json
{
  "total_products": 350000,
  "files_loaded": 34,
  "using_mock_data": false,
  "cache_size_mb": 125.5,
  "file_metadata": {...}
}
```

### `GET /api/cache/products`
Lista produktów w cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products`

**Query Parameters:**
- `page` (default: 1) - Numer strony
- `page_size` (default: 20) - Rozmiar strony
- `search` (optional) - Wyszukiwanie po nazwie
- `category` (optional) - Filtruj po kategorii
- `brand` (optional) - Filtruj po marce

**Przykłady:**

1. **Pierwsza strona (20 produktów):**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/cache/products?page=1&page_size=20
   ```

2. **Wyszukiwanie:**
   ```
   GET https://ozonscienceproject-production.up.railway.app/api/cache/products?search=крем&page=1&page_size=5
   ```

### `GET /api/cache/products/{product_id}`
Pobierz produkt z cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products/{product_id}`

### `POST /api/cache/products`
Dodaj produkt do cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products`

**Method:** `POST`

**Body (JSON):**
```json
{
  "name": "Test Product",
  "brand": "Test Brand",
  "category_level_1": "Красота и здоровье",
  "favorites_count": 1000,
  "days_out_of_stock": 10
}
```

### `PUT /api/cache/products/{product_id}`
Aktualizuj produkt w cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products/{product_id}`

**Method:** `PUT`

**Body (JSON):**
```json
{
  "name": "Updated Product Name",
  "favorites_count": 2000
}
```

### `DELETE /api/cache/products/{product_id}`
Usuń produkt z cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products/{product_id}`

**Method:** `DELETE`

### `DELETE /api/cache/products`
Masowe usuwanie produktów

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/products`

**Method:** `DELETE`

**Body (JSON):**
```json
{
  "product_ids": ["id1", "id2", "id3"]
}
```

### `POST /api/cache/clear`
Wyczyść cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/clear`

**Method:** `POST`

### `POST /api/cache/reload`
Przeładuj cache

**URL:** `https://ozonscienceproject-production.up.railway.app/api/cache/reload`

**Method:** `POST`

---

## 🔌 n8n Integration

### `GET /api/n8n/workflows`
Lista workflows z n8n

**URL:** `https://ozonscienceproject-production.up.railway.app/api/n8n/workflows`

**Query Parameters:**
- `url` (optional) - URL instancji n8n
- `api_key` (optional) - API key n8n

**Przykład:**
```
GET https://ozonscienceproject-production.up.railway.app/api/n8n/workflows?url=https://n8n.example.com&api_key=your_key
```

### `POST /api/n8n/workflows/{workflow_id}/toggle`
Przełącz workflow (aktywny/nieaktywny)

**URL:** `https://ozonscienceproject-production.up.railway.app/api/n8n/workflows/{workflow_id}/toggle`

**Method:** `POST`

**Query Parameters:**
- `url` (optional) - URL instancji n8n
- `api_key` (optional) - API key n8n

**Body (JSON):**
```json
{
  "active": true
}
```

### `POST /api/n8n/workflows/{workflow_id}/execute`
Uruchom workflow

**URL:** `https://ozonscienceproject-production.up.railway.app/api/n8n/workflows/{workflow_id}/execute`

**Method:** `POST`

**Query Parameters:**
- `url` (optional) - URL instancji n8n
- `api_key` (optional) - API key n8n

**Body (JSON):**
```json
{
  "data": {}
}
```

### `GET /api/n8n/workflows/{workflow_id}`
Pobierz informacje o workflow

**URL:** `https://ozonscienceproject-production.up.railway.app/api/n8n/workflows/{workflow_id}`

**Query Parameters:**
- `url` (optional) - URL instancji n8n
- `api_key` (optional) - API key n8n

### `POST /api/n8n/test-connection`
Test połączenia z n8n

**URL:** `https://ozonscienceproject-production.up.railway.app/api/n8n/test-connection`

**Method:** `POST`

**Body (JSON):**
```json
{
  "url": "https://n8n.example.com",
  "api_key": "your_api_key"
}
```

---

## 🤖 Telegram Integration

### `POST /api/telegram/command`
Obsługa komend z Telegram

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/command`

**Method:** `POST`

**Body (JSON):**
```json
{
  "command": "/stats",
  "chat_id": "123456",
  "user_id": "789012",
  "message": "/stats"
}
```

**Dostępne komendy:**
- `/stats` - Statystyka cache
- `/dashboard` - Dashboard
- `/products` - Informacja o produktach
- `/analytics` - Analityka
- `/pricing` - Cenowanie
- `/cache` - Zarządzanie cache
- `/cache_clear` - Wyczyść cache
- `/cache_reload` - Przeładuj cache
- `/products_count` - Liczba produktów
- `/help` - Lista komend

### `POST /api/telegram/webhook`
Webhook dla Telegram

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/webhook`

**Method:** `POST`

**Body (JSON):**
```json
{
  "message": {
    "text": "/stats",
    "chat": {"id": 123456},
    "from": {"id": 789012}
  }
}
```

### `POST /api/telegram/bot/settings`
Zapisz ustawienia Telegram bota

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/bot/settings`

**Method:** `POST`

**Body (JSON):**
```json
{
  "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "webhook_url": "https://your-domain.com/api/telegram/webhook"
}
```

### `GET /api/telegram/bot/status`
Status Telegram bota

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/bot/status`

### `POST /api/telegram/bot/send-message`
Wyślij wiadomość przez bota

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/bot/send-message`

**Method:** `POST`

**Body (JSON):**
```json
{
  "chat_id": "123456",
  "message": "Test message"
}
```

### `POST /api/telegram/bot/set-menu`
Ustaw menu komend w bocie

**URL:** `https://ozonscienceproject-production.up.railway.app/api/telegram/bot/set-menu`

**Method:** `POST`

---

## 🧪 Przykłady użycia w n8n

### Przykład 1: Pobierz top produkty

**Node:** HTTP Request

**Method:** GET

**URL:** 
```
https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=10
```

**Response:**
```json
[
  {
    "product_id": "...",
    "product_name": "...",
    "favorites_count": 25000,
    ...
  }
]
```

### Przykład 2: Sprawdź produkty bez stanu

**Node:** HTTP Request

**Method:** GET

**URL:**
```
https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=30
```

### Przykład 3: Pobierz metryki cenowe

**Node:** HTTP Request

**Method:** GET

**URL:**
```
https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15
```

### Przykład 4: Wyszukaj produkty

**Node:** HTTP Request

**Method:** GET

**URL:**
```
https://ozonscienceproject-production.up.railway.app/api/products?category_level_1=Красота%20и%20здоровье&min_favorites_count=1000&page=1&page_size=20
```

### Przykład 5: Wyślij komendę Telegram

**Node:** HTTP Request

**Method:** POST

**URL:**
```
https://ozonscienceproject-production.up.railway.app/api/telegram/command
```

**Body (JSON):**
```json
{
  "command": "/stats",
  "chat_id": "{{$json.chat_id}}",
  "user_id": "{{$json.user_id}}"
}
```

---

## 📝 Notatki dla n8n

1. **Encoding:** Używaj URL encoding dla parametrów (np. `%20` dla spacji)
2. **Headers:** Dla POST/PUT/DELETE ustaw `Content-Type: application/json`
3. **Paginacja:** Używaj `page` i `page_size` dla dużych zbiorów danych
4. **Filtry:** Możesz łączyć wiele filtrów w jednym zapytaniu
5. **Error handling:** Sprawdź status code w odpowiedzi

---

## 🔗 Przydatne linki

- **Swagger UI:** https://ozonscienceproject-production.up.railway.app/docs
- **ReDoc:** https://ozonscienceproject-production.up.railway.app/redoc
- **OpenAPI Schema:** https://ozonscienceproject-production.up.railway.app/openapi.json

