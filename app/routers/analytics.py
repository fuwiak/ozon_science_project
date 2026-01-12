from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date
import pandas as pd
import io
from app.models import (
    DemandMetrics, TrendData, TimeSeriesResponse, 
    OutOfStockProduct, PricingMetricsResponse
)
from app.services.analytics_service import get_analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/demand/top", response_model=list[DemandMetrics])
async def get_top_products_by_demand(
    limit: int = Query(10, ge=1, le=1000, description="Количество товаров в топе"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    period_start: Optional[date] = Query(None, description="Начало периода"),
    period_end: Optional[date] = Query(None, description="Конец периода")
):
    """
    Получает топ N товаров по количеству добавлений в избранное
    
    Товары ранжируются по общему количеству добавлений в избранное
    за указанный период с учетом фильтров.
    """
    try:
        service = get_analytics_service()
        top_products = service.get_top_products_by_demand(
            limit=limit,
            category=category,
            brand=brand,
            period_start=period_start,
            period_end=period_end
        )
        return top_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении топ товаров: {str(e)}")


@router.get("/demand/trends", response_model=list[TrendData])
async def get_demand_trends(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    group_by: str = Query("category", pattern="^(category|brand|period)$", description="Группировка: category, brand или period")
):
    """
    Анализирует тренды спроса
    
    Возвращает динамику добавлений в избранное с группировкой по:
    - категориям
    - брендам
    - периодам
    """
    try:
        service = get_analytics_service()
        trends = service.get_demand_trends(
            category=category,
            brand=brand,
            group_by=group_by
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении трендов: {str(e)}")


@router.get("/stock/out-of-stock", response_model=list[OutOfStockProduct])
async def get_out_of_stock_products(
    min_days: int = Query(15, ge=0, description="Минимальное количество дней отсутствия в наличии"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    period_start: Optional[date] = Query(None, description="Начало периода"),
    period_end: Optional[date] = Query(None, description="Конец периода"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество товаров для возврата")
):
    """
    Получает товары, отсутствующие в наличии более указанного количества дней
    
    Товары отсортированы по приоритетности (на основе спроса и длительности отсутствия).
    """
    try:
        service = get_analytics_service()
        products = service.get_out_of_stock_with_priority(
            min_days=min_days,
            category=category,
            brand=brand,
            limit=limit
        )
        
        # Дополнительная фильтрация по периоду (если нужно)
        if period_start or period_end:
            # Фильтруем через product_service для доступа к period_start/period_end
            from app.services.product_service import get_product_service
            product_service = get_product_service()
            filtered_products = product_service.get_out_of_stock_products(
                min_days=min_days,
                category=category,
                brand=brand,
                period_start=period_start,
                period_end=period_end
            )
            # Конвертируем в OutOfStockProduct
            result = []
            for p in filtered_products:
                if p.days_out_of_stock and p.days_out_of_stock >= min_days:
                    # Рассчитываем приоритетность
                    priority = min(100, (p.favorites_count / 1000 * 70) + (p.days_out_of_stock / 100 * 30))
                    result.append(OutOfStockProduct(
                        product_id=p.id,
                        product_name=p.name,
                        brand=p.brand,
                        category_level_1=p.category_level_1,
                        last_in_stock=p.last_in_stock or date.today(),
                        days_out_of_stock=p.days_out_of_stock,
                        favorites_count=p.favorites_count,
                        priority_score=priority
                    ))
            sorted_result = sorted(result, key=lambda x: x.priority_score, reverse=True)
            return sorted_result[:limit]
        
        return products[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении товаров без остатков: {str(e)}")


@router.get("/timeseries", response_model=TimeSeriesResponse)
async def get_time_series(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    group_by: Optional[str] = Query(None, pattern="^(category|brand)$", description="Группировка: category или brand"),
    period: str = Query("month", pattern="^(day|week|month)$", description="Период агрегации: day, week или month")
):
    """
    Получает временной ряд добавлений в избранное
    
    Возвращает данные, сгруппированные по выбранному периоду (день/неделя/месяц)
    с опциональной группировкой по категориям или брендам.
    """
    try:
        service = get_analytics_service()
        time_series = service.get_time_series(
            category=category,
            brand=brand,
            group_by=group_by,
            period=period
        )
        return TimeSeriesResponse(
            data=time_series,
            group_by=group_by
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении временного ряда: {str(e)}")


@router.get("/pricing-metrics", response_model=PricingMetricsResponse)
async def get_pricing_metrics(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    min_days_out_of_stock: int = Query(15, ge=0, description="Минимальное количество дней отсутствия в наличии"),
    limit: int = Query(50, ge=1, le=500, description="Максимальное количество метрик для возврата (для оптимизации памяти)")
):
    """
    Получает комплексные метрики для динамического ценообразования
    
    Включает:
    - Уровень спроса (high/medium/low)
    - Количество дней отсутствия в наличии
    - Приоритетность товара для пополнения (0-100)
    - Рекомендации по действиям
    
    Lazy evaluation: возвращает только top N метрик по приоритетности для оптимизации памяти.
    """
    try:
        service = get_analytics_service()
        metrics = service.get_pricing_metrics(
            category=category,
            brand=brand,
            min_days_out_of_stock=min_days_out_of_stock,
            limit=limit
        )
        return PricingMetricsResponse(
            metrics=metrics,
            total=len(metrics)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении метрик ценообразования: {str(e)}")


@router.get("/export/demand/top")
async def export_top_products_by_demand(
    format: str = Query("csv", pattern="^(csv|excel)$", description="Формат экспорта: csv или excel"),
    limit: int = Query(1000, ge=1, le=10000, description="Количество товаров"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    period_start: Optional[date] = Query(None, description="Начало периода"),
    period_end: Optional[date] = Query(None, description="Конец периода")
):
    """
    Экспортирует топ товаров по спросу в CSV или Excel
    """
    try:
        service = get_analytics_service()
        top_products = service.get_top_products_by_demand(
            limit=limit,
            category=category,
            brand=brand,
            period_start=period_start,
            period_end=period_end
        )
        
        # Конвертируем в DataFrame
        df = pd.DataFrame([p.dict() for p in top_products])
        
        if format == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=top_products_{date.today()}.xlsx"}
            )
        else:  # csv
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=top_products_{date.today()}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")


@router.get("/export/demand/trends")
async def export_demand_trends(
    format: str = Query("csv", pattern="^(csv|excel)$", description="Формат экспорта: csv или excel"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    group_by: str = Query("category", pattern="^(category|brand|period)$", description="Группировка")
):
    """
    Экспортирует тренды спроса в CSV или Excel
    """
    try:
        service = get_analytics_service()
        trends = service.get_demand_trends(
            category=category,
            brand=brand,
            group_by=group_by
        )
        
        df = pd.DataFrame([t.dict() for t in trends])
        
        if format == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=demand_trends_{date.today()}.xlsx"}
            )
        else:
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=demand_trends_{date.today()}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")


@router.get("/export/timeseries")
async def export_time_series(
    format: str = Query("csv", pattern="^(csv|excel)$", description="Формат экспорта: csv или excel"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    group_by: Optional[str] = Query(None, pattern="^(category|brand)$", description="Группировка"),
    period: str = Query("month", pattern="^(day|week|month)$", description="Период агрегации")
):
    """
    Экспортирует временной ряд в CSV или Excel
    """
    try:
        service = get_analytics_service()
        time_series = service.get_time_series(
            category=category,
            brand=brand,
            group_by=group_by,
            period=period
        )
        
        df = pd.DataFrame([ts.dict() for ts in time_series])
        
        if format == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=timeseries_{date.today()}.xlsx"}
            )
        else:
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=timeseries_{date.today()}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")


@router.get("/export/out-of-stock")
async def export_out_of_stock(
    format: str = Query("csv", pattern="^(csv|excel)$", description="Формат экспорта: csv или excel"),
    min_days: int = Query(15, ge=0, description="Минимальное количество дней отсутствия"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду")
):
    """
    Экспортирует товары без остатков в CSV или Excel
    """
    try:
        service = get_analytics_service()
        products = service.get_out_of_stock_with_priority(
            min_days=min_days,
            category=category,
            brand=brand
        )
        
        df = pd.DataFrame([p.dict() for p in products])
        
        if format == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=out_of_stock_{date.today()}.xlsx"}
            )
        else:
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=out_of_stock_{date.today()}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")


@router.get("/export/pricing-metrics")
async def export_pricing_metrics(
    format: str = Query("csv", pattern="^(csv|excel)$", description="Формат экспорта: csv или excel"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду"),
    min_days_out_of_stock: int = Query(15, ge=0, description="Минимальное количество дней отсутствия"),
    limit: int = Query(500, ge=1, le=5000, description="Максимальное количество метрик")
):
    """
    Экспортирует метрики ценообразования в CSV или Excel
    """
    try:
        service = get_analytics_service()
        metrics = service.get_pricing_metrics(
            category=category,
            brand=brand,
            min_days_out_of_stock=min_days_out_of_stock,
            limit=limit
        )
        
        df = pd.DataFrame([m.dict() for m in metrics])
        
        if format == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=pricing_metrics_{date.today()}.xlsx"}
            )
        else:
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=pricing_metrics_{date.today()}.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")

