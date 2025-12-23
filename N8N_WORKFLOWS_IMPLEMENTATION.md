# Implementacja workflows n8n z dostępnymi endpointami

**Base URL:** `https://ozonscienceproject-production.up.railway.app`

## 📊 Analiza workflows

### ✅ 1. Обновление цен на основе спроса (Aktualizacja cen na podstawie popytu)

**Status:** ✅ **MOŻLIWE DO ZREALIZOWANIA**

**Używane endpointy:**
- `GET /api/analytics/pricing-metrics` - Metryki cenowe z poziomem popytu
- `GET /api/analytics/demand/top` - Top produkty według popytu
- `GET /api/products` - Szczegóły produktów do aktualizacji cen

**Workflow w n8n:**
```
1. HTTP Request → GET /api/analytics/pricing-metrics?min_days_out_of_stock=15
   └─> Pobierz produkty z wysokim popytem i priorytetem

2. Filter → Filtruj produkty z demand_level="high" i priority_score >= 70

3. HTTP Request → GET /api/products/{product_id}
   └─> Pobierz szczegóły każdego produktu

4. Function/Code → Oblicz nową cenę na podstawie:
   - favorites_count (popyt)
   - days_out_of_stock
   - priority_score

5. Webhook/API → Wyślij zaktualizowane ceny do systemu cenowego
```

**Endpointy:**
```bash
# Pobierz metryki cenowe
GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15

# Pobierz top produkty
GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=50
```

---

### ✅ 2. Мониторинг остатков на складе (Monitorowanie stanów magazynowych)

**Status:** ✅ **MOŻLIWE DO ZREALIZOWANIA**

**Używane endpointy:**
- `GET /api/analytics/stock/out-of-stock` - Produkty bez stanu
- `GET /api/products?out_of_stock_days=X` - Filtrowanie produktów bez stanu
- `GET /api/cache/stats` - Statystyki cache

**Workflow w n8n:**
```
1. HTTP Request → GET /api/analytics/stock/out-of-stock?min_days=15
   └─> Pobierz produkty bez stanu

2. Filter → Filtruj produkty z days_out_of_stock > 30 (krytyczne)

3. HTTP Request → GET /api/products/{product_id}
   └─> Pobierz szczegóły każdego produktu

4. Condition → Sprawdź czy days_out_of_stock > 30

5. Email/Slack/Telegram → Wyślij alert o niskich stanach
```

**Endpointy:**
```bash
# Produkty bez stanu
GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=15

# Krytyczne produkty (30+ dni)
GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=30

# Filtrowanie przez produkty
GET https://ozonscienceproject-production.up.railway.app/api/products?out_of_stock_days=30
```

---

### ⚠️ 3. Анализ цен конкурентов (Analiza cen konkurentów)

**Status:** ⚠️ **CZĘŚCIOWO MOŻLIWE** (brak danych o cenach konkurentów w API)

**Używane endpointy:**
- `GET /api/analytics/demand/top` - Top produkty (można porównać popyt)
- `GET /api/products` - Szczegóły produktów
- `GET /api/analytics/demand/trends` - Trendy popytu

**Ograniczenia:**
- API nie zawiera danych o cenach konkurentów
- Można analizować popyt i trendy, ale nie ceny

**Workflow w n8n (częściowy):**
```
1. HTTP Request → GET /api/analytics/demand/top?limit=100
   └─> Pobierz top produkty

2. HTTP Request → GET /api/analytics/demand/trends?group_by=category
   └─> Pobierz trendy popytu

3. Function/Code → Analizuj trendy i popyt
   └─> (Brak danych o cenach konkurentów - wymaga zewnętrznego źródła)

4. External API → Pobierz ceny konkurentów z zewnętrznego źródła
   └─> (np. scraping, API konkurentów)

5. Function/Code → Porównaj ceny i wygeneruj rekomendacje
```

**Endpointy:**
```bash
# Top produkty do analizy
GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=100

# Trendy popytu
GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/trends?group_by=category
```

**Uwaga:** Wymaga integracji z zewnętrznym źródłem danych o cenach konkurentów.

---

### ✅ 4. Автоматическое пополнение товаров (Automatyczne uzupełnianie towarów)

**Status:** ✅ **MOŻLIWE DO ZREALIZOWANIA**

**Używane endpointy:**
- `GET /api/analytics/pricing-metrics` - Metryki z priorytetem
- `GET /api/analytics/stock/out-of-stock` - Produkty bez stanu
- `GET /api/products` - Szczegóły produktów

**Workflow w n8n:**
```
1. HTTP Request → GET /api/analytics/pricing-metrics?min_days_out_of_stock=15
   └─> Pobierz produkty wymagające uzupełnienia

2. Filter → Filtruj produkty z:
   - priority_score >= 70
   - days_out_of_stock > 15
   - demand_level = "high"

3. HTTP Request → GET /api/products/{product_id}
   └─> Pobierz szczegóły każdego produktu

4. Function/Code → Oblicz ilość do zamówienia na podstawie:
   - favorites_count (popyt)
   - days_out_of_stock
   - priority_score

5. Webhook/API → Wyślij zamówienie do systemu magazynowego
```

**Endpointy:**
```bash
# Metryki z priorytetem
GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15

# Produkty bez stanu
GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=15
```

---

### ✅ 5. Уведомления о критичных остатках (Powiadomienia o krytycznych stanach)

**Status:** ✅ **MOŻLIWE DO ZREALIZOWANIA**

**Używane endpointy:**
- `GET /api/analytics/stock/out-of-stock?min_days=30` - Krytyczne produkty
- `GET /api/analytics/pricing-metrics` - Produkty z wysokim priorytetem
- `POST /api/telegram/bot/send-message` - Wyślij powiadomienie przez Telegram

**Workflow w n8n:**
```
1. Schedule Trigger → Uruchamiaj co godzinę/dzień

2. HTTP Request → GET /api/analytics/stock/out-of-stock?min_days=30
   └─> Pobierz krytyczne produkty

3. Filter → Filtruj produkty z:
   - days_out_of_stock > 30
   - priority_score >= 80

4. HTTP Request → GET /api/analytics/pricing-metrics?min_days_out_of_stock=30
   └─> Pobierz metryki dla kontekstu

5. Function/Code → Formatuj wiadomość z listą produktów

6. HTTP Request → POST /api/telegram/bot/send-message
   └─> Wyślij powiadomienie przez Telegram

7. (Opcjonalnie) Email/Slack → Wyślij również przez email/Slack
```

**Endpointy:**
```bash
# Krytyczne produkty
GET https://ozonscienceproject-production.up.railway.app/api/analytics/stock/out-of-stock?min_days=30

# Metryki dla kontekstu
GET https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=30

# Wyślij powiadomienie
POST https://ozonscienceproject-production.up.railway.app/api/telegram/bot/send-message
Body: {
  "chat_id": "YOUR_CHAT_ID",
  "message": "Krytyczne produkty: ..."
}
```

---

### ✅ 6. Экспорт данных для аналитики (Eksport danych do analityki)

**Status:** ✅ **MOŻLIWE DO ZREALIZOWANIA**

**Używane endpointy:**
- `GET /api/products` - Wszystkie produkty (z paginacją)
- `GET /api/analytics/demand/top` - Top produkty
- `GET /api/analytics/demand/trends` - Trendy
- `GET /api/analytics/timeseries` - Szeregi czasowe
- `GET /api/cache/stats` - Statystyki

**Workflow w n8n:**
```
1. Schedule Trigger → Uruchamiaj codziennie/tygodniowo

2. HTTP Request → GET /api/analytics/demand/top?limit=1000
   └─> Pobierz top produkty

3. HTTP Request → GET /api/analytics/demand/trends?group_by=category
   └─> Pobierz trendy

4. HTTP Request → GET /api/analytics/timeseries?period=month
   └─> Pobierz szeregi czasowe

5. Function/Code → Połącz i sformatuj dane

6. Google Sheets/CSV/Excel → Eksportuj dane
   └─> Zapisz do Google Sheets, CSV lub Excel

7. (Opcjonalnie) Email → Wyślij raport emailem
```

**Endpointy:**
```bash
# Top produkty
GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/top?limit=1000

# Trendy
GET https://ozonscienceproject-production.up.railway.app/api/analytics/demand/trends?group_by=category

# Szeregi czasowe
GET https://ozonscienceproject-production.up.railway.app/api/analytics/timeseries?period=month

# Wszystkie produkty (z paginacją)
GET https://ozonscienceproject-production.up.railway.app/api/products?page=1&page_size=1000
```

---

## 📊 Podsumowanie

| Workflow | Status | Dostępne endpointy | Wymagane dodatkowe źródła |
|----------|--------|-------------------|---------------------------|
| 1. Обновление цен на основе спроса | ✅ Pełne | pricing-metrics, demand/top, products | System cenowy (opcjonalnie) |
| 2. Мониторинг остатков на складе | ✅ Pełne | stock/out-of-stock, products | Email/Slack/Telegram |
| 3. Анализ цен конкурентов | ⚠️ Częściowe | demand/top, demand/trends | **Dane o cenach konkurentów** |
| 4. Автоматическое пополнение товаров | ✅ Pełne | pricing-metrics, stock/out-of-stock | System magazynowy |
| 5. Уведомления о критичных остатках | ✅ Pełne | stock/out-of-stock, telegram/bot/send-message | Telegram bot token |
| 6. Экспорт данных для аналитики | ✅ Pełne | products, demand/top, trends, timeseries | Google Sheets/CSV/Excel |

## 🎯 Rekomendacje

### ✅ Gotowe do implementacji (5/6):
1. **Обновление цен на основе спроса** - Wymaga tylko integracji z systemem cenowym
2. **Мониторинг остатков на складе** - Gotowe, wymaga tylko kanału powiadomień
3. **Автоматическое пополнение товаров** - Wymaga integracji z systemem magazynowym
4. **Уведомления о критичных остатках** - Gotowe, wymaga konfiguracji Telegram bota
5. **Экспорт данных для аналитики** - Gotowe, wymaga tylko wyboru formatu eksportu

### ⚠️ Wymaga dodatkowych danych (1/6):
3. **Анализ цен конкурентов** - Wymaga zewnętrznego źródła danych o cenach konkurentów (scraping, API, etc.)

## 🔧 Przykładowe konfiguracje n8n

Szczegółowe przykłady workflows znajdują się w: `n8n_workflow_examples.json`

