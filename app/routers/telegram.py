"""
Эндпоинты для интеграции с Telegram через n8n
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import json
from pathlib import Path

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

# Путь к файлу с настройками Telegram бота
TELEGRAM_CONFIG_PATH = Path(__file__).parent.parent.parent / "telegram_config.json"


class TelegramCommand(BaseModel):
    """Модель команды из Telegram"""
    command: str = Field(..., description="Команда (например: /stats, /cache_clear)")
    chat_id: Optional[str] = Field(None, description="ID чата Telegram")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    message: Optional[str] = Field(None, description="Текст сообщения")


class TelegramResponse(BaseModel):
    """Ответ для Telegram"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/command", response_model=TelegramResponse)
async def handle_telegram_command(command: TelegramCommand):
    """
    Обрабатывает команды из Telegram через n8n webhook
    
    Поддерживаемые команды:
    - /stats - статистика кэша
    - /cache_clear - очистка кэша
    - /cache_reload - перезагрузка кэша
    - /products_count - количество товаров
    - /help - список команд
    """
    try:
        cmd = command.command.lower().strip()
        
        if cmd == "/stats" or cmd == "stats":
            from app.services.excel_loader import get_loader
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            
            if loader._cache is None:
                stats_dict = {
                    "total_products": 0,
                    "files_loaded": 0,
                    "using_mock_data": loader._using_mock_data,
                    "cache_size_mb": 0.0
                }
            else:
                import pandas as pd
                df = loader._cache
                cache_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                stats_dict = {
                    "total_products": len(df),
                    "files_loaded": len(loader.get_file_metadata()),
                    "using_mock_data": loader._using_mock_data,
                    "cache_size_mb": round(cache_size_mb, 2)
                }
            
            return TelegramResponse(
                success=True,
                message=f"📊 Статистика кэша:\n\n"
                       f"Всего товаров: {stats_dict['total_products']:,}\n"
                       f"Файлов загружено: {stats_dict['files_loaded']}\n"
                       f"Размер кэша: {stats_dict['cache_size_mb']} МБ\n"
                       f"Режим: {'Мок данные' if stats_dict['using_mock_data'] else 'Реальные данные'}",
                data=stats_dict
            )
        
        elif cmd == "/cache_clear" or cmd == "cache_clear":
            from app.services.excel_loader import get_loader
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            
            total_products = len(loader._cache) if loader._cache is not None else 0
            loader.clear_cache()
            
            return TelegramResponse(
                success=True,
                message=f"✅ Кэш очищен\nУдалено товаров: {total_products:,}",
                data={"deleted_products": total_products}
            )
        
        elif cmd == "/cache_reload" or cmd == "cache_reload":
            from app.services.excel_loader import get_loader
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            
            loader.load_all_data(force_reload=True)
            total_products = len(loader._cache) if loader._cache is not None else 0
            
            return TelegramResponse(
                success=True,
                message=f"🔄 Кэш перезагружен\nТоваров в кэше: {total_products:,}",
                data={"total_products": total_products}
            )
        
        elif cmd == "/products_count" or cmd == "products_count":
            from app.services.excel_loader import get_loader
            import os
            from pathlib import Path
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            count = len(loader._cache) if loader._cache is not None else 0
            
            return TelegramResponse(
                success=True,
                message=f"📦 Товаров в кэше: {count:,}",
                data={"count": count}
            )
        
        elif cmd == "/help" or cmd == "help" or cmd == "/start":
            help_text = """🤖 <b>Dynamic Pricing 1299$</b>

Доступные команды:

📊 <b>Дашборд</b>
/dashboard - Основные метрики и статистика

📦 <b>Товары</b>
/products - Поиск и фильтрация товаров
/products_count - Количество товаров в кэше

📈 <b>Аналитика</b>
/analytics - Спрос и тренды

💰 <b>Ценообразование</b>
/pricing - Рекомендации по ценам

🗄️ <b>Кэш</b>
/cache - Управление кэшем
/stats - Статистика кэша
/cache_clear - Очистить кэш
/cache_reload - Перезагрузить кэш

❓ <b>Помощь</b>
/help - Этот список команд"""
            
            return TelegramResponse(
                success=True,
                message=help_text
            )
        
        elif cmd == "/dashboard" or cmd == "dashboard":
            from app.services.excel_loader import get_loader
            from app.services.analytics_service import AnalyticsService
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            analytics = AnalyticsService(loader)
            
            # Получаем метрики
            metrics = analytics.get_pricing_metrics(min_days_out_of_stock=15)
            high_priority = len([m for m in metrics if m.priority_score >= 70])
            critical_stock = len([m for m in metrics if m.days_out_of_stock > 30])
            high_demand = len([m for m in metrics if m.demand_level == 'high'])
            
            dashboard_text = f"""📊 <b>Дашборд динамического ценообразования</b>

🔴 Высокий приоритет: {high_priority}
📦 Критичные остатки: {critical_stock}
📈 Высокий спрос: {high_demand}
📊 Всего метрик: {len(metrics)}

<i>Используйте /products для поиска товаров</i>"""
            
            return TelegramResponse(
                success=True,
                message=dashboard_text,
                data={"metrics": len(metrics), "high_priority": high_priority}
            )
        
        elif cmd == "/products" or cmd == "products":
            from app.services.excel_loader import get_loader
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            count = len(loader._cache) if loader._cache is not None else 0
            
            products_text = f"""📦 <b>Товары</b>

Всего товаров в кэше: {count:,}

<i>Используйте веб-интерфейс для поиска и фильтрации товаров</i>

Команды:
/products_count - Количество товаров
/cache - Управление кэшем"""
            
            return TelegramResponse(
                success=True,
                message=products_text,
                data={"count": count}
            )
        
        elif cmd == "/analytics" or cmd == "analytics":
            analytics_text = """📈 <b>Аналитика</b>

Доступные данные:
• Топ товаров по спросу
• Тренды по категориям
• Временные ряды

<i>Используйте веб-интерфейс для детальной аналитики</i>"""
            
            return TelegramResponse(
                success=True,
                message=analytics_text
            )
        
        elif cmd == "/pricing" or cmd == "pricing":
            pricing_text = """💰 <b>Ценообразование</b>

Рекомендации по ценам:
• Товары с высоким приоритетом
• Критичные остатки
• Высокий спрос

<i>Используйте /dashboard для основных метрик</i>"""
            
            return TelegramResponse(
                success=True,
                message=pricing_text
            )
        
        elif cmd == "/cache" or cmd == "cache":
            from app.services.excel_loader import get_loader
            from pathlib import Path
            import os
            
            DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
            loader = get_loader(DATA_DIR)
            
            if loader._cache is None:
                cache_size_mb = 0.0
                total_products = 0
            else:
                import pandas as pd
                df = loader._cache
                cache_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                total_products = len(df)
            
            cache_text = f"""🗄️ <b>Управление кэшем</b>

Товаров: {total_products:,}
Размер: {cache_size_mb:.2f} МБ
Режим: {'Мок данные' if loader._using_mock_data else 'Реальные данные'}

Команды:
/stats - Детальная статистика
/cache_clear - Очистить кэш
/cache_reload - Перезагрузить кэш"""
            
            return TelegramResponse(
                success=True,
                message=cache_text,
                data={"total_products": total_products, "cache_size_mb": cache_size_mb}
            )
        
        else:
            return TelegramResponse(
                success=False,
                message=f"❌ Неизвестная команда: {command.command}\nИспользуйте /help для списка команд"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки команды: {str(e)}")


@router.post("/webhook", response_model=TelegramResponse)
async def telegram_webhook(data: Dict[str, Any] = Body(...)):
    """
    Webhook для получения сообщений из Telegram через n8n
    
    Ожидает данные в формате:
    {
        "message": {
            "text": "/stats",
            "chat": {"id": 123456},
            "from": {"id": 789012}
        }
    }
    """
    try:
        message = data.get("message", {})
        text = message.get("text", "").strip()
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        
        if not text:
            return TelegramResponse(
                success=False,
                message="Пустое сообщение"
            )
        
        command = TelegramCommand(
            command=text,
            chat_id=str(chat_id) if chat_id else None,
            user_id=str(user_id) if user_id else None,
            message=text
        )
        
        return await handle_telegram_command(command)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки webhook: {str(e)}")

