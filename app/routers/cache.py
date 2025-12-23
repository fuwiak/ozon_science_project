"""
Эндпоинты для администрирования кэша
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.services.excel_loader import get_loader
import os
import pandas as pd

router = APIRouter(prefix="/api/cache", tags=["cache"])


class CacheStats(BaseModel):
    """Статистика кэша"""
    total_products: int
    files_loaded: int
    using_mock_data: bool
    cache_size_mb: float
    file_metadata: Dict[str, Dict]


class ProductItem(BaseModel):
    """Элемент товара для добавления/обновления"""
    id: Optional[str] = None
    name: str
    brand: Optional[str] = None
    link: Optional[str] = None
    category_level_1: Optional[str] = None
    category_level_2: Optional[str] = None
    category_level_3: Optional[str] = None
    category_level_4: Optional[str] = None
    favorites_count: int = 0
    last_in_stock: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    days_out_of_stock: Optional[int] = None


class ProductListRequest(BaseModel):
    """Запрос списка товаров с фильтрацией"""
    page: int = 1
    page_size: int = 50
    search: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None


class ProductListResponse(BaseModel):
    """Ответ со списком товаров"""
    products: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/stats", response_model=CacheStats)
async def get_cache_stats():
    """Получает статистику кэша"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            return CacheStats(
                total_products=0,
                files_loaded=0,
                using_mock_data=loader._using_mock_data,
                cache_size_mb=0.0,
                file_metadata={}
            )
        
        df = loader._cache
        cache_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        return CacheStats(
            total_products=len(df),
            files_loaded=len(loader.get_file_metadata()),
            using_mock_data=loader._using_mock_data,
            cache_size_mb=round(cache_size_mb, 2),
            file_metadata=loader.get_file_metadata()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статистики: {str(e)}")


@router.get("/products", response_model=ProductListResponse)
async def get_cache_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None)
):
    """Получает список товаров из кэша с фильтрацией и пагинацией"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            return ProductListResponse(
                products=[],
                total=0,
                page=page,
                page_size=page_size,
                total_pages=0
            )
        
        df = loader._cache.copy()
        
        # Фильтрация
        if search:
            mask = (
                df['name'].str.contains(search, case=False, na=False) |
                df['brand'].astype(str).str.contains(search, case=False, na=False)
            )
            df = df[mask]
        
        if category:
            df = df[df['category_level_1'] == category]
        
        if brand:
            df = df[df['brand'] == brand]
        
        total = len(df)
        total_pages = (total + page_size - 1) // page_size
        
        # Пагинация
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx]
        
        # Конвертируем в список словарей
        products = []
        for _, row in df_page.iterrows():
            products.append({
                'id': str(row.get('id', '')),
                'name': str(row.get('name', '')),
                'brand': str(row.get('brand', '')) if pd.notna(row.get('brand')) else None,
                'link': str(row.get('link', '')) if pd.notna(row.get('link')) else None,
                'category_level_1': str(row.get('category_level_1', '')) if pd.notna(row.get('category_level_1')) else None,
                'category_level_2': str(row.get('category_level_2', '')) if pd.notna(row.get('category_level_2')) else None,
                'category_level_3': str(row.get('category_level_3', '')) if pd.notna(row.get('category_level_3')) else None,
                'category_level_4': str(row.get('category_level_4', '')) if pd.notna(row.get('category_level_4')) else None,
                'favorites_count': int(row.get('favorites_count', 0)),
                'last_in_stock': str(row.get('last_in_stock', '')) if pd.notna(row.get('last_in_stock')) else None,
                'period_start': str(row.get('period_start', '')) if pd.notna(row.get('period_start')) else None,
                'period_end': str(row.get('period_end', '')) if pd.notna(row.get('period_end')) else None,
                'days_out_of_stock': int(row.get('days_out_of_stock', 0)) if pd.notna(row.get('days_out_of_stock')) else None,
            })
        
        return ProductListResponse(
            products=products,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении товаров: {str(e)}")


@router.post("/products", response_model=Dict[str, Any])
async def add_product(product: ProductItem):
    """Добавляет товар в кэш"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        from datetime import date
        import hashlib
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            # Создаем пустой DataFrame если кэш пуст
            loader._cache = pd.DataFrame(columns=[
                'id', 'name', 'brand', 'link', 'category_level_1', 'category_level_2',
                'category_level_3', 'category_level_4', 'favorites_count', 'last_in_stock',
                'period_start', 'period_end', 'days_out_of_stock'
            ])
        
        # Генерируем ID если не указан
        product_id = product.id
        if not product_id:
            key = f"{product.name}|{product.brand}|{product.link}"
            product_id = hashlib.md5(key.encode()).hexdigest()[:16]
        
        # Проверяем, существует ли уже товар с таким ID
        if product_id in loader._cache['id'].values:
            raise HTTPException(status_code=400, detail=f"Товар с ID {product_id} уже существует")
        
        # Создаем новую строку
        new_row = {
            'id': product_id,
            'name': product.name,
            'brand': product.brand,
            'link': product.link,
            'category_level_1': product.category_level_1,
            'category_level_2': product.category_level_2,
            'category_level_3': product.category_level_3,
            'category_level_4': product.category_level_4,
            'favorites_count': product.favorites_count,
            'last_in_stock': pd.to_datetime(product.last_in_stock).date() if product.last_in_stock else None,
            'period_start': pd.to_datetime(product.period_start).date() if product.period_start else None,
            'period_end': pd.to_datetime(product.period_end).date() if product.period_end else None,
            'days_out_of_stock': product.days_out_of_stock,
        }
        
        # Вычисляем days_out_of_stock если не указан
        if product.days_out_of_stock is None and product.last_in_stock:
            from datetime import date
            today = date.today()
            last_stock = pd.to_datetime(product.last_in_stock).date()
            delta = today - last_stock
            new_row['days_out_of_stock'] = delta.days if delta.days >= 0 else 0
        
        # Добавляем в DataFrame
        new_df = pd.DataFrame([new_row])
        loader._cache = pd.concat([loader._cache, new_df], ignore_index=True)
        
        return {
            "success": True,
            "message": "Товар добавлен в кэш",
            "product_id": product_id,
            "total_products": len(loader._cache)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении товара: {str(e)}")


@router.put("/products/{product_id}", response_model=Dict[str, Any])
async def update_product(product_id: str, product: ProductItem):
    """Обновляет товар в кэше"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        from datetime import date
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            raise HTTPException(status_code=404, detail="Кэш пуст")
        
        # Ищем товар
        mask = loader._cache['id'] == product_id
        if not mask.any():
            raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")
        
        # Обновляем данные
        loader._cache.loc[mask, 'name'] = product.name
        if product.brand is not None:
            loader._cache.loc[mask, 'brand'] = product.brand
        if product.link is not None:
            loader._cache.loc[mask, 'link'] = product.link
        if product.category_level_1 is not None:
            loader._cache.loc[mask, 'category_level_1'] = product.category_level_1
        if product.category_level_2 is not None:
            loader._cache.loc[mask, 'category_level_2'] = product.category_level_2
        if product.category_level_3 is not None:
            loader._cache.loc[mask, 'category_level_3'] = product.category_level_3
        if product.category_level_4 is not None:
            loader._cache.loc[mask, 'category_level_4'] = product.category_level_4
        loader._cache.loc[mask, 'favorites_count'] = product.favorites_count
        if product.last_in_stock:
            loader._cache.loc[mask, 'last_in_stock'] = pd.to_datetime(product.last_in_stock).date()
        if product.period_start:
            loader._cache.loc[mask, 'period_start'] = pd.to_datetime(product.period_start).date()
        if product.period_end:
            loader._cache.loc[mask, 'period_end'] = pd.to_datetime(product.period_end).date()
        if product.days_out_of_stock is not None:
            loader._cache.loc[mask, 'days_out_of_stock'] = product.days_out_of_stock
        
        # Пересчитываем days_out_of_stock если нужно
        if product.days_out_of_stock is None and product.last_in_stock:
            from datetime import date
            today = date.today()
            last_stock = pd.to_datetime(product.last_in_stock).date()
            delta = today - last_stock
            loader._cache.loc[mask, 'days_out_of_stock'] = delta.days if delta.days >= 0 else 0
        elif product.days_out_of_stock is not None:
            loader._cache.loc[mask, 'days_out_of_stock'] = product.days_out_of_stock
        
        return {
            "success": True,
            "message": "Товар обновлен",
            "product_id": product_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении товара: {str(e)}")


@router.delete("/products/{product_id}", response_model=Dict[str, Any])
async def delete_product(product_id: str):
    """Удаляет товар из кэша"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            raise HTTPException(status_code=404, detail="Кэш пуст")
        
        # Ищем товар
        mask = loader._cache['id'] == product_id
        if not mask.any():
            raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")
        
        # Удаляем товар
        loader._cache = loader._cache[~mask].reset_index(drop=True)
        
        return {
            "success": True,
            "message": "Товар удален из кэша",
            "product_id": product_id,
            "total_products": len(loader._cache)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении товара: {str(e)}")


@router.delete("/products", response_model=Dict[str, Any])
async def delete_products_bulk(product_ids: List[str] = Body(..., embed=True)):
    """Удаляет несколько товаров из кэша"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            raise HTTPException(status_code=404, detail="Кэш пуст")
        
        # Удаляем товары
        mask = loader._cache['id'].isin(product_ids)
        deleted_count = mask.sum()
        loader._cache = loader._cache[~mask].reset_index(drop=True)
        
        return {
            "success": True,
            "message": f"Удалено товаров: {deleted_count}",
            "deleted_count": int(deleted_count),
            "total_products": len(loader._cache)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении товаров: {str(e)}")


@router.post("/clear", response_model=Dict[str, Any])
async def clear_cache():
    """Очищает весь кэш"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        total_products = len(loader._cache) if loader._cache is not None else 0
        loader.clear_cache()
        
        return {
            "success": True,
            "message": "Кэш очищен",
            "deleted_products": total_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при очистке кэша: {str(e)}")


@router.post("/reload", response_model=Dict[str, Any])
async def reload_cache():
    """Перезагружает кэш из файлов"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        # Перезагружаем данные
        loader.load_all_data(force_reload=True)
        
        return {
            "success": True,
            "message": "Кэш перезагружен",
            "total_products": len(loader._cache) if loader._cache is not None else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при перезагрузке кэша: {str(e)}")


@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: str):
    """Получает товар по ID из кэша"""
    try:
        from app.services.excel_loader import get_loader
        from pathlib import Path
        
        DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent / "data"))
        loader = get_loader(DATA_DIR)
        
        if loader._cache is None:
            raise HTTPException(status_code=404, detail="Кэш пуст")
        
        # Ищем товар
        mask = loader._cache['id'] == product_id
        if not mask.any():
            raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")
        
        row = loader._cache[mask].iloc[0]
        
        return {
            'id': str(row.get('id', '')),
            'name': str(row.get('name', '')),
            'brand': str(row.get('brand', '')) if pd.notna(row.get('brand')) else None,
            'link': str(row.get('link', '')) if pd.notna(row.get('link')) else None,
            'category_level_1': str(row.get('category_level_1', '')) if pd.notna(row.get('category_level_1')) else None,
            'category_level_2': str(row.get('category_level_2', '')) if pd.notna(row.get('category_level_2')) else None,
            'category_level_3': str(row.get('category_level_3', '')) if pd.notna(row.get('category_level_3')) else None,
            'category_level_4': str(row.get('category_level_4', '')) if pd.notna(row.get('category_level_4')) else None,
            'favorites_count': int(row.get('favorites_count', 0)),
            'last_in_stock': str(row.get('last_in_stock', '')) if pd.notna(row.get('last_in_stock')) else None,
            'period_start': str(row.get('period_start', '')) if pd.notna(row.get('period_start')) else None,
            'period_end': str(row.get('period_end', '')) if pd.notna(row.get('period_end')) else None,
            'days_out_of_stock': int(row.get('days_out_of_stock', 0)) if pd.notna(row.get('days_out_of_stock')) else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении товара: {str(e)}")

