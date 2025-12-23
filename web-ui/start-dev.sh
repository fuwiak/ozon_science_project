#!/bin/bash
# Скрипт для запуска Next.js dev сервера с автоматической очисткой портов

echo "🧹 Очистка портов и lock файлов..."

# Убиваем процессы на портах 3000 и 3001
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# Удаляем lock файлы
rm -rf .next/dev/lock 2>/dev/null

# Убиваем все процессы Next.js
ps aux | grep -E "next dev|node.*next" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

echo "✅ Очистка завершена"
echo "🚀 Запуск Next.js dev сервера..."
echo ""

npm run dev



