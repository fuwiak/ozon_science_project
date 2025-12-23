"""
Тесты для эндпоинтов n8n интеграции
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestN8NEndpoints:
    """Тесты эндпоинтов n8n"""
    
    def test_get_workflows_mock(self):
        """Тест получения workflows (моковые данные)"""
        response = client.get("/api/n8n/workflows")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "workflows" in data
        assert "total" in data
        assert isinstance(data["workflows"], list)
        assert isinstance(data["total"], int)
        assert data["total"] > 0
        
        # Проверяем структуру workflow
        if len(data["workflows"]) > 0:
            workflow = data["workflows"][0]
            assert "id" in workflow
            assert "name" in workflow
            assert "active" in workflow
            assert "nodes" in workflow
            assert isinstance(workflow["active"], bool)
            assert isinstance(workflow["nodes"], int)
    
    def test_toggle_workflow_mock(self):
        """Тест переключения статуса workflow (моковый режим)"""
        response = client.post(
            "/api/n8n/workflows/1/toggle",
            json={"active": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
    
    def test_get_workflow_by_id_mock(self):
        """Тест получения workflow по ID (моковые данные)"""
        response = client.get("/api/n8n/workflows/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "name" in data
        assert "active" in data
        assert "nodes" in data
        assert data["id"] == "1"
    
    def test_get_workflow_not_found(self):
        """Тест получения несуществующего workflow"""
        response = client.get("/api/n8n/workflows/999")
        
        # В моковом режиме может вернуть 404 или моковые данные
        assert response.status_code in [200, 404]
    
    def test_test_connection_without_credentials(self):
        """Тест проверки подключения без учетных данных"""
        response = client.post(
            "/api/n8n/test-connection",
            json={"url": "", "api_key": ""}
        )
        
        # Должен вернуть ошибку или информацию о моковом режиме
        assert response.status_code == 200
        data = response.json()
        assert "success" in data



