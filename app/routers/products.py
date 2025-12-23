from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional
from datetime import date
from app.models import Product, ProductFilter, ProductListResponse
from app.services.product_service import get_product_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def search_products(
    category_level_1: Optional[str] = Query(None, description="Категория 1 уровня"),
    category_level_2: Optional[str] = Query(None, description="Категория 2 уровня"),
    category_level_3: Optional[str] = Query(None, description="Категория 3 уровня"),
    category_level_4: Optional[str] = Query(None, description="Категория 4 уровня"),
    brand: Optional[str] = Query(None, description="Бренд"),
    min_favorites_count: Optional[int] = Query(None, ge=0, description="Минимальное количество добавлений в избранное"),
    period_start: Optional[date] = Query(None, description="Начало периода"),
    period_end: Optional[date] = Query(None, description="Конец периода"),
    out_of_stock_days: Optional[int] = Query(None, ge=0, description="Минимальное количество дней отсутствия в наличии"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=1000, description="Размер страницы")
):
    """
    Поиск товаров с фильтрацией и пагинацией
    
    Поддерживает фильтрацию по:
    - Категориям (4 уровня)
    - Бренду
    - Количеству добавлений в избранное
    - Периоду данных
    - Дням отсутствия в наличии
    """
    try:
        service = get_product_service()
        
        filters = ProductFilter(
            category_level_1=category_level_1,
            category_level_2=category_level_2,
            category_level_3=category_level_3,
            category_level_4=category_level_4,
            brand=brand,
            min_favorites_count=min_favorites_count,
            period_start=period_start,
            period_end=period_end,
            out_of_stock_days=out_of_stock_days
        )
        
        products, total = service.search_products(filters, page=page, page_size=page_size)
        
        total_pages = (total + page_size - 1) // page_size
        
        return ProductListResponse(
            products=products,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске товаров: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str = Path(..., description="ID товара")):
    """
    Получает детальную информацию о товаре по ID
    """
    try:
        service = get_product_service()
        product = service.get_product_by_id(product_id)
        
        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении товара: {str(e)}")


@router.get("/categories/list", response_model=list[str])
async def get_categories():
    """
    Получает список всех категорий 1 уровня
    """
    try:
        service = get_product_service()
        categories = service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении категорий: {str(e)}")


@router.get("/brands/list", response_model=list[str])
async def get_brands(
    category: Optional[str] = Query(None, description="Фильтр по категории")
):
    """
    Получает список всех брендов (опционально с фильтром по категории)
    """
    try:
        service = get_product_service()
        brands = service.get_brands(category=category)
        return brands
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении брендов: {str(e)}")



