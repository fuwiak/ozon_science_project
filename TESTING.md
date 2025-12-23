# Тестирование API - Endpoints и примеры

## Способы тестирования

### 1. Swagger UI (Рекомендуется)
Откройте в браузере: **http://localhost:8000/docs**

- Интерактивный интерфейс
- Автоматическая документация
- Можно тестировать прямо в браузере
- Примеры запросов и ответов

### 2. Автоматические тесты (pytest)
```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск конкретного файла
pytest tests/test_products.py -v

# Запуск с подробным выводом
pytest tests/ -v --tb=short
```

### 3. curl / HTTP клиенты
Примеры ниже для каждого эндпоинта

### 4. Postman / Insomnia
Импортируйте OpenAPI схему из: http://localhost:8000/openapi.json

---

## 📋 Полный список эндпоинтов

### 🔹 Базовые эндпоинты

#### `GET /`
Информация об API
```bash
curl http://localhost:8000/
```

#### `GET /health`
Проверка здоровья API
```bash
curl http://localhost:8000/health
```

#### `GET /api/status`
Статус загрузки данных
```bash
curl http://localhost:8000/api/status
```

---

### 🔹 Товары (Products)

#### `GET /api/products`
Поиск товаров с фильтрацией и пагинацией

**Параметры:**
- `category_level_1` - Категория 1 уровня
- `category_level_2` - Категория 2 уровня
- `brand` - Бренд
- `min_favorites_count` - Минимальное количество избранного
- `out_of_stock_days` - Минимальное количество дней отсутствия
- `page` - Номер страницы (default: 1)
- `page_size` - Размер страницы (default: 50)

**Примеры:**
```bash
# Все товары
curl "http://localhost:8000/api/products"

# С фильтрами
curl "http://localhost:8000/api/products?category_level_1=Красота%20и%20здоровье&min_favorites_count=1000&page=1&page_size=20"

# Товары без остатка более 15 дней
curl "http://localhost:8000/api/products?out_of_stock_days=15"
```

#### `GET /api/products/{product_id}`
Получение товара по ID
```bash
curl "http://localhost:8000/api/products/abc123"
```

#### `GET /api/products/categories/list`
Список всех категорий
```bash
curl "http://localhost:8000/api/products/categories/list"
```

#### `GET /api/products/brands/list`
Список всех брендов
```bash
# Все бренды
curl "http://localhost:8000/api/products/brands/list"

# Бренды в категории
curl "http://localhost:8000/api/products/brands/list?category=Красота%20и%20здоровье"
```

---

### 🔹 Аналитика (Analytics)

#### `GET /api/analytics/demand/top`
Топ товаров по спросу

**Параметры:**
- `limit` - Количество товаров (default: 10)
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду

**Примеры:**
```bash
# Топ 10 товаров
curl "http://localhost:8000/api/analytics/demand/top?limit=10"

# Топ 20 товаров в категории
curl "http://localhost:8000/api/analytics/demand/top?limit=20&category=Красота%20и%20здоровье"
```

#### `GET /api/analytics/demand/trends`
Тренды спроса

**Параметры:**
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду
- `group_by` - Группировка: `category`, `brand`, `period` (default: `category`)

**Примеры:**
```bash
# Тренды по категориям
curl "http://localhost:8000/api/analytics/demand/trends?group_by=category"

# Тренды по брендам
curl "http://localhost:8000/api/analytics/demand/trends?group_by=brand"
```

#### `GET /api/analytics/stock/out-of-stock`
Товары без остатка

**Параметры:**
- `min_days` - Минимальное количество дней отсутствия (default: 15)
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду

**Примеры:**
```bash
# Товары без остатка более 15 дней
curl "http://localhost:8000/api/analytics/stock/out-of-stock?min_days=15"

# Критичные остатки (30+ дней)
curl "http://localhost:8000/api/analytics/stock/out-of-stock?min_days=30"
```

#### `GET /api/analytics/timeseries`
Временной ряд добавлений в избранное

**Параметры:**
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду
- `group_by` - Группировка: `category`, `brand`
- `period` - Период: `day`, `week`, `month` (default: `month`)

**Примеры:**
```bash
# Временной ряд по месяцам
curl "http://localhost:8000/api/analytics/timeseries?period=month"

# По неделям, сгруппировано по категориям
curl "http://localhost:8000/api/analytics/timeseries?period=week&group_by=category"
```

#### `GET /api/analytics/pricing-metrics`
Метрики для динамического ценообразования

**Параметры:**
- `min_days_out_of_stock` - Минимальное количество дней отсутствия (default: 15)
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду

**Примеры:**
```bash
# Все метрики
curl "http://localhost:8000/api/analytics/pricing-metrics?min_days_out_of_stock=15"

# Метрики для категории
curl "http://localhost:8000/api/analytics/pricing-metrics?category=Красота%20и%20здоровье&min_days_out_of_stock=20"
```

---

### 🔹 Кэш (Cache Administration)

#### `GET /api/cache/stats`
Статистика кэша
```bash
curl "http://localhost:8000/api/cache/stats"
```

#### `GET /api/cache/products`
Список товаров в кэше

**Параметры:**
- `page` - Номер страницы (default: 1)
- `page_size` - Размер страницы (default: 20)
- `search` - Поиск по названию
- `category` - Фильтр по категории
- `brand` - Фильтр по бренду

**Примеры:**
```bash
# Первая страница (20 товаров)
curl "http://localhost:8000/api/cache/products?page=1&page_size=20"

# Поиск
curl "http://localhost:8000/api/cache/products?search=крем&page=1&page_size=5"
```

#### `GET /api/cache/products/{product_id}`
Получение товара из кэша
```bash
curl "http://localhost:8000/api/cache/products/abc123"
```

#### `POST /api/cache/products`
Добавление товара в кэш
```bash
curl -X POST "http://localhost:8000/api/cache/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовый товар",
    "brand": "Тестовый бренд",
    "category_level_1": "Красота и здоровье",
    "favorites_count": 1000,
    "days_out_of_stock": 10
  }'
```

#### `PUT /api/cache/products/{product_id}`
Обновление товара в кэше
```bash
curl -X PUT "http://localhost:8000/api/cache/products/abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Обновленное название",
    "favorites_count": 2000
  }'
```

#### `DELETE /api/cache/products/{product_id}`
Удаление товара из кэша
```bash
curl -X DELETE "http://localhost:8000/api/cache/products/abc123"
```

#### `DELETE /api/cache/products`
Массовое удаление товаров
```bash
curl -X DELETE "http://localhost:8000/api/cache/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": ["id1", "id2", "id3"]
  }'
```

#### `POST /api/cache/clear`
Очистка кэша
```bash
curl -X POST "http://localhost:8000/api/cache/clear"
```

#### `POST /api/cache/reload`
Перезагрузка кэша
```bash
curl -X POST "http://localhost:8000/api/cache/reload"
```

---

### 🔹 n8n Интеграция

#### `GET /api/n8n/workflows`
Список workflows

**Параметры:**
- `url` - URL n8n инстанса
- `api_key` - API ключ

**Примеры:**
```bash
# С параметрами
curl "http://localhost:8000/api/n8n/workflows?url=https://n8n.example.com&api_key=your_key"

# Без параметров (вернет моковые данные)
curl "http://localhost:8000/api/n8n/workflows"
```

#### `POST /api/n8n/workflows/{workflow_id}/toggle`
Переключение workflow (активен/неактивен)
```bash
curl -X POST "http://localhost:8000/api/n8n/workflows/123/toggle?url=https://n8n.example.com&api_key=your_key" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

#### `POST /api/n8n/workflows/{workflow_id}/execute`
Запуск workflow
```bash
curl -X POST "http://localhost:8000/api/n8n/workflows/123/execute?url=https://n8n.example.com&api_key=your_key" \
  -H "Content-Type: application/json" \
  -d '{"data": {}}'
```

#### `GET /api/n8n/workflows/{workflow_id}`
Получение информации о workflow
```bash
curl "http://localhost:8000/api/n8n/workflows/123?url=https://n8n.example.com&api_key=your_key"
```

#### `POST /api/n8n/test-connection`
Тест подключения к n8n
```bash
curl -X POST "http://localhost:8000/api/n8n/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://n8n.example.com",
    "api_key": "your_key"
  }'
```

---

### 🔹 Telegram Интеграция

#### `POST /api/telegram/command`
Обработка команды из Telegram

**Поддерживаемые команды:**
- `/stats` - Статистика кэша
- `/cache_clear` - Очистить кэш
- `/cache_reload` - Перезагрузить кэш
- `/products_count` - Количество товаров
- `/dashboard` - Дашборд
- `/products` - Информация о товарах
- `/analytics` - Аналитика
- `/pricing` - Ценообразование
- `/cache` - Управление кэшем
- `/help` - Список команд

**Примеры:**
```bash
# Статистика
curl -X POST "http://localhost:8000/api/telegram/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "/stats",
    "chat_id": "123456",
    "user_id": "789012"
  }'

# Дашборд
curl -X POST "http://localhost:8000/api/telegram/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "/dashboard"
  }'
```

#### `POST /api/telegram/webhook`
Webhook для получения сообщений из Telegram
```bash
curl -X POST "http://localhost:8000/api/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "/stats",
      "chat": {"id": 123456},
      "from": {"id": 789012}
    }
  }'
```

#### `POST /api/telegram/bot/settings`
Сохранение настроек Telegram бота
```bash
curl -X POST "http://localhost:8000/api/telegram/bot/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "webhook_url": "https://your-domain.com/api/telegram/webhook"
  }'
```

#### `GET /api/telegram/bot/status`
Статус Telegram бота
```bash
curl "http://localhost:8000/api/telegram/bot/status"
```

#### `POST /api/telegram/bot/send-message`
Отправка сообщения через бота
```bash
curl -X POST "http://localhost:8000/api/telegram/bot/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456",
    "message": "Тестовое сообщение"
  }'
```

#### `POST /api/telegram/bot/set-menu`
Установка меню команд в боте
```bash
curl -X POST "http://localhost:8000/api/telegram/bot/set-menu"
```

---

## 🧪 Примеры тестирования

### Тестирование через pytest

```bash
# Все тесты
pytest tests/ -v

# Только тесты товаров
pytest tests/test_products.py -v

# Только тесты аналитики
pytest tests/test_analytics.py -v

# Тесты дашборда
pytest tests/test_dashboard_integration.py -v

# С покрытием кода
pytest tests/ --cov=app --cov-report=html
```

### Тестирование через curl (bash скрипт)

Создайте файл `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🔍 Тестирование API..."

# 1. Проверка здоровья
echo "1. Health check:"
curl -s "$BASE_URL/health" | jq .

# 2. Статус
echo "2. Status:"
curl -s "$BASE_URL/api/status" | jq .

# 3. Товары
echo "3. Products (first page):"
curl -s "$BASE_URL/api/products?page=1&page_size=5" | jq '.total, .products | length'

# 4. Топ товаров
echo "4. Top products:"
curl -s "$BASE_URL/api/analytics/demand/top?limit=5" | jq 'length'

# 5. Метрики ценообразования
echo "5. Pricing metrics:"
curl -s "$BASE_URL/api/analytics/pricing-metrics?min_days_out_of_stock=15" | jq '.total'

# 6. Статистика кэша
echo "6. Cache stats:"
curl -s "$BASE_URL/api/cache/stats" | jq '.total_products'

echo "✅ Тестирование завершено"
```

Запуск:
```bash
chmod +x test_api.sh
./test_api.sh
```

### Тестирование через Python

Создайте файл `test_manual.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

def test_endpoints():
    # 1. Health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code}")
    print(response.json())
    
    # 2. Products
    response = requests.get(f"{BASE_URL}/api/products?page=1&page_size=10")
    print(f"\nProducts: {response.status_code}")
    data = response.json()
    print(f"Total: {data['total']}, Products: {len(data['products'])}")
    
    # 3. Analytics
    response = requests.get(f"{BASE_URL}/api/analytics/demand/top?limit=5")
    print(f"\nTop products: {response.status_code}")
    print(f"Count: {len(response.json())}")
    
    # 4. Pricing metrics
    response = requests.get(f"{BASE_URL}/api/analytics/pricing-metrics?min_days_out_of_stock=15")
    print(f"\nPricing metrics: {response.status_code}")
    data = response.json()
    print(f"Total metrics: {data['total']}")

if __name__ == "__main__":
    test_endpoints()
```

Запуск:
```bash
python test_manual.py
```

---

## 📊 Проверка ответов

### Успешный ответ (200 OK)
```json
{
  "products": [...],
  "total": 1000,
  "page": 1,
  "page_size": 50
}
```

### Ошибка (400/500)
```json
{
  "detail": "Описание ошибки"
}
```

---

## 🔗 Полезные ссылки

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 💡 Советы по тестированию

1. **Начните с Swagger UI** - самый простой способ
2. **Используйте автоматические тесты** для регрессии
3. **Проверяйте граничные случаи** (пустые ответы, большие числа)
4. **Тестируйте фильтры** - комбинируйте параметры
5. **Проверяйте пагинацию** - разные размеры страниц
6. **Тестируйте ошибки** - неверные параметры, отсутствующие данные

