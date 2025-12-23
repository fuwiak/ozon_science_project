from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from app.routers import products, analytics
from contextlib import asynccontextmanager


# Определяем путь к папке с данными (относительно корня проекта)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # При старте приложения
    print("🚀 Запуск приложения...")
    
    # Предзагружаем данные: сначала быстрый старт, затем остальные файлы
    from app.services.excel_loader import get_loader
    loader = get_loader(DATA_DIR)
    loader.preload_data_async()
    
    print("✅ Приложение готово к работе! Демонстрационные данные загружены, реальные данные загружаются в фоне...")
    
    yield
    
    # При остановке приложения
    print("🛑 Остановка приложения...")


app = FastAPI(
    title="OZON Dynamic Pricing API",
    description="REST API для анализа данных OZON о товарах в избранном и поддержки динамического ценообразования",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
# В продакшене можно указать конкретные домены через переменную окружения
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(products.router)
app.include_router(analytics.router)

# Подключение роутера для n8n интеграции
from app.routers import n8n
app.include_router(n8n.router)

# Подключение роутера для администрирования кэша
from app.routers import cache
app.include_router(cache.router)

# Подключение роутера для Telegram интеграции
from app.routers import telegram
app.include_router(telegram.router)


@app.get("/")
async def root():
    """Корневой эндпоинт с информацией об API"""
    return {
        "message": "OZON Dynamic Pricing API",
        "version": "1.0.0",
        "docs": "/docs",
            "endpoints": {
            "products": "/api/products",
            "analytics": "/api/analytics",
            "n8n": "/api/n8n"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    try:
        # Проверяем доступность данных
        from app.services.excel_loader import get_loader
        loader = get_loader(DATA_DIR)
        
        # Проверяем, загружены ли данные
        if loader._cache is None:
            return {
                "status": "loading",
                "message": "Данные загружаются в фоновом режиме",
                "data_files_loaded": 0,
                "total_products": 0,
                "using_mock_data": False
            }
        
        df = loader._cache
        return {
            "status": "healthy",
            "data_files_loaded": len(loader.get_file_metadata()),
            "total_products": len(df),
            "cache_ready": True,
            "using_mock_data": loader._using_mock_data,
            "message": "⚠️ Используются демонстрационные данные. Реальные данные загружаются в фоне." if loader._using_mock_data else "✅ Используются реальные данные"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/status")
async def get_status():
    """Получить статус загрузки данных"""
    from app.services.excel_loader import get_loader
    loader = get_loader(DATA_DIR)
    
    return {
        "cache_ready": loader._cache is not None,
        "loading": loader._loading,
        "files_loaded": len(loader.get_file_metadata()) if loader._cache is not None else 0,
        "total_products": len(loader._cache) if loader._cache is not None else 0,
        "using_mock_data": loader._using_mock_data,
        "message": "⚠️ Используются демонстрационные данные. Реальные данные загружаются в фоне." if loader._using_mock_data else "✅ Используются реальные данные"
    }


if __name__ == "__main__":
    import uvicorn
    # Railway использует переменную PORT, по умолчанию 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
