import pandas as pd
import os
import re
import hashlib
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dateutil import parser as date_parser
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from app.services.mock_data import generate_mock_products
from app.services.sqlite_cache import SQLiteCache


class ExcelLoader:
    """Сервис для загрузки и нормализации данных из Excel файлов"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._cache: Optional[pd.DataFrame] = None
        self._file_metadata: Dict[str, Dict] = {}
        self._loading = False
        self._load_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._using_mock_data = False
        self._data_ready = False
        # Инициализируем SQLite кэш
        cache_dir = os.getenv("CACHE_DIR", "cache")
        if not os.path.isabs(cache_dir):
            base_dir = Path(__file__).parent.parent.parent
            cache_dir = str(base_dir / cache_dir)
        self._sqlite_cache = SQLiteCache(cache_dir)
    
    def _parse_filename_dates(self, filename: str) -> Tuple[Optional[date], Optional[date]]:
        """Парсит даты из названия файла"""
        period_start = None
        period_end = None
        
        # Паттерны для разных форматов названий файлов
        patterns = [
            # Формат: chto-dobavlyaut-v-izbrannoe_-06_03_2021-04_04_2021.xlsx
            (r'(\d{2})_(\d{2})_(\d{4})-(\d{2})_(\d{2})_(\d{4})', 
             lambda m: (date(int(m.group(3)), int(m.group(2)), int(m.group(1))),
                       date(int(m.group(6)), int(m.group(5)), int(m.group(4))))),
            # Формат: chto-dobavlyali-v-izbrannoe-v-dekabre-2020.xlsx
            (r'dekabre-(\d{4})', lambda m: (date(int(m.group(1)), 12, 1), date(int(m.group(1)), 12, 31))),
            (r'noyabre-(\d{4})', lambda m: (date(int(m.group(1)), 11, 1), date(int(m.group(1)), 11, 30))),
            (r'yanvare-(\d{4})', lambda m: (date(int(m.group(1)), 1, 1), date(int(m.group(1)), 1, 31))),
            # Формат: 2021-07-12_opendata_datasetfavorites_2021-06-12_2021-07-11.xlsx
            (r'(\d{4}-\d{2}-\d{2})_opendata.*?(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})',
             lambda m: (date_parser.parse(m.group(2)).date(), date_parser.parse(m.group(3)).date())),
        ]
        
        for pattern, func in patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    period_start, period_end = func(match)
                    return period_start, period_end
                except:
                    continue
        
        return None, None
    
    def _normalize_columns(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Нормализует названия колонок и структуру данных"""
        # Стандартные названия колонок
        column_mapping = {
            'Название товара': 'name',
            'Бренд': 'brand',
            'Ссылка на товар': 'link',
            'Категория 1 уровня': 'category_level_1',
            'Категория 2 уровня': 'category_level_2',
            'Категория 3 уровня': 'category_level_3',
            'Категория 4 уровня': 'category_level_4',
        }
        
        # Переименовываем колонки
        df_normalized = df.rename(columns=column_mapping)
        
        # Находим колонку с количеством добавлений в избранное
        favorites_col = None
        for col in df.columns:
            if 'Количество добавлений' in col or 'добавлений в избранное' in col:
                favorites_col = col
                break
        
        if favorites_col:
            df_normalized['favorites_count'] = df[favorites_col]
        else:
            df_normalized['favorites_count'] = 0
        
        # Находим колонку с последним появлением в наличии
        stock_col = None
        for col in df.columns:
            if 'Последнее появление' in col or 'появление в наличии' in col:
                stock_col = col
                break
        
        if stock_col:
            df_normalized['last_in_stock'] = pd.to_datetime(df[stock_col], errors='coerce').dt.date
        else:
            df_normalized['last_in_stock'] = None
        
        # Парсим даты из названия файла
        period_start, period_end = self._parse_filename_dates(filename)
        df_normalized['period_start'] = period_start
        df_normalized['period_end'] = period_end
        
        # Создаем уникальный ID для товара
        def create_product_id(row):
            """Создает уникальный ID на основе названия, бренда и ссылки"""
            key = f"{row.get('name', '')}|{row.get('brand', '')}|{row.get('link', '')}"
            return hashlib.md5(key.encode()).hexdigest()[:16]
        
        df_normalized['id'] = df_normalized.apply(create_product_id, axis=1)
        
        # Выбираем только нужные колонки
        required_cols = ['id', 'name', 'brand', 'link', 'category_level_1', 
                        'category_level_2', 'category_level_3', 'category_level_4',
                        'favorites_count', 'last_in_stock', 'period_start', 'period_end']
        
        # Добавляем отсутствующие колонки
        for col in required_cols:
            if col not in df_normalized.columns:
                df_normalized[col] = None
        
        return df_normalized[required_cols]
    
    def _calculate_days_out_of_stock(self, df: pd.DataFrame) -> pd.DataFrame:
        """Вычисляет количество дней отсутствия в наличии"""
        today = date.today()
        
        def calc_days(row):
            if pd.isna(row['last_in_stock']) or row['last_in_stock'] is None:
                return None
            delta = today - row['last_in_stock']
            return delta.days if delta.days >= 0 else 0
        
        df['days_out_of_stock'] = df.apply(calc_days, axis=1)
        return df
    
    def _load_single_file(self, file_path: Path) -> Optional[Tuple[pd.DataFrame, Dict]]:
        """Загружает один Excel файл"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df_normalized = self._normalize_columns(df, file_path.name)
            
            # Сохраняем метаданные файла
            period_start, period_end = self._parse_filename_dates(file_path.name)
            metadata = {
                'period_start': period_start,
                'period_end': period_end,
                'rows_count': len(df)
            }
            
            return df_normalized, metadata
        except Exception as e:
            print(f"Ошибка при загрузке файла {file_path.name}: {e}")
            return None
    
    def load_all_data(self, force_reload: bool = False) -> pd.DataFrame:
        """Загружает все данные из Excel файлов с кэшированием и параллельной загрузкой"""
        with self._load_lock:
            if self._cache is not None and not force_reload:
                return self._cache
            
            if self._loading:
                # Если загрузка уже идет, ждем ее завершения
                while self._loading:
                    import time
                    time.sleep(0.1)
                if self._cache is not None:
                    return self._cache
            
            self._loading = True
        
        # Пробуем загрузить из SQLite кэша
        if not force_reload:
            cached_df = self._sqlite_cache.get_cached_data(self.data_dir)
            if cached_df is not None:
                with self._load_lock:
                    self._cache = cached_df
                    self._file_metadata = self._sqlite_cache.get_file_metadata()
                    self._loading = False
                    self._using_mock_data = False
                return cached_df
        
        try:
            if not self.data_dir.exists():
                raise FileNotFoundError(f"Директория {self.data_dir} не найдена")
            
            excel_files = list(self.data_dir.glob("*.xlsx"))
            
            if not excel_files:
                raise FileNotFoundError(f"Excel файлы не найдены в {self.data_dir}")
            
            print(f"Начинаю загрузку {len(excel_files)} файлов...")
            
            # Параллельная загрузка файлов
            all_dataframes = []
            file_metadata = {}
            
            # Используем ThreadPoolExecutor для параллельной загрузки
            futures = []
            for file_path in excel_files:
                future = self._executor.submit(self._load_single_file, file_path)
                futures.append((future, file_path.name))
            
            # Собираем результаты
            for future, filename in futures:
                result = future.result()
                if result is not None:
                    df_normalized, metadata = result
                    all_dataframes.append(df_normalized)
                    file_metadata[filename] = metadata
                    print(f"✓ Загружен файл: {filename} ({metadata['rows_count']} строк)")
            
            if not all_dataframes:
                raise ValueError("Не удалось загрузить данные из файлов")
            
            print(f"Объединяю {len(all_dataframes)} датафреймов...")
            
            # Объединяем все данные
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            print("Вычисляю дни отсутствия в наличии...")
            
            # Вычисляем дни отсутствия в наличии
            combined_df = self._calculate_days_out_of_stock(combined_df)
            
            # Кэшируем результат
            with self._load_lock:
                self._cache = combined_df
                self._file_metadata = file_metadata
                self._loading = False
                self._using_mock_data = False
            
            # Сохраняем в SQLite кэш
            self._sqlite_cache.save_data(self.data_dir, combined_df)
            self._sqlite_cache.save_file_metadata(file_metadata)
            
            print(f"✓ Данные загружены: {len(combined_df)} товаров из {len(file_metadata)} файлов")
            
            return combined_df
            
        except Exception as e:
            with self._load_lock:
                self._loading = False
            raise e
    
    def get_file_metadata(self) -> Dict[str, Dict]:
        """Возвращает метаданные загруженных файлов"""
        if self._cache is None:
            self.load_all_data()
        return self._file_metadata
    
    def clear_cache(self):
        """Очищает кэш"""
        with self._load_lock:
            self._cache = None
            self._file_metadata = {}
    
    def load_quick_start_file(self) -> pd.DataFrame:
        """Быстрая загрузка данных для немедленного старта приложения"""
        # Сначала проверяем SQLite кэш
        print("⚡ Быстрый старт: проверяю кэш...")
        cached_df = self._sqlite_cache.get_cached_data(self.data_dir)
        
        if cached_df is not None and len(cached_df) > 0:
            print(f"✅ Данные загружены из кэша: {len(cached_df)} товаров")
            with self._load_lock:
                self._cache = cached_df
                self._file_metadata = self._sqlite_cache.get_file_metadata()
                self._loading = False
                self._using_mock_data = False
                self._data_ready = True
            return cached_df
        
        # Если кэша нет, загружаем мок данные для мгновенного старта
        print("⚡ Быстрый старт: загружаю демонстрационные данные...")
        
        # Генерируем мок данные (1000 товаров, 70% с days_out_of_stock >= 15)
        mock_df = generate_mock_products(1000)
        
        # Вычисляем days_out_of_stock для мок данных
        mock_df = self._calculate_days_out_of_stock(mock_df)
        
        with self._load_lock:
            self._cache = mock_df
            self._file_metadata = {"mock_data": {"rows_count": len(mock_df)}}
            self._loading = False
            self._using_mock_data = True
            self._data_ready = True
        
        high_priority_count = len(mock_df[mock_df['days_out_of_stock'] >= 15])
        print(f"✅ Демонстрационные данные загружены: {len(mock_df)} товаров")
        print(f"   📊 Товаров с days_out_of_stock >= 15: {high_priority_count}")
        print("⚠️ ВНИМАНИЕ: Используются демонстрационные данные. Реальные данные загружаются в фоне.")
        return mock_df
    
    def load_remaining_files_async(self):
        """Асинхронная загрузка реальных данных в фоновом режиме с заменой мок данных"""
        def load_in_background():
            try:
                import time
                time.sleep(2)  # Небольшая задержка, чтобы мок данные успели загрузиться
                
                print("🔄 Начинаю загрузку реальных данных из Excel файлов...")
                print("📊 Демонстрационные данные будут постепенно заменены на реальные")
                
                if not self.data_dir.exists():
                    print("❌ Директория данных не найдена, продолжаем использовать демонстрационные данные")
                    return
                
                excel_files = list(self.data_dir.glob("*.xlsx"))
                
                if not excel_files:
                    print("❌ Excel файлы не найдены, продолжаем использовать демонстрационные данные")
                    return
                
                # Начинаем с быстрого стартового файла
                quick_start_file = "chto-dobavlyaut-v-izbrannoe_-06_03_2021-04_04_2021.xlsx"
                quick_start_path = self.data_dir / quick_start_file
                
                # Сначала загружаем быстрый стартовый файл
                if quick_start_path.exists():
                    try:
                        print(f"📥 Загружаю стартовый файл: {quick_start_file}")
                        result = self._load_single_file(quick_start_path)
                        if result is not None:
                            df_normalized, metadata = result
                            df_normalized = self._calculate_days_out_of_stock(df_normalized)
                            
                            with self._load_lock:
                                # Заменяем мок данные на реальные
                                self._cache = df_normalized
                                self._file_metadata = {quick_start_file: metadata}
                                self._using_mock_data = False
                            
                            print(f"✅ Переключение на реальные данные: {len(df_normalized)} товаров")
                            print("🔄 Продолжаю загрузку остальных файлов...")
                    except Exception as e:
                        print(f"⚠️ Ошибка загрузки стартового файла: {e}")
                
                # Затем загружаем остальные файлы по одному
                remaining_files = [f for f in excel_files if f.name != quick_start_file]
                
                if remaining_files:
                    print(f"📦 Загружаю {len(remaining_files)} дополнительных файлов...")
                    loaded_count = 0
                    
                    for file_path in remaining_files:
                        try:
                            result = self._load_single_file(file_path)
                            if result is not None:
                                df_normalized, metadata = result
                                loaded_count += 1
                                print(f"✓ Загружен файл: {file_path.name} ({metadata['rows_count']} строк)")
                                
                                # Объединяем с существующим кэшем
                                with self._load_lock:
                                    if self._cache is not None:
                                        self._cache = pd.concat([self._cache, df_normalized], ignore_index=True)
                                        self._cache = self._calculate_days_out_of_stock(self._cache)
                                    else:
                                        self._cache = df_normalized
                                        self._cache = self._calculate_days_out_of_stock(self._cache)
                                    
                                    if file_path.name not in self._file_metadata:
                                        self._file_metadata[file_path.name] = metadata
                                    
                                    self._using_mock_data = False
                                
                                print(f"  📊 Всего товаров в кэше: {len(self._cache)}")
                        except Exception as e:
                            print(f"❌ Ошибка при загрузке файла {file_path.name}: {e}")
                            continue
                    
                    with self._load_lock:
                        print(f"✅ Загрузка завершена: {len(self._cache)} товаров из {len(self._file_metadata)} файлов")
                        print("✅ Все данные заменены на реальные")
                else:
                    print("✅ Все файлы загружены")
                
            except Exception as e:
                print(f"❌ Ошибка при фоновой загрузке: {e}")
                print("⚠️ Продолжаем использовать демонстрационные данные")
        
        thread = threading.Thread(target=load_in_background, daemon=True)
        thread.start()
        return thread
    
    def preload_data_async(self):
        """Предзагрузка данных: сначала из кэша/мок, затем реальные"""
        # Сначала загружаем данные из кэша или мок данные мгновенно
        df = self.load_quick_start_file()
        
        # Если загрузили из кэша и это не мок данные, не нужно загружать реальные
        if not self._using_mock_data:
            print("✅ Используются данные из кэша, пропускаю загрузку реальных данных")
            return None
        
        # Если это мок данные, загружаем реальные в фоне
        return self.load_remaining_files_async()


# Глобальный экземпляр загрузчика
_loader_instance: Optional[ExcelLoader] = None


def get_loader(data_dir: Optional[str] = None) -> ExcelLoader:
    """Получает глобальный экземпляр загрузчика (singleton)"""
    global _loader_instance
    if _loader_instance is None:
        # Используем путь из переменной окружения или дефолтный
        if data_dir is None:
            import os
            from pathlib import Path
            data_dir = os.getenv("DATA_DIR", "data")
            # Если путь относительный, делаем его относительно корня проекта
            if not os.path.isabs(data_dir):
                base_dir = Path(__file__).parent.parent.parent
                data_dir = str(base_dir / data_dir)
        _loader_instance = ExcelLoader(data_dir)
    return _loader_instance
