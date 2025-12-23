import pandas as pd
from typing import List, Optional
import os
from pathlib import Path
from datetime import date
from app.services.excel_loader import get_loader
from app.models import Product, ProductFilter


class ProductService:
    """Сервис для работы с товарами"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.getenv("DATA_DIR", "data")
            if not os.path.isabs(data_dir):
                base_dir = Path(__file__).parent.parent.parent
                data_dir = str(base_dir / data_dir)
        self.loader = get_loader(data_dir)
    
    def _df_to_product(self, row: pd.Series) -> Product:
        """Конвертирует строку DataFrame в модель Product"""
        return Product(
            id=str(row['id']),
            name=str(row['name']) if pd.notna(row['name']) else "",
            brand=str(row['brand']) if pd.notna(row['brand']) else None,
            link=str(row['link']) if pd.notna(row['link']) else None,
            category_level_1=str(row['category_level_1']) if pd.notna(row['category_level_1']) else None,
            category_level_2=str(row['category_level_2']) if pd.notna(row['category_level_2']) else None,
            category_level_3=str(row['category_level_3']) if pd.notna(row['category_level_3']) else None,
            category_level_4=str(row['category_level_4']) if pd.notna(row['category_level_4']) else None,
            favorites_count=int(row['favorites_count']) if pd.notna(row['favorites_count']) else 0,
            last_in_stock=row['last_in_stock'] if pd.notna(row['last_in_stock']) else None,
            period_start=row['period_start'] if pd.notna(row['period_start']) else None,
            period_end=row['period_end'] if pd.notna(row['period_end']) else None,
            days_out_of_stock=int(row['days_out_of_stock']) if pd.notna(row['days_out_of_stock']) else None
        )
    
    def search_products(
        self,
        filters: ProductFilter,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[Product], int]:
        """Поиск товаров с фильтрацией и пагинацией"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Применяем фильтры
        if filters.category_level_1:
            df = df[df['category_level_1'] == filters.category_level_1]
        if filters.category_level_2:
            df = df[df['category_level_2'] == filters.category_level_2]
        if filters.category_level_3:
            df = df[df['category_level_3'] == filters.category_level_3]
        if filters.category_level_4:
            df = df[df['category_level_4'] == filters.category_level_4]
        if filters.brand:
            df = df[df['brand'] == filters.brand]
        if filters.min_favorites_count is not None:
            df = df[df['favorites_count'] >= filters.min_favorites_count]
        if filters.period_start:
            df = df[df['period_start'] >= filters.period_start]
        if filters.period_end:
            df = df[df['period_end'] <= filters.period_end]
        if filters.out_of_stock_days is not None:
            df = df[df['days_out_of_stock'] >= filters.out_of_stock_days]
        
        total = len(df)
        
        # Пагинация
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx]
        
        # Конвертируем в модели
        products = [self._df_to_product(row) for _, row in df_page.iterrows()]
        
        return products, total
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Получает товар по ID"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        product_df = df[df['id'] == product_id]
        
        if product_df.empty:
            return None
        
        # Берем первую запись (если есть дубликаты)
        row = product_df.iloc[0]
        return self._df_to_product(row)
    
    def get_out_of_stock_products(
        self,
        min_days: int = 15,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> List[Product]:
        """Получает товары, отсутствующие в наличии более указанного количества дней"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Фильтруем по дням отсутствия
        df = df[df['days_out_of_stock'] >= min_days]
        
        # Дополнительные фильтры
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        if period_start:
            df = df[df['period_start'] >= period_start]
        if period_end:
            df = df[df['period_end'] <= period_end]
        
        # Сортируем по количеству добавлений в избранное (по убыванию)
        df = df.sort_values('favorites_count', ascending=False)
        
        products = [self._df_to_product(row) for _, row in df.iterrows()]
        return products
    
    def get_categories(self) -> List[str]:
        """Получает список всех категорий 1 уровня"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        categories = df['category_level_1'].dropna().unique().tolist()
        return sorted([str(c) for c in categories])
    
    def get_brands(self, category: Optional[str] = None) -> List[str]:
        """Получает список всех брендов"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        if category:
            df = df[df['category_level_1'] == category]
        
        brands = df['brand'].dropna().unique().tolist()
        return sorted([str(b) for b in brands])


# Глобальный экземпляр сервиса
_service_instance: Optional[ProductService] = None


def get_product_service(data_dir: Optional[str] = None) -> ProductService:
    """Получает глобальный экземпляр сервиса товаров (singleton)"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ProductService(data_dir)
    return _service_instance

