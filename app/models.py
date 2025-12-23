from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class Product(BaseModel):
    """Модель товара"""
    id: str = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    brand: Optional[str] = Field(None, description="Бренд")
    link: Optional[str] = Field(None, description="Ссылка на товар")
    category_level_1: Optional[str] = Field(None, description="Категория 1 уровня")
    category_level_2: Optional[str] = Field(None, description="Категория 2 уровня")
    category_level_3: Optional[str] = Field(None, description="Категория 3 уровня")
    category_level_4: Optional[str] = Field(None, description="Категория 4 уровня")
    favorites_count: int = Field(..., description="Количество добавлений в избранное")
    last_in_stock: Optional[date] = Field(None, description="Последнее появление в наличии")
    period_start: Optional[date] = Field(None, description="Начало периода данных")
    period_end: Optional[date] = Field(None, description="Конец периода данных")
    days_out_of_stock: Optional[int] = Field(None, description="Дней отсутствия в наличии")


class ProductFilter(BaseModel):
    """Фильтры для поиска товаров"""
    category_level_1: Optional[str] = None
    category_level_2: Optional[str] = None
    category_level_3: Optional[str] = None
    category_level_4: Optional[str] = None
    brand: Optional[str] = None
    min_favorites_count: Optional[int] = Field(None, ge=0)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    out_of_stock_days: Optional[int] = Field(None, ge=0, description="Минимальное количество дней отсутствия в наличии")


class ProductListResponse(BaseModel):
    """Ответ со списком товаров"""
    products: List[Product]
    total: int
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total_pages: int


class DemandMetrics(BaseModel):
    """Метрики спроса"""
    product_id: str
    product_name: str
    brand: Optional[str]
    category_level_1: Optional[str]
    favorites_count: int
    period_start: Optional[date]
    period_end: Optional[date]
    rank: Optional[int] = None


class TrendData(BaseModel):
    """Данные тренда"""
    period: str
    category: Optional[str]
    brand: Optional[str]
    total_favorites: int
    unique_products: int
    avg_favorites_per_product: float


class TimeSeriesPoint(BaseModel):
    """Точка временного ряда"""
    date: date
    value: int
    category: Optional[str] = None
    brand: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Ответ с временным рядом"""
    data: List[TimeSeriesPoint]
    group_by: Optional[str] = None


class OutOfStockProduct(BaseModel):
    """Товар, отсутствующий в наличии"""
    product_id: str
    product_name: str
    brand: Optional[str]
    category_level_1: Optional[str]
    last_in_stock: date
    days_out_of_stock: int
    favorites_count: int
    priority_score: float = Field(..., description="Приоритетность для пополнения (на основе спроса и длительности отсутствия)")


class PricingMetric(BaseModel):
    """Метрика для динамического ценообразования"""
    product_id: str
    product_name: str
    brand: Optional[str]
    category_level_1: Optional[str]
    demand_level: str = Field(..., description="Уровень спроса: high/medium/low")
    favorites_count: int
    days_out_of_stock: int
    priority_score: float = Field(..., description="Приоритетность товара для пополнения (0-100)")
    recommendation: str = Field(..., description="Рекомендация по действию")


class PricingMetricsResponse(BaseModel):
    """Ответ с метриками ценообразования"""
    metrics: List[PricingMetric]
    total: int



