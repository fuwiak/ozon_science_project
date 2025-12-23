import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from pathlib import Path

# Устанавливаем путь к данным для тестов
BASE_DIR = Path(__file__).parent.parent
TEST_DATA_DIR = str(BASE_DIR / "data")
os.environ["DATA_DIR"] = TEST_DATA_DIR


@pytest.fixture(scope="module")
def client():
    """Создает тестовый клиент FastAPI"""
    return TestClient(app)


@pytest.fixture(scope="module")
def sample_product_id(client):
    """Получает ID первого товара для тестирования"""
    response = client.get("/api/products?page_size=1")
    if response.status_code == 200:
        data = response.json()
        if data.get("products") and len(data["products"]) > 0:
            return data["products"][0]["id"]
    return None



