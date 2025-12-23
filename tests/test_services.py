import pytest
import os
from pathlib import Path
from app.services.excel_loader import ExcelLoader
from app.services.product_service import ProductService
from app.services.analytics_service import AnalyticsService
from app.models import ProductFilter


# Устанавливаем путь к данным
BASE_DIR = Path(__file__).parent.parent
TEST_DATA_DIR = str(BASE_DIR / "data")
os.environ["DATA_DIR"] = TEST_DATA_DIR


@pytest.fixture(scope="module")
def loader():
    """Создает экземпляр загрузчика Excel"""
    return ExcelLoader(TEST_DATA_DIR)


@pytest.fixture(scope="module")
def product_service():
    """Создает экземпляр сервиса товаров"""
    return ProductService(TEST_DATA_DIR)


@pytest.fixture(scope="module")
def analytics_service():
    """Создает экземпляр сервиса аналитики"""
    return AnalyticsService(TEST_DATA_DIR)


def test_excel_loader_load_data(loader):
    """Тест загрузки данных из Excel"""
    df = loader.load_all_data()
    assert df is not None
    assert len(df) > 0
    # Проверяем наличие необходимых колонок
    required_cols = ['id', 'name', 'favorites_count']
    for col in required_cols:
        assert col in df.columns


def test_excel_loader_caching(loader):
    """Тест кэширования данных"""
    # Первая загрузка
    df1 = loader.load_all_data()
    # Вторая загрузка должна использовать кэш
    df2 = loader.load_all_data()
    assert len(df1) == len(df2)
    # Проверяем, что это тот же объект (кэш работает)
    assert df1 is df2


def test_excel_loader_file_metadata(loader):
    """Тест получения метаданных файлов"""
    loader.load_all_data()
    metadata = loader.get_file_metadata()
    assert isinstance(metadata, dict)
    assert len(metadata) > 0


def test_product_service_search_products(product_service):
    """Тест поиска товаров"""
    filters = ProductFilter()
    products, total = product_service.search_products(filters, page=1, page_size=10)
    assert isinstance(products, list)
    assert total >= 0
    assert len(products) <= 10


def test_product_service_search_with_filters(product_service):
    """Тест поиска товаров с фильтрами"""
    filters = ProductFilter(min_favorites_count=1000)
    products, total = product_service.search_products(filters)
    assert total >= 0
    if products:
        for product in products:
            assert product.favorites_count >= 1000


def test_product_service_get_categories(product_service):
    """Тест получения категорий"""
    categories = product_service.get_categories()
    assert isinstance(categories, list)
    if categories:
        assert all(isinstance(cat, str) for cat in categories)


def test_product_service_get_brands(product_service):
    """Тест получения брендов"""
    brands = product_service.get_brands()
    assert isinstance(brands, list)
    if brands:
        assert all(isinstance(brand, str) for brand in brands)


def test_product_service_get_out_of_stock(product_service):
    """Тест получения товаров без остатков"""
    products = product_service.get_out_of_stock_products(min_days=15)
    assert isinstance(products, list)
    if products:
        for product in products:
            assert product.days_out_of_stock is None or product.days_out_of_stock >= 15


def test_analytics_service_top_products(analytics_service):
    """Тест получения топ товаров"""
    top_products = analytics_service.get_top_products_by_demand(limit=10)
    assert isinstance(top_products, list)
    assert len(top_products) <= 10
    if len(top_products) > 1:
        # Проверяем сортировку
        assert top_products[0].favorites_count >= top_products[1].favorites_count


def test_analytics_service_trends(analytics_service):
    """Тест получения трендов"""
    trends = analytics_service.get_demand_trends(group_by="category")
    assert isinstance(trends, list)
    if trends:
        trend = trends[0]
        assert hasattr(trend, 'period')
        assert hasattr(trend, 'total_favorites')


def test_analytics_service_time_series(analytics_service):
    """Тест получения временного ряда"""
    time_series = analytics_service.get_time_series(period="month")
    assert isinstance(time_series, list)
    if time_series:
        point = time_series[0]
        assert hasattr(point, 'date')
        assert hasattr(point, 'value')


def test_analytics_service_pricing_metrics(analytics_service):
    """Тест получения метрик ценообразования"""
    metrics = analytics_service.get_pricing_metrics(min_days_out_of_stock=15)
    assert isinstance(metrics, list)
    if metrics:
        metric = metrics[0]
        assert hasattr(metric, 'demand_level')
        assert hasattr(metric, 'priority_score')
        assert hasattr(metric, 'recommendation')
        assert metric.demand_level in ["high", "medium", "low"]
        assert 0 <= metric.priority_score <= 100


def test_analytics_service_out_of_stock_priority(analytics_service):
    """Тест получения товаров без остатков с приоритетностью"""
    products = analytics_service.get_out_of_stock_with_priority(min_days=15)
    assert isinstance(products, list)
    if products:
        product = products[0]
        assert hasattr(product, 'priority_score')
        assert hasattr(product, 'days_out_of_stock')
        assert 0 <= product.priority_score <= 100



