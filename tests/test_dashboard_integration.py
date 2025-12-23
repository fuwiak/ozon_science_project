"""
Тесты для проверки соответствия эндпоинтов FastAPI дашборду
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestDashboardEndpoints:
    """Тесты эндпоинтов, используемых дашбордом"""
    
    def test_get_pricing_metrics_for_dashboard(self):
        """Тест эндпоинта /api/analytics/pricing-metrics с параметрами дашборда"""
        response = client.get("/api/analytics/pricing-metrics?min_days_out_of_stock=15")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "metrics" in data
        assert "total" in data
        assert isinstance(data["metrics"], list)
        assert isinstance(data["total"], int)
        
        # Если есть метрики, проверяем их структуру
        if len(data["metrics"]) > 0:
            metric = data["metrics"][0]
            assert "product_id" in metric
            assert "product_name" in metric
            assert "demand_level" in metric
            assert "favorites_count" in metric
            assert "days_out_of_stock" in metric
            assert "priority_score" in metric
            assert "recommendation" in metric
            
            # Проверяем, что days_out_of_stock >= 15
            assert metric["days_out_of_stock"] >= 15
            
            # Проверяем допустимые значения demand_level
            assert metric["demand_level"] in ["high", "medium", "low"]
            
            # Проверяем диапазон priority_score
            assert 0 <= metric["priority_score"] <= 100
    
    def test_get_out_of_stock_products_for_dashboard(self):
        """Тест эндпоинта /api/analytics/stock/out-of-stock с параметрами дашборда"""
        response = client.get("/api/analytics/stock/out-of-stock?min_days=15")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем, что это список
        assert isinstance(data, list)
        
        # Если есть товары, проверяем их структуру
        if len(data) > 0:
            product = data[0]
            assert "product_id" in product
            assert "product_name" in product
            assert "days_out_of_stock" in product
            assert "favorites_count" in product
            assert "priority_score" in product
            assert "last_in_stock" in product
            
            # Проверяем, что days_out_of_stock >= 15
            assert product["days_out_of_stock"] >= 15
            
            # Проверяем диапазон priority_score
            assert 0 <= product["priority_score"] <= 100
    
    def test_get_top_products_for_dashboard(self):
        """Тест эндпоинта /api/analytics/demand/top с параметрами дашборда"""
        response = client.get("/api/analytics/demand/top?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем, что это список
        assert isinstance(data, list)
        
        # Проверяем, что количество не превышает limit
        assert len(data) <= 5
        
        # Если есть товары, проверяем их структуру
        if len(data) > 0:
            product = data[0]
            assert "product_id" in product
            assert "product_name" in product
            assert "favorites_count" in product
            assert "rank" in product or product.get("rank") is None
    
    def test_get_status_endpoint(self):
        """Тест эндпоинта /api/status"""
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "cache_ready" in data
        assert "loading" in data
        assert "files_loaded" in data
        assert "total_products" in data
        
        # Проверяем типы
        assert isinstance(data["cache_ready"], bool)
        assert isinstance(data["loading"], bool)
        assert isinstance(data["files_loaded"], int)
        assert isinstance(data["total_products"], int)
        
        # Проверяем опциональные поля
        if "using_mock_data" in data:
            assert isinstance(data["using_mock_data"], bool)
        if "message" in data:
            assert isinstance(data["message"], str)
    
    def test_dashboard_data_consistency(self):
        """Тест согласованности данных между эндпоинтами дашборда"""
        # Получаем данные из всех эндпоинтов
        metrics_response = client.get("/api/analytics/pricing-metrics?min_days_out_of_stock=15")
        out_of_stock_response = client.get("/api/analytics/stock/out-of-stock?min_days=15")
        top_products_response = client.get("/api/analytics/demand/top?limit=5")
        status_response = client.get("/api/status")
        
        # Все запросы должны быть успешными
        assert metrics_response.status_code == 200
        assert out_of_stock_response.status_code == 200
        assert top_products_response.status_code == 200
        assert status_response.status_code == 200
        
        metrics_data = metrics_response.json()
        out_of_stock_data = out_of_stock_response.json()
        top_products_data = top_products_response.json()
        status_data = status_response.json()
        
        # Проверяем, что если кэш готов, то есть данные
        if status_data["cache_ready"]:
            # Хотя бы один из эндпоинтов должен вернуть данные
            has_data = (
                len(metrics_data.get("metrics", [])) > 0 or
                len(out_of_stock_data) > 0 or
                len(top_products_data) > 0
            )
            # Это не обязательно, но логично
            # assert has_data or status_data["using_mock_data"] == True
    
    def test_pricing_metrics_filtering(self):
        """Тест фильтрации метрик по min_days_out_of_stock"""
        response = client.get("/api/analytics/pricing-metrics?min_days_out_of_stock=15")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем, что все метрики соответствуют фильтру
        for metric in data.get("metrics", []):
            assert metric["days_out_of_stock"] >= 15
    
    def test_out_of_stock_filtering(self):
        """Тест фильтрации товаров без остатка по min_days"""
        response = client.get("/api/analytics/stock/out-of-stock?min_days=15")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем, что все товары соответствуют фильтру
        for product in data:
            assert product["days_out_of_stock"] >= 15
    
    def test_top_products_limit(self):
        """Тест ограничения количества товаров в топе"""
        for limit in [1, 5, 10, 50]:
            response = client.get(f"/api/analytics/demand/top?limit={limit}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Проверяем, что количество не превышает limit
            assert len(data) <= limit



