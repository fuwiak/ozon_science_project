import pandas as pd
from typing import List, Optional
import os
from pathlib import Path
from datetime import date, timedelta
from app.services.excel_loader import get_loader
from app.models import (
    DemandMetrics, TrendData, TimeSeriesPoint, 
    OutOfStockProduct, PricingMetric
)


class AnalyticsService:
    """Сервис для аналитики и метрик"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.getenv("DATA_DIR", "data")
            if not os.path.isabs(data_dir):
                base_dir = Path(__file__).parent.parent.parent
                data_dir = str(base_dir / data_dir)
        self.loader = get_loader(data_dir)
    
    def get_top_products_by_demand(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> List[DemandMetrics]:
        """Получает топ товаров по количеству добавлений в избранное"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Фильтры
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        if period_start:
            df = df[df['period_start'] >= period_start]
        if period_end:
            df = df[df['period_end'] <= period_end]
        
        # Группируем по товару (ID) и суммируем добавления в избранное
        grouped = df.groupby('id').agg({
            'name': 'first',
            'brand': 'first',
            'category_level_1': 'first',
            'favorites_count': 'sum',
            'period_start': 'min',
            'period_end': 'max'
        }).reset_index()
        
        # Сортируем по количеству добавлений
        grouped = grouped.sort_values('favorites_count', ascending=False)
        
        # Берем топ N
        top_products = grouped.head(limit)
        
        # Конвертируем в модели
        result = []
        for idx, (_, row) in enumerate(top_products.iterrows(), 1):
            result.append(DemandMetrics(
                product_id=str(row['id']),
                product_name=str(row['name']),
                brand=str(row['brand']) if pd.notna(row['brand']) else None,
                category_level_1=str(row['category_level_1']) if pd.notna(row['category_level_1']) else None,
                favorites_count=int(row['favorites_count']),
                period_start=row['period_start'] if pd.notna(row['period_start']) else None,
                period_end=row['period_end'] if pd.notna(row['period_end']) else None,
                rank=idx
            ))
        
        return result
    
    def get_demand_trends(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        group_by: str = "category"
    ) -> List[TrendData]:
        """Анализирует тренды спроса"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Фильтры
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        
        # Группировка
        if group_by == "category":
            group_col = 'category_level_1'
        elif group_by == "brand":
            group_col = 'brand'
        else:
            group_col = 'period_start'
        
        # Группируем по периоду и выбранному полю
        df['period_str'] = df['period_start'].apply(
            lambda x: x.strftime('%Y-%m') if pd.notna(x) else 'Unknown'
        )
        
        grouped = df.groupby([group_col, 'period_str']).agg({
            'favorites_count': ['sum', 'count'],
            'id': 'nunique'
        }).reset_index()
        
        grouped.columns = [group_col, 'period', 'total_favorites', 'count', 'unique_products']
        grouped['avg_favorites_per_product'] = grouped['total_favorites'] / grouped['unique_products']
        
        # Конвертируем в модели
        result = []
        for _, row in grouped.iterrows():
            result.append(TrendData(
                period=str(row['period']),
                category=str(row[group_col]) if group_by == "category" and pd.notna(row[group_col]) else None,
                brand=str(row[group_col]) if group_by == "brand" and pd.notna(row[group_col]) else None,
                total_favorites=int(row['total_favorites']),
                unique_products=int(row['unique_products']),
                avg_favorites_per_product=float(row['avg_favorites_per_product'])
            ))
        
        return sorted(result, key=lambda x: x.period)
    
    def get_time_series(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        group_by: Optional[str] = None,
        period: str = "month"
    ) -> List[TimeSeriesPoint]:
        """Получает временной ряд добавлений в избранное"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Фильтры
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        
        # Форматируем дату в зависимости от периода
        if period == "day":
            df['date_str'] = df['period_start'].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None
            )
        elif period == "week":
            df['date_str'] = df['period_start'].apply(
                lambda x: (x - timedelta(days=x.weekday())).strftime('%Y-W%W') if pd.notna(x) else None
            )
        else:  # month
            df['date_str'] = df['period_start'].apply(
                lambda x: x.strftime('%Y-%m') if pd.notna(x) else None
            )
        
        # Группировка
        if group_by == "category":
            group_col = 'category_level_1'
        elif group_by == "brand":
            group_col = 'brand'
        else:
            group_col = None
        
        if group_col:
            grouped = df.groupby([group_col, 'date_str']).agg({
                'favorites_count': 'sum'
            }).reset_index()
            
            result = []
            for _, row in grouped.iterrows():
                if pd.notna(row['date_str']):
                    # Парсим дату обратно
                    if period == "day":
                        date_val = pd.to_datetime(row['date_str']).date()
                    elif period == "week":
                        # Упрощенная обработка недели
                        date_val = pd.to_datetime(row['date_str'].split('-W')[0] + '-01-01').date()
                    else:
                        date_val = pd.to_datetime(row['date_str'] + '-01').date()
                    
                    result.append(TimeSeriesPoint(
                        date=date_val,
                        value=int(row['favorites_count']),
                        category=str(row[group_col]) if group_by == "category" and pd.notna(row[group_col]) else None,
                        brand=str(row[group_col]) if group_by == "brand" and pd.notna(row[group_col]) else None
                    ))
        else:
            grouped = df.groupby('date_str').agg({
                'favorites_count': 'sum'
            }).reset_index()
            
            result = []
            for _, row in grouped.iterrows():
                if pd.notna(row['date_str']):
                    if period == "day":
                        date_val = pd.to_datetime(row['date_str']).date()
                    elif period == "week":
                        date_val = pd.to_datetime(row['date_str'].split('-W')[0] + '-01-01').date()
                    else:
                        date_val = pd.to_datetime(row['date_str'] + '-01').date()
                    
                    result.append(TimeSeriesPoint(
                        date=date_val,
                        value=int(row['favorites_count'])
                    ))
        
        return sorted(result, key=lambda x: x.date)
    
    def get_out_of_stock_with_priority(
        self,
        min_days: int = 15,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 100
    ) -> List[OutOfStockProduct]:
        """Получает товары, отсутствующие в наличии, с расчетом приоритетности (lazy evaluation)"""
        # Используем кэш если доступен
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Lazy evaluation: сначала фильтруем по дням отсутствия (быстрая операция)
        df = df[df['days_out_of_stock'] >= min_days]
        
        # Дополнительные фильтры (lazy evaluation)
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        
        # Lazy evaluation: если данных слишком много, сначала ограничиваем по favorites_count
        # Это экономит память при группировке
        if len(df) > limit * 3:
            # Берем топ товаров по favorites_count для быстрой предварительной фильтрации
            df = df.nlargest(limit * 3, 'favorites_count')
        
        # Группируем по товару и агрегируем данные
        grouped = df.groupby('id').agg({
            'name': 'first',
            'brand': 'first',
            'category_level_1': 'first',
            'last_in_stock': 'min',
            'days_out_of_stock': 'max',
            'favorites_count': 'sum'
        }).reset_index()
        
        # Рассчитываем приоритетность (0-100)
        # Приоритет = (спрос * 0.7) + (дни отсутствия * 0.3)
        max_favorites = grouped['favorites_count'].max() if len(grouped) > 0 else 1
        max_days = grouped['days_out_of_stock'].max() if len(grouped) > 0 else 1
        
        grouped['priority_score'] = (
            (grouped['favorites_count'] / max_favorites * 70) +
            (grouped['days_out_of_stock'] / max_days * 30)
        ).clip(0, 100)
        
        # Сортируем по приоритетности и ограничиваем результат (lazy evaluation)
        grouped = grouped.sort_values('priority_score', ascending=False).head(limit)
        
        # Конвертируем в модели (lazy evaluation - только top N)
        result = []
        for _, row in grouped.iterrows():
            result.append(OutOfStockProduct(
                product_id=str(row['id']),
                product_name=str(row['name']),
                brand=str(row['brand']) if pd.notna(row['brand']) else None,
                category_level_1=str(row['category_level_1']) if pd.notna(row['category_level_1']) else None,
                last_in_stock=row['last_in_stock'] if pd.notna(row['last_in_stock']) else date.today(),
                days_out_of_stock=int(row['days_out_of_stock']),
                favorites_count=int(row['favorites_count']),
                priority_score=float(row['priority_score'])
            ))
        
        return result
    
    def get_pricing_metrics(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_days_out_of_stock: int = 15,
        limit: int = 50
    ) -> List[PricingMetric]:
        """
        Получает комплексные метрики для динамического ценообразования
        
        Lazy evaluation: обрабатывает данные по требованию и возвращает только top N метрик
        для оптимизации памяти и производительности.
        """
        # Используем кэш если доступен (lazy evaluation)
        if self.loader._cache is not None:
            df = self.loader._cache
        else:
            df = self.loader.load_all_data()
        
        # Фильтры (lazy evaluation - применяются до полной обработки)
        if category:
            df = df[df['category_level_1'] == category]
        if brand:
            df = df[df['brand'] == brand]
        
        # Lazy evaluation: группируем только необходимые колонки
        grouped = df.groupby('id').agg({
            'name': 'first',
            'brand': 'first',
            'category_level_1': 'first',
            'favorites_count': 'sum',
            'days_out_of_stock': 'max'
        }).reset_index()
        
        # Фильтруем по минимальному количеству дней отсутствия
        grouped = grouped[grouped['days_out_of_stock'] >= min_days_out_of_stock]
        
        # Lazy evaluation: если данных слишком много, сначала сортируем и ограничиваем
        # Это экономит память при расчете квантилей
        if len(grouped) > limit * 2:
            # Быстрая предварительная сортировка по favorites_count для экономии памяти
            grouped = grouped.nlargest(limit * 2, 'favorites_count')
        
        # Определяем уровень спроса (lazy evaluation - только для отфильтрованных данных)
        if len(grouped) > 0:
            q75 = grouped['favorites_count'].quantile(0.75)
            q25 = grouped['favorites_count'].quantile(0.25)
            
            def get_demand_level(count):
                if count >= q75:
                    return "high"
                elif count >= q25:
                    return "medium"
                else:
                    return "low"
            
            grouped['demand_level'] = grouped['favorites_count'].apply(get_demand_level)
        else:
            grouped['demand_level'] = "low"
        
        # Рассчитываем приоритетность (lazy evaluation)
        max_favorites = grouped['favorites_count'].max() if len(grouped) > 0 else 1
        max_days = grouped['days_out_of_stock'].max() if len(grouped) > 0 else 1
        
        grouped['priority_score'] = (
            (grouped['favorites_count'] / max_favorites * 70) +
            (grouped['days_out_of_stock'] / max_days * 30)
        ).clip(0, 100)
        
        # Генерируем рекомендации (lazy evaluation)
        def get_recommendation(row):
            if row['demand_level'] == "high" and row['days_out_of_stock'] > 30:
                return "Критично: высокий спрос, товар отсутствует более месяца. Срочное пополнение."
            elif row['demand_level'] == "high":
                return "Высокий приоритет: высокий спрос, рекомендуется пополнить в ближайшее время."
            elif row['days_out_of_stock'] > 60:
                return "Средний приоритет: товар отсутствует длительное время, рассмотреть пополнение."
            else:
                return "Низкий приоритет: мониторинг ситуации."
        
        grouped['recommendation'] = grouped.apply(get_recommendation, axis=1)
        
        # Сортируем по приоритетности и ограничиваем результат (lazy evaluation)
        grouped = grouped.sort_values('priority_score', ascending=False).head(limit)
        
        # Конвертируем в модели (lazy evaluation - только top N)
        result = []
        for _, row in grouped.iterrows():
            result.append(PricingMetric(
                product_id=str(row['id']),
                product_name=str(row['name']),
                brand=str(row['brand']) if pd.notna(row['brand']) else None,
                category_level_1=str(row['category_level_1']) if pd.notna(row['category_level_1']) else None,
                demand_level=str(row['demand_level']),
                favorites_count=int(row['favorites_count']),
                days_out_of_stock=int(row['days_out_of_stock']),
                priority_score=float(row['priority_score']),
                recommendation=str(row['recommendation'])
            ))
        
        return result


# Глобальный экземпляр сервиса
_service_instance: Optional[AnalyticsService] = None


def get_analytics_service(data_dir: Optional[str] = None) -> AnalyticsService:
    """Получает глобальный экземпляр сервиса аналитики (singleton)"""
    global _service_instance
    if _service_instance is None:
        _service_instance = AnalyticsService(data_dir)
    return _service_instance

