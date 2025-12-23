import pytest
from fastapi import status


def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


def test_health_check(client):
    """Тест проверки здоровья API"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    # Если данные загружены, проверяем наличие информации
    if data["status"] == "healthy":
        assert "data_files_loaded" in data
        assert "total_products" in data


def test_get_products_list(client):
    """Тест получения списка товаров"""
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "products" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert isinstance(data["products"], list)


def test_get_products_with_pagination(client):
    """Тест пагинации товаров"""
    response = client.get("/api/products?page=1&page_size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["products"]) <= 10


def test_get_products_with_filters(client):
    """Тест фильтрации товаров"""
    # Тест фильтра по категории
    response = client.get("/api/products?category_level_1=Красота%20и%20здоровье&page_size=5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    if data["products"]:
        # Проверяем, что все товары соответствуют фильтру
        for product in data["products"]:
            assert product["category_level_1"] == "Красота и здоровье"
    
    # Тест фильтра по минимальному количеству добавлений
    response = client.get("/api/products?min_favorites_count=1000&page_size=5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    if data["products"]:
        for product in data["products"]:
            assert product["favorites_count"] >= 1000


def test_get_product_by_id(client, sample_product_id):
    """Тест получения товара по ID"""
    if sample_product_id:
        response = client.get(f"/api/products/{sample_product_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_product_id
        assert "name" in data
        assert "favorites_count" in data
    else:
        pytest.skip("Нет доступных товаров для тестирования")


def test_get_product_by_id_not_found(client):
    """Тест получения несуществующего товара"""
    response = client.get("/api/products/nonexistent_id_12345")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "не найден" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


def test_get_categories(client):
    """Тест получения списка категорий"""
    response = client.get("/api/products/categories/list")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all(isinstance(cat, str) for cat in data)


def test_get_brands(client):
    """Тест получения списка брендов"""
    response = client.get("/api/products/brands/list")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all(isinstance(brand, str) for brand in data)


def test_get_brands_with_category_filter(client):
    """Тест получения брендов с фильтром по категории"""
    # Сначала получаем категории
    categories_response = client.get("/api/products/categories/list")
    if categories_response.status_code == 200:
        categories = categories_response.json()
        if categories:
            category = categories[0]
            response = client.get(f"/api/products/brands/list?category={category}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)


def test_products_invalid_pagination(client):
    """Тест невалидной пагинации"""
    # Отрицательный номер страницы
    response = client.get("/api/products?page=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Нулевой размер страницы
    response = client.get("/api/products?page_size=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



