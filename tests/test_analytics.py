import pytest
from fastapi import status


def test_get_top_products_by_demand(client):
    """Тест получения топ товаров по спросу"""
    response = client.get("/api/analytics/demand/top?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert len(data) <= 10
        # Проверяем структуру первого элемента
        product = data[0]
        assert "product_id" in product
        assert "product_name" in product
        assert "favorites_count" in product
        assert "rank" in product
        # Проверяем, что товары отсортированы по убыванию
        if len(data) > 1:
            assert data[0]["favorites_count"] >= data[1]["favorites_count"]


def test_get_top_products_with_filters(client):
    """Тест топ товаров с фильтрами"""
    response = client.get("/api/analytics/demand/top?limit=5&category=Красота%20и%20здоровье")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        for product in data:
            if product.get("category_level_1"):
                assert product["category_level_1"] == "Красота и здоровье"


def test_get_demand_trends(client):
    """Тест получения трендов спроса"""
    response = client.get("/api/analytics/demand/trends?group_by=category")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        trend = data[0]
        assert "period" in trend
        assert "total_favorites" in trend
        assert "unique_products" in trend
        assert "avg_favorites_per_product" in trend


def test_get_demand_trends_by_brand(client):
    """Тест трендов по брендам"""
    response = client.get("/api/analytics/demand/trends?group_by=brand")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_out_of_stock_products(client):
    """Тест получения товаров без остатков"""
    response = client.get("/api/analytics/stock/out-of-stock?min_days=15")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        product = data[0]
        assert "product_id" in product
        assert "product_name" in product
        assert "days_out_of_stock" in product
        assert "priority_score" in product
        # Проверяем, что все товары отсутствуют более указанного количества дней
        for p in data:
            assert p["days_out_of_stock"] >= 15


def test_get_out_of_stock_with_filters(client):
    """Тест товаров без остатков с фильтрами"""
    response = client.get("/api/analytics/stock/out-of-stock?min_days=30&category=Красота%20и%20здоровье")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_time_series(client):
    """Тест получения временного ряда"""
    response = client.get("/api/analytics/timeseries?period=month")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    if data["data"]:
        point = data["data"][0]
        assert "date" in point
        assert "value" in point


def test_get_time_series_by_category(client):
    """Тест временного ряда с группировкой по категориям"""
    response = client.get("/api/analytics/timeseries?period=month&group_by=category")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert data["group_by"] == "category"


def test_get_time_series_different_periods(client):
    """Тест временного ряда с разными периодами"""
    for period in ["day", "week", "month"]:
        response = client.get(f"/api/analytics/timeseries?period={period}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data


def test_get_pricing_metrics(client):
    """Тест получения метрик ценообразования"""
    response = client.get("/api/analytics/pricing-metrics?min_days_out_of_stock=15")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert isinstance(data["metrics"], list)
    if data["metrics"]:
        metric = data["metrics"][0]
        assert "product_id" in metric
        assert "product_name" in metric
        assert "demand_level" in metric
        assert "favorites_count" in metric
        assert "days_out_of_stock" in metric
        assert "priority_score" in metric
        assert "recommendation" in metric
        # Проверяем валидность уровня спроса
        assert metric["demand_level"] in ["high", "medium", "low"]
        # Проверяем диапазон приоритетности
        assert 0 <= metric["priority_score"] <= 100


def test_get_pricing_metrics_with_filters(client):
    """Тест метрик ценообразования с фильтрами"""
    response = client.get("/api/analytics/pricing-metrics?category=Красота%20и%20здоровье&min_days_out_of_stock=20")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "metrics" in data
    assert isinstance(data["metrics"], list)


def test_analytics_invalid_parameters(client):
    """Тест невалидных параметров аналитики"""
    # Невалидный limit
    response = client.get("/api/analytics/demand/top?limit=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Невалидный group_by
    response = client.get("/api/analytics/demand/trends?group_by=invalid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Невалидный period
    response = client.get("/api/analytics/timeseries?period=invalid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



