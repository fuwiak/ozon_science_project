# OZON Dynamic Pricing API

REST API на FastAPI для анализа данных OZON о товарах, добавленных в избранное, с целью поддержки динамического ценообразования.

## Описание

API предоставляет инструменты для:
- Поиска и фильтрации товаров по различным критериям
- Анализа уровня спроса (количество добавлений в избранное)
- Мониторинга остатков (товары, отсутствующие в наличии)
- Анализа трендов и временных рядов
- Получения метрик для принятия решений по ценообразованию

## Установка

1. Создайте виртуальное окружение (рекомендуется):
```bash
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Убедитесь, что данные находятся в папке `data/` (Excel файлы с данными OZON)

4. Создайте файл `.env` (опционально, для настройки путей):
```bash
DATA_DIR=data
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Запуск

```bash
# Активируйте виртуальное окружение (если используете)
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Запуск через uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или напрямую через Python
python -m app.main
```

## Тестирование

```bash
# Активируйте виртуальное окружение
source .venv/bin/activate

# Запустите тесты
pytest tests/ -v

# Или с более подробным выводом
pytest tests/ -v --tb=short
```

После запуска API будет доступен по адресу:
- API: http://localhost:8000
- Swagger документация: http://localhost:8000/docs
- ReDoc документация: http://localhost:8000/redoc

## Эндпоинты

### Товары

#### `GET /api/products`
Поиск товаров с фильтрацией и пагинацией.

**Параметры запроса:**
- `category_level_1` (optional) - Категория 1 уровня
- `category_level_2` (optional) - Категория 2 уровня
- `category_level_3` (optional) - Категория 3 уровня
- `category_level_4` (optional) - Категория 4 уровня
- `brand` (optional) - Бренд
- `min_favorites_count` (optional) - Минимальное количество добавлений в избранное
- `period_start` (optional) - Начало периода (YYYY-MM-DD)
- `period_end` (optional) - Конец периода (YYYY-MM-DD)
- `out_of_stock_days` (optional) - Минимальное количество дней отсутствия в наличии
- `page` (default: 1) - Номер страницы
- `page_size` (default: 50) - Размер страницы

**Пример:**
```bash
GET /api/products?category_level_1=Красота%20и%20здоровье&min_favorites_count=1000&page=1&page_size=20
```

#### `GET /api/products/{product_id}`
Получение детальной информации о товаре по ID.

**Пример:**
```bash
GET /api/products/abc123def456
```

#### `GET /api/products/categories/list`
Получение списка всех категорий 1 уровня.

#### `GET /api/products/brands/list`
Получение списка всех брендов.

**Параметры:**
- `category` (optional) - Фильтр по категории

### Аналитика

#### `GET /api/analytics/demand/top`
Получение топ N товаров по количеству добавлений в избранное.

**Параметры:**
- `limit` (default: 10) - Количество товаров в топе
- `category` (optional) - Фильтр по категории
- `brand` (optional) - Фильтр по бренду
- `period_start` (optional) - Начало периода
- `period_end` (optional) - Конец периода

**Пример:**
```bash
GET /api/analytics/demand/top?limit=20&category=Красота%20и%20здоровье
```

#### `GET /api/analytics/demand/trends`
Анализ трендов спроса.

**Параметры:**
- `category` (optional) - Фильтр по категории
- `brand` (optional) - Фильтр по бренду
- `group_by` (default: "category") - Группировка: "category", "brand" или "period"

**Пример:**
```bash
GET /api/analytics/demand/trends?group_by=brand
```

#### `GET /api/analytics/stock/out-of-stock`
Получение товаров, отсутствующих в наличии более указанного количества дней.

**Параметры:**
- `min_days` (default: 15) - Минимальное количество дней отсутствия
- `category` (optional) - Фильтр по категории
- `brand` (optional) - Фильтр по бренду
- `period_start` (optional) - Начало периода
- `period_end` (optional) - Конец периода

**Пример:**
```bash
GET /api/analytics/stock/out-of-stock?min_days=30&category=Красота%20и%20здоровье
```

#### `GET /api/analytics/timeseries`
Получение временного ряда добавлений в избранное.

**Параметры:**
- `category` (optional) - Фильтр по категории
- `brand` (optional) - Фильтр по бренду
- `group_by` (optional) - Группировка: "category" или "brand"
- `period` (default: "month") - Период агрегации: "day", "week" или "month"

**Пример:**
```bash
GET /api/analytics/timeseries?period=week&group_by=category
```

#### `GET /api/analytics/pricing-metrics`
Получение комплексных метрик для динамического ценообразования.

**Параметры:**
- `category` (optional) - Фильтр по категории
- `brand` (optional) - Фильтр по бренду
- `min_days_out_of_stock` (default: 15) - Минимальное количество дней отсутствия

**Пример:**
```bash
GET /api/analytics/pricing-metrics?category=Красота%20и%20здоровье&min_days_out_of_stock=20
```

**Ответ включает:**
- `demand_level` - Уровень спроса (high/medium/low)
- `favorites_count` - Количество добавлений в избранное
- `days_out_of_stock` - Дней отсутствия в наличии
- `priority_score` - Приоритетность для пополнения (0-100)
- `recommendation` - Рекомендация по действию

### Служебные эндпоинты

#### `GET /`
Корневой эндпоинт с информацией об API.

#### `GET /health`
Проверка здоровья API и доступности данных.

## Структура проекта

```
ozon_science_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI
│   ├── models.py            # Pydantic модели
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_loader.py  # Загрузка Excel файлов
│   │   ├── product_service.py  # Логика работы с товарами
│   │   └── analytics_service.py  # Аналитика и метрики
│   └── routers/
│       ├── __init__.py
│       ├── products.py      # Эндпоинты товаров
│       └── analytics.py    # Эндпоинты аналитики
├── data/                    # Excel файлы с данными
├── requirements.txt
└── README.md
```

## Особенности

1. **Ленивая загрузка данных** - Excel файлы загружаются только при первом запросе
2. **Кэширование** - Загруженные данные кэшируются в памяти для быстрого доступа
3. **Нормализация данных** - Автоматическая унификация разных форматов колонок в Excel файлах
4. **Автоматическая документация** - Swagger UI доступен по адресу `/docs`

## Использование для динамического ценообразования

API предоставляет следующие метрики для принятия решений:

1. **Уровень спроса** - на основе количества добавлений в избранное
2. **Длительность отсутствия** - сколько дней товар отсутствует в наличии
3. **Приоритетность** - комбинированная метрика для определения приоритета пополнения
4. **Рекомендации** - автоматические рекомендации по действиям

Пример использования:
```bash
# Получить метрики для категории "Красота и здоровье"
curl "http://localhost:8000/api/analytics/pricing-metrics?category=Красота%20и%20здоровье&min_days_out_of_stock=15"

# Получить топ товаров с высоким спросом
curl "http://localhost:8000/api/analytics/demand/top?limit=50&min_favorites_count=5000"

# Получить товары, требующие срочного пополнения
curl "http://localhost:8000/api/analytics/stock/out-of-stock?min_days=30"
```

## Лицензия

Данные предоставлены OZON. Воспроизведение, распространение, копирование данных, а также публикация любых результатов, полученных с использованием данных полностью или в части допускается с обязательным указанием на источник — www.ozon.ru, ООО «Интернет Решения».

