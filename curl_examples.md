# cURL примеры для API

## Pricing Metrics

### Базовый запрос с limit=10:
```bash
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=10" \
  -H "Accept: application/json"
```

### С форматированием JSON:
```bash
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=10" \
  -H "Accept: application/json" | jq
```

### С выводом заголовков:
```bash
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=10" \
  -H "Accept: application/json" \
  -v
```

### С сохранением в файл:
```bash
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=10" \
  -H "Accept: application/json" \
нет все)
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15" \
  -H "Accept: application/json"

# С limit=5
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=5" \
  -H "Accept: application/json"imit=20
curl -X GET "https://ozonscienceproject-production.up.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15&limit=20" \
  -H "Accept: application/json"
```
