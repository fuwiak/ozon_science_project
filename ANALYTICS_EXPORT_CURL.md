# Примеры curl команд для экспорта данных аналитики

**Base URL (Production):** `https://ozonscienceproject-production.up.railway.app`  
**Local URL (для разработки):** `http://localhost:8000`

## 📊 Экспорт топ товаров по спросу

### CSV формат
```bash
# Экспорт топ 100 товаров в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=csv&limit=100" -o top_products.csv

# Экспорт топ 1000 товаров с фильтром по категории (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=csv&limit=1000&category=Красота%20и%20здоровье" -o top_products_category.csv

# Экспорт топ товаров с фильтром по бренду (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=csv&limit=500&brand=BrandName" -o top_products_brand.csv

# Экспорт за период (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=csv&limit=1000&period_start=2024-01-01&period_end=2024-01-31" -o top_products_period.csv
```

### Excel формат
```bash
# Экспорт топ 100 товаров в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=excel&limit=100" -o top_products.xlsx

# Экспорт топ 1000 товаров с фильтром по категории в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=excel&limit=1000&category=Красота%20и%20здоровье" -o top_products_category.xlsx

# Экспорт топ товаров с фильтром по бренду в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=excel&limit=500&brand=BrandName" -o top_products_brand.xlsx

# Экспорт за период в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/top?format=excel&limit=1000&period_start=2024-01-01&period_end=2024-01-31" -o top_products_period.xlsx
```

## 📈 Экспорт трендов спроса

### CSV формат
```bash
# Экспорт трендов по категориям в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=csv&group_by=category" -o demand_trends_category.csv

# Экспорт трендов по брендам в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=csv&group_by=brand" -o demand_trends_brand.csv

# Экспорт трендов по периодам в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=csv&group_by=period" -o demand_trends_period.csv

# Экспорт трендов с фильтром по категории (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=csv&group_by=category&category=Красота%20и%20здоровье" -o demand_trends_filtered.csv
```

### Excel формат
```bash
# Экспорт трендов по категориям в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=excel&group_by=category" -o demand_trends_category.xlsx

# Экспорт трендов по брендам в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=excel&group_by=brand" -o demand_trends_brand.xlsx

# Экспорт трендов по периодам в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/demand/trends?format=excel&group_by=period" -o demand_trends_period.xlsx
```

## 📅 Экспорт временных рядов

### CSV формат
```bash
# Экспорт временного ряда по месяцам в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=month" -o timeseries_month.csv

# Экспорт временного ряда по неделям в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=week" -o timeseries_week.csv

# Экспорт временного ряда по дням в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=day" -o timeseries_day.csv

# Экспорт с группировкой по категориям (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=month&group_by=category" -o timeseries_category.csv

# Экспорт с группировкой по брендам (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=month&group_by=brand" -o timeseries_brand.csv

# Экспорт с фильтром по категории (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=csv&period=month&category=Красота%20и%20здоровье" -o timeseries_filtered.csv
```

### Excel формат
```bash
# Экспорт временного ряда по месяцам в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=excel&period=month" -o timeseries_month.xlsx

# Экспорт временного ряда по неделям в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=excel&period=week" -o timeseries_week.xlsx

# Экспорт временного ряда по дням в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=excel&period=day" -o timeseries_day.xlsx

# Экспорт с группировкой по категориям в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/timeseries?format=excel&period=month&group_by=category" -o timeseries_category.xlsx
```

## 📦 Экспорт товаров без остатков

### CSV формат
```bash
# Экспорт товаров без остатков (15+ дней) в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=csv&min_days=15" -o out_of_stock.csv

# Экспорт критичных товаров (30+ дней) в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=csv&min_days=30" -o out_of_stock_critical.csv

# Экспорт с фильтром по категории (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=csv&min_days=15&category=Красота%20и%20здоровье" -o out_of_stock_category.csv

# Экспорт с фильтром по бренду (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=csv&min_days=15&brand=BrandName" -o out_of_stock_brand.csv
```

### Excel формат
```bash
# Экспорт товаров без остатков (15+ дней) в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=excel&min_days=15" -o out_of_stock.xlsx

# Экспорт критичных товаров (30+ дней) в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=excel&min_days=30" -o out_of_stock_critical.xlsx

# Экспорт с фильтром по категории в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/out-of-stock?format=excel&min_days=15&category=Красота%20и%20здоровье" -o out_of_stock_category.xlsx
```

## 💰 Экспорт метрик ценообразования

### CSV формат
```bash
# Экспорт метрик ценообразования в CSV (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=csv&min_days_out_of_stock=15&limit=500" -o pricing_metrics.csv

# Экспорт метрик с фильтром по категории (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=csv&min_days_out_of_stock=15&limit=500&category=Красота%20и%20здоровье" -o pricing_metrics_category.csv

# Экспорт метрик с фильтром по бренду (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=csv&min_days_out_of_stock=15&limit=500&brand=BrandName" -o pricing_metrics_brand.csv

# Экспорт критичных метрик (30+ дней) (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=csv&min_days_out_of_stock=30&limit=1000" -o pricing_metrics_critical.csv
```

### Excel формат
```bash
# Экспорт метрик ценообразования в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=excel&min_days_out_of_stock=15&limit=500" -o pricing_metrics.xlsx

# Экспорт метрик с фильтром по категории в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=excel&min_days_out_of_stock=15&limit=500&category=Красота%20и%20здоровье" -o pricing_metrics_category.xlsx

# Экспорт критичных метрик (30+ дней) в Excel (Railway)
curl "https://ozonscienceproject-production.up.railway.app/api/analytics/export/pricing-metrics?format=excel&min_days_out_of_stock=30&limit=1000" -o pricing_metrics_critical.xlsx
```

## 🖥️ Примеры для локальной разработки

Для локальной разработки замените URL на `http://localhost:8000`:

```bash
# Экспорт топ товаров в CSV (локально)
curl "http://localhost:8000/api/analytics/export/demand/top?format=csv&limit=1000" -o top_products.csv

# Экспорт трендов в Excel (локально)
curl "http://localhost:8000/api/analytics/export/demand/trends?format=excel&group_by=category" -o demand_trends.xlsx

# Экспорт временных рядов в CSV (локально)
curl "http://localhost:8000/api/analytics/export/timeseries?format=csv&period=month" -o timeseries.csv

# Экспорт товаров без остатков в Excel (локально)
curl "http://localhost:8000/api/analytics/export/out-of-stock?format=excel&min_days=30" -o out_of_stock.xlsx

# Экспорт метрик ценообразования в CSV (локально)
curl "http://localhost:8000/api/analytics/export/pricing-metrics?format=csv&limit=500" -o pricing_metrics.csv
```

## 📝 Параметры запросов

### Общие параметры для всех эндпоинтов:
- `format` - Формат экспорта: `csv` или `excel` (по умолчанию: `csv`)

### Параметры для `/export/demand/top`:
- `limit` - Количество товаров (1-10000, по умолчанию: 1000)
- `category` - Фильтр по категории (опционально)
- `brand` - Фильтр по бренду (опционально)
- `period_start` - Начало периода в формате YYYY-MM-DD (опционально)
- `period_end` - Конец периода в формате YYYY-MM-DD (опционально)

### Параметры для `/export/demand/trends`:
- `group_by` - Группировка: `category`, `brand` или `period` (по умолчанию: `category`)
- `category` - Фильтр по категории (опционально)
- `brand` - Фильтр по бренду (опционально)

### Параметры для `/export/timeseries`:
- `period` - Период агрегации: `day`, `week` или `month` (по умолчанию: `month`)
- `group_by` - Группировка: `category` или `brand` (опционально)
- `category` - Фильтр по категории (опционально)
- `brand` - Фильтр по бренду (опционально)

### Параметры для `/export/out-of-stock`:
- `min_days` - Минимальное количество дней отсутствия (по умолчанию: 15)
- `category` - Фильтр по категории (опционально)
- `brand` - Фильтр по бренду (опционально)

### Параметры для `/export/pricing-metrics`:
- `min_days_out_of_stock` - Минимальное количество дней отсутствия (по умолчанию: 15)
- `limit` - Максимальное количество метрик (1-5000, по умолчанию: 500)
- `category` - Фильтр по категории (опционально)
- `brand` - Фильтр по бренду (опционально)

## 🔍 Примеры использования в скриптах

### Bash скрипт для экспорта всех данных (Railway)
```bash
#!/bin/bash

BASE_URL="https://ozonscienceproject-production.up.railway.app"
OUTPUT_DIR="./exports"

mkdir -p "$OUTPUT_DIR"

# Экспорт всех типов данных
echo "Экспорт топ товаров..."
curl "${BASE_URL}/api/analytics/export/demand/top?format=csv&limit=1000" -o "${OUTPUT_DIR}/top_products.csv"

echo "Экспорт трендов..."
curl "${BASE_URL}/api/analytics/export/demand/trends?format=csv&group_by=category" -o "${OUTPUT_DIR}/demand_trends.csv"

echo "Экспорт временных рядов..."
curl "${BASE_URL}/api/analytics/export/timeseries?format=csv&period=month" -o "${OUTPUT_DIR}/timeseries.csv"

echo "Экспорт товаров без остатков..."
curl "${BASE_URL}/api/analytics/export/out-of-stock?format=csv&min_days=15" -o "${OUTPUT_DIR}/out_of_stock.csv"

echo "Экспорт метрик ценообразования..."
curl "${BASE_URL}/api/analytics/export/pricing-metrics?format=csv&limit=500" -o "${OUTPUT_DIR}/pricing_metrics.csv"

echo "Экспорт завершен! Файлы сохранены в ${OUTPUT_DIR}/"
```

### Python скрипт для экспорта (Railway)
```python
import requests
from datetime import date

BASE_URL = "https://ozonscienceproject-production.up.railway.app"
OUTPUT_DIR = "./exports"

# Создаем директорию для экспорта
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Экспорт топ товаров
response = requests.get(f"{BASE_URL}/api/analytics/export/demand/top", params={
    "format": "csv",
    "limit": 1000
})
with open(f"{OUTPUT_DIR}/top_products.csv", "wb") as f:
    f.write(response.content)

# Экспорт трендов
response = requests.get(f"{BASE_URL}/api/analytics/export/demand/trends", params={
    "format": "excel",
    "group_by": "category"
})
with open(f"{OUTPUT_DIR}/demand_trends.xlsx", "wb") as f:
    f.write(response.content)

print("Экспорт завершен!")
```

## ⚠️ Примечания

1. **URL Encoding**: При использовании категорий с пробелами используйте URL encoding (например, `%20` для пробела)
2. **Большие файлы**: Для больших объемов данных используйте параметр `limit` для ограничения количества записей
3. **Кодировка**: CSV файлы экспортируются в UTF-8 с BOM для корректного отображения в Excel
4. **Производительность**: Excel формат может быть медленнее для больших объемов данных (>10000 записей)
