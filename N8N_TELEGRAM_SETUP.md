# Konfiguracja workflows n8n dla Telegram z API

**Base URL API:** `https://ozonscienceproject-production.up.railway.app`

## 📋 Dostępne workflows

### 1. Telegram API Commands - Direct
**Plik:** `n8n_telegram_integration_workflows.json`

Bezpośrednia obsługa komend Telegram z wywołaniami API.

**Funkcje:**
- Rozpoznawanie komend (`/stats`, `/dashboard`, `/products`, etc.)
- Wywoływanie odpowiednich endpointów API
- Formatowanie odpowiedzi
- Wysyłanie wyników do Telegram

**Komendy:**
- `/stats` - Statystyka cache
- `/dashboard` - Dashboard z metrykami
- `/products` - Lista produktów
- `/top` - Top produkty
- `/outofstock` - Produkty bez stanu
- `/metrics` - Metryki cenowe
- `/cache` - Statystyka cache
- `/cache_clear` - Wyczyść cache
- `/cache_reload` - Przeładuj cache
- `/help` - Lista komend

---

### 2. Telegram AI Agent with API Tools
**Plik:** `n8n_telegram_ai_workflow.json`

AI Agent który może wywoływać endpointy API jako tools.

**Funkcje:**
- Natural language processing
- Automatyczne rozpoznawanie intencji
- Wywoływanie API przez tools
- Konwersacyjny interfejs

**Tools dostępne dla AI:**
- `get_cache_stats` - Statystyka cache
- `get_dashboard_metrics` - Metryki dashboard
- `get_top_products` - Top produkty
- `get_out_of_stock` - Produkty bez stanu
- `search_products` - Wyszukiwanie produktów

**Przykłady pytań:**
- "Покажи статистику кэша"
- "Какие товары без остатка?"
- "Топ 10 товаров"
- "Метрики ценообразования"

---

### 3. Telegram Scheduled Notifications
**Plik:** `n8n_telegram_scheduled_notifications.json`

Automatyczne powiadomienia o krytycznych stanach.

**Funkcje:**
- Uruchamia się co godzinę
- Sprawdza produkty bez stanu 30+ dni
- Wysyła powiadomienia do Telegram
- Formatuje wiadomości z HTML

---

## 🚀 Instalacja w n8n

### Workflow 1: Direct Commands

1. **Import workflow:**
   - W n8n: Workflows → Import from File
   - Wybierz: `n8n_telegram_integration_workflows.json`

2. **Konfiguracja:**
   - Ustaw credentials dla Telegram Trigger
   - Sprawdź czy URL API jest poprawny: `https://ozonscienceproject-production.up.railway.app`

3. **Aktywuj workflow**

### Workflow 2: AI Agent

1. **Import workflow:**
   - Wybierz: `n8n_telegram_ai_workflow.json`

2. **Konfiguracja:**
   - Ustaw credentials dla:
     - Telegram Trigger
     - OpenRouter Chat Model
   - Sprawdź URL API

3. **Aktywuj workflow**

### Workflow 3: Scheduled Notifications

1. **Import workflow:**
   - Wybierz: `n8n_telegram_scheduled_notifications.json`

2. **Konfiguracja:**
   - Ustaw `TELEGRAM_CHAT_ID` w zmiennych środowiskowych n8n
   - Dostosuj interwał (domyślnie co godzinę)
   - Ustaw credentials dla Telegram

3. **Aktywuj workflow**

---

## 🔧 Konfiguracja

### Zmienne środowiskowe w n8n

Dodaj w Settings → Environment Variables:

```
TELEGRAM_CHAT_ID=your_chat_id
API_BASE_URL=https://ozonscienceproject-production.up.railway.app
```

### Credentials

**Telegram:**
- Bot Token (od @BotFather)

**OpenRouter (dla AI Agent):**
- API Key z OpenRouter

---

## 📝 Przykłady użycia

### Direct Commands Workflow

Użytkownik w Telegram:
```
/stats
```

Workflow:
1. Rozpoznaje komendę `/stats`
2. Wywołuje `GET /api/cache/stats`
3. Formatuje odpowiedź
4. Wysyła do Telegram

**Odpowiedź:**
```
📊 Статистика кэша

Товаров: 350,000
Файлов: 34
Размер: 125.5 МБ
Режим: Реальные данные
```

### AI Agent Workflow

Użytkownik w Telegram:
```
Покажи топ 5 товаров
```

AI Agent:
1. Rozpoznaje intencję
2. Wywołuje tool `get_top_products` z limit=5
3. Formatuje odpowiedź naturalnym językiem
4. Wysyła do Telegram

**Odpowiedź:**
```
🏆 Топ 5 товаров:

1. Название товара
   ❤️ Избранное: 25,000
   🏅 Ранг: 1
...
```

### Scheduled Notifications

Workflow uruchamia się automatycznie i wysyła:
```
⚠️ КРИТИЧЕСКИЕ ТОВАРЫ БЕЗ ОСТАТКА

Найдено: 15 товаров

1. Товар 1
   📦 Дней нет: 45
   ⭐ Приоритет: 92
   ❤️ Избранное: 25,000
...
```

---

## 🔄 Integracja z istniejącym workflow

Jeśli masz już workflow z AI Agent, możesz:

1. **Dodać tools do istniejącego AI Agent:**
   - Skopiuj nodes "Tool: *" z `n8n_telegram_ai_workflow.json`
   - Dodaj je do swojego workflow
   - Połącz z AI Agent jako `ai_tool`

2. **Użyć Direct Commands jako fallback:**
   - Jeśli AI nie rozpozna intencji, przekieruj do Direct Commands

3. **Kombinować oba podejścia:**
   - AI Agent dla naturalnych pytań
   - Direct Commands dla konkretnych komend

---

## 🛠️ Dostosowanie

### Zmiana URL API

We wszystkich workflows znajdź:
```
https://ozonscienceproject-production.up.railway.app
```

I zamień na swój URL.

### Dodanie nowych komend

W workflow "Direct Commands" w node "Parse Command" dodaj do `commandMap`:

```javascript
'/nowa_komenda': {
  method: 'GET',
  url: '/api/endpoint',
  command: 'nowa_komenda'
}
```

### Dodanie nowych tools dla AI

W workflow "AI Agent" dodaj nowy tool node i połącz z AI Agent.

---

## 📊 Struktura workflows

### Direct Commands Flow:
```
Telegram Trigger → Parse Command → Is Command? → Is Help?
  ├─> Help → Send Help
  └─> API Command → Call API → Format Response → Send Telegram
```

### AI Agent Flow:
```
Telegram Trigger → AI Agent → Send Telegram Reply
  └─> Tools (Cache Stats, Dashboard, Top Products, etc.)
```

### Scheduled Notifications Flow:
```
Schedule Trigger → Get Critical Products → Has Critical?
  └─> Format Message → Send Notification
```

---

## ✅ Testowanie

1. **Test Direct Commands:**
   - Wyślij `/help` do bota
   - Sprawdź czy otrzymujesz listę komend

2. **Test AI Agent:**
   - Zapytaj naturalnym językiem: "Какая статистика кэша?"
   - Sprawdź czy AI wywołuje odpowiedni tool

3. **Test Scheduled:**
   - Zmień interwał na 1 minutę dla testów
   - Sprawdź czy powiadomienia przychodzą

---

## 🐛 Troubleshooting

### Problem: Komendy nie działają

- Sprawdź czy workflow jest aktywny
- Sprawdź credentials Telegram
- Sprawdź logi w n8n

### Problem: AI nie wywołuje tools

- Sprawdź czy tools są poprawnie połączone z AI Agent
- Sprawdź czy URL API jest dostępny
- Sprawdź logi AI Agent

### Problem: Powiadomienia nie przychodzą

- Sprawdź `TELEGRAM_CHAT_ID`
- Sprawdź czy są krytyczne produkty
- Sprawdź logi workflow

---

## 📚 Dokumentacja

- **Endpointy:** `N8N_ENDPOINTS.md`
- **Workflows:** `N8N_WORKFLOWS_IMPLEMENTATION.md`
- **API Base:** `https://ozonscienceproject-production.up.railway.app/docs`

