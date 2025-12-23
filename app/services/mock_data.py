"""
Мок данные для быстрого старта приложения
"""
from datetime import date, timedelta
import random

def generate_mock_products(count: int = 1000):
    """Генерирует мок данные товаров"""
    import pandas as pd
    
    categories = [
        'Красота и здоровье',
        'Электроника',
        'Одежда и обувь',
        'Дом и сад',
        'Спорт и отдых',
        'Книги',
        'Игрушки',
        'Автотовары'
    ]
    
    brands = [
        'OZON', 'Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'LG', 'Xiaomi',
        'Huawei', 'Canon', 'Nikon', 'Bosch', 'Philips', 'Panasonic'
    ]
    
    products = []
    today = date.today()
    
    for i in range(count):
        product_id = f"mock_{i:06d}"
        category = random.choice(categories)
        brand = random.choice(brands)
        
        # Генерируем дни отсутствия: 70% товаров с >= 15 дней для показа метрик
        if i < int(count * 0.7):
            days_out = random.randint(15, 100)
        else:
            days_out = random.randint(0, 14)
        
        # Генерируем спрос: некоторые товары с высоким спросом
        if i < int(count * 0.2):
            favorites = random.randint(10000, 50000)  # Высокий спрос
        elif i < int(count * 0.5):
            favorites = random.randint(5000, 10000)   # Средний спрос
        else:
            favorites = random.randint(100, 5000)    # Низкий спрос
        
        products.append({
            'id': product_id,
            'name': f'Товар {i+1} - {brand} {category}',
            'brand': brand,
            'link': f'https://www.ozon.ru/product/{product_id}',
            'category_level_1': category,
            'category_level_2': None,
            'category_level_3': None,
            'category_level_4': None,
            'favorites_count': favorites,
            'last_in_stock': today - timedelta(days=days_out),
            'period_start': today - timedelta(days=30),
            'period_end': today,
            'days_out_of_stock': days_out
        })
    
    return pd.DataFrame(products)

