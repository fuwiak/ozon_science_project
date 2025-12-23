# Publikacja na GitHub

## Status

✅ Git zainicjalizowany
✅ Pliki dodane
✅ Initial commit utworzony

## Następne kroki

### 1. Utwórz repozytorium na GitHub

1. Przejdź do: https://github.com/new
2. Wprowadź nazwę repozytorium (np. `ozon-dynamic-pricing`)
3. **NIE** zaznaczaj "Initialize with README" (już mamy pliki)
4. Kliknij "Create repository"

### 2. Dodaj remote i opublikuj

Po utworzeniu repozytorium GitHub pokaże instrukcje. Użyj:

```bash
# Dodaj remote (zamień YOUR_USERNAME i YOUR_REPO na swoje)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Lub z SSH (jeśli masz skonfigurowane klucze):
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# Zmień nazwę głównej gałęzi na main (jeśli potrzeba)
git branch -M main

# Opublikuj kod
git push -u origin main
```

### 3. Alternatywnie - przez GitHub CLI

```bash
# Zainstaluj GitHub CLI (jeśli nie masz)
# brew install gh  # macOS
# lub: https://cli.github.com/

# Zaloguj się
gh auth login

# Utwórz repozytorium i opublikuj
gh repo create ozon-dynamic-pricing --public --source=. --remote=origin --push
```

## Sprawdzenie

Po publikacji sprawdź:
- ✅ Repozytorium widoczne na GitHub
- ✅ Wszystkie pliki są tam
- ✅ README.md wyświetla się poprawnie

## Ważne pliki w .gitignore

Następujące pliki/katalogi **NIE** będą opublikowane:
- `.venv/` - wirtualne środowisko Python
- `__pycache__/` - cache Python
- `.env` - zmienne środowiskowe (wrażliwe dane)
- `cache/` - cache SQLite
- `telegram_config.json` - konfiguracja Telegram
- `node_modules/` - zależności Node.js
- `.next/` - build Next.js

## Bezpieczeństwo

⚠️ **WAŻNE:** Przed publikacją sprawdź, że:
- ✅ Brak haseł/tokenów w kodzie
- ✅ `.env` jest w `.gitignore`
- ✅ `telegram_config.json` jest w `.gitignore`
- ✅ Brak wrażliwych danych w commitach

## Aktualizacja kodu

Po zmianach w kodzie:

```bash
git add .
git commit -m "Opis zmian"
git push
```

## Railway deployment z GitHub

Po publikacji na GitHub możesz:
1. Połączyć Railway z GitHub
2. Railway automatycznie wdraża przy każdym push
3. Railway używa Dockerfile do budowania

