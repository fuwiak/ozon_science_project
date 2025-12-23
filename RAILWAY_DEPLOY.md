# Wdrożenie na Railway

## Wymagania

1. Konto na Railway: https://railway.app
2. Git repository z kodem
3. Dockerfile (już przygotowany)

## Kroki wdrożenia

### 1. Przygotowanie repozytorium

Upewnij się, że masz:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ Kod aplikacji w folderze `app/`
- ✅ Dane w folderze `data/` (opcjonalnie, można dodać później)

### 2. Wdrożenie na Railway

#### Opcja A: Przez Railway CLI

```bash
# Zainstaluj Railway CLI
npm i -g @railway/cli

# Zaloguj się
railway login

# Inicjalizuj projekt
railway init

# Wdróż
railway up
```

#### Opcja B: Przez GitHub (Rekomendowane)

1. **Push kodu do GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Połącz z Railway:**
   - Otwórz https://railway.app
   - Kliknij "New Project"
   - Wybierz "Deploy from GitHub repo"
   - Wybierz swoje repozytorium
   - Railway automatycznie wykryje Dockerfile

3. **Skonfiguruj zmienne środowiskowe:**
   - W Railway Dashboard → Settings → Variables
   - Dodaj:
     ```
     DATA_DIR=/app/data
     PORT=8000 (automatycznie ustawiane przez Railway)
     ```

### 3. Dodanie danych

Railway nie przechowuje danych między wdrożeniami. Masz kilka opcji:

#### Opcja A: Volume (Rekomendowane dla danych)

1. W Railway Dashboard → Settings → Volumes
2. Dodaj volume dla `/app/data`
3. Prześlij pliki Excel do volume

#### Opcja B: S3 / Cloud Storage

Zmodyfikuj kod aby pobierał dane z S3 lub innego cloud storage.

#### Opcja C: Wbudowane dane w obrazie

Dodaj dane do Dockerfile (większy obraz):
```dockerfile
COPY data/ /app/data/
```

### 4. Konfiguracja zmiennych środowiskowych

W Railway Dashboard → Settings → Variables dodaj:

```
DATA_DIR=/app/data
N8N_URL=https://your-n8n-instance.com (opcjonalnie)
N8N_API_KEY=your-api-key (opcjonalnie)
```

### 5. Sprawdzenie wdrożenia

Po wdrożeniu Railway poda URL aplikacji:
- API: `https://your-app.railway.app`
- Swagger: `https://your-app.railway.app/docs`
- Health: `https://your-app.railway.app/health`

## Testowanie zdalnych endpointów

Po wdrożeniu możesz testować endpointy:

```bash
# Health check
curl https://your-app.railway.app/health

# Status
curl https://your-app.railway.app/api/status

# Produkty
curl "https://your-app.railway.app/api/products?page=1&page_size=10"

# Top produkty
curl "https://your-app.railway.app/api/analytics/demand/top?limit=5"

# Metryki cenowe
curl "https://your-app.railway.app/api/analytics/pricing-metrics?min_days_out_of_stock=15"
```

## Aktualizacja frontendu

Zaktualizuj `web-ui/.env.local` lub `web-ui/lib/api.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-app.railway.app';
```

## Monitoring i logi

- **Logi:** Railway Dashboard → Deployments → View Logs
- **Metryki:** Railway Dashboard → Metrics
- **Health checks:** Railway automatycznie sprawdza `/health`

## Troubleshooting

### Problem: Aplikacja nie startuje

1. Sprawdź logi w Railway Dashboard
2. Upewnij się, że PORT jest ustawiony (Railway to robi automatycznie)
3. Sprawdź czy wszystkie zależności są w `requirements.txt`

### Problem: Brak danych

1. Sprawdź czy folder `data/` istnieje w kontenerze
2. Upewnij się, że `DATA_DIR` jest poprawnie ustawiony
3. Sprawdź logi podczas startu aplikacji

### Problem: Timeout przy starcie

Aplikacja ładuje dane w tle. Jeśli timeout jest zbyt krótki:
- Railway automatycznie restartuje kontener
- Dane będą ładowane przy każdym restarcie
- Rozważ użycie volume dla cache

## Optymalizacja

### 1. Multi-stage build (mniejszy obraz)

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 2. Cache dla danych

Użyj Railway Volume dla folderu `cache/` aby przyspieszyć kolejne starty.

### 3. Health checks

Railway automatycznie sprawdza `/health` endpoint.

## Koszty

Railway oferuje:
- **Free tier:** $5 darmowych kredytów miesięcznie
- **Pro:** $20/miesiąc za więcej zasobów

Sprawdź aktualne ceny: https://railway.app/pricing

## Bezpieczeństwo

1. **CORS:** Zaktualizuj `allow_origins` w `app/main.py` dla produkcji
2. **Secrets:** Używaj Railway Variables dla wrażliwych danych
3. **HTTPS:** Railway automatycznie zapewnia HTTPS

## Przykładowe zmienne środowiskowe dla produkcji

```
DATA_DIR=/app/data
N8N_URL=https://your-n8n-instance.com
N8N_API_KEY=your-secret-key
CORS_ORIGINS=https://your-frontend-domain.com
```

