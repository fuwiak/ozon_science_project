"""
SQLite кэш для сохранения данных между запусками
"""
import sqlite3
import pandas as pd
import pickle
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime
import os


class SQLiteCache:
    """Кэш данных в SQLite для быстрого доступа"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "data_cache.db"
        self._init_db()
    
    def _init_db(self):
        """Инициализирует базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для кэша данных
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_cache (
                key TEXT PRIMARY KEY,
                data BLOB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Таблица для метаданных файлов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                filename TEXT PRIMARY KEY,
                metadata TEXT,
                updated_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_data_hash(self, data_dir: Path) -> str:
        """Вычисляет хэш всех Excel файлов для проверки изменений"""
        excel_files = sorted(data_dir.glob("*.xlsx"))
        if not excel_files:
            return ""
        
        # Создаем хэш на основе имен файлов и их размеров
        file_info = []
        for f in excel_files:
            try:
                stat = f.stat()
                file_info.append(f"{f.name}:{stat.st_mtime}:{stat.st_size}")
            except:
                pass
        
        content = "|".join(file_info)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_data(self, data_dir: Path) -> Optional[pd.DataFrame]:
        """Получает закэшированные данные"""
        try:
            # Сначала пробуем найти кэш по хэшу текущих файлов
            data_hash = self._get_data_hash(data_dir)
            cache_key = f"products_{data_hash}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data FROM data_cache 
                WHERE key = ?
            """, (cache_key,))
            
            result = cursor.fetchone()
            
            # Если не нашли по точному хэшу, берем последний кэш
            if not result:
                cursor.execute("""
                    SELECT data FROM data_cache 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
            
            conn.close()
            
            if result:
                data_bytes = result[0]
                df = pickle.loads(data_bytes)
                print(f"✅ Данные загружены из кэша: {len(df)} товаров")
                return df
            
            return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения кэша: {e}")
            return None
    
    def save_data(self, data_dir: Path, df: pd.DataFrame):
        """Сохраняет данные в кэш"""
        try:
            data_hash = self._get_data_hash(data_dir)
            cache_key = f"products_{data_hash}"
            
            data_bytes = pickle.dumps(df)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO data_cache (key, data, created_at, updated_at)
                VALUES (?, ?, 
                    COALESCE((SELECT created_at FROM data_cache WHERE key = ?), ?),
                    ?)
            """, (cache_key, data_bytes, cache_key, now, now))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Данные сохранены в кэш: {len(df)} товаров")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения кэша: {e}")
    
    def save_file_metadata(self, metadata: dict):
        """Сохраняет метаданные файлов"""
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            for filename, meta in metadata.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO file_metadata (filename, metadata, updated_at)
                    VALUES (?, ?, ?)
                """, (filename, json.dumps(meta), now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Ошибка сохранения метаданных: {e}")
    
    def get_file_metadata(self) -> dict:
        """Получает метаданные файлов из кэша"""
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT filename, metadata FROM file_metadata")
            results = cursor.fetchall()
            conn.close()
            
            metadata = {}
            for filename, meta_json in results:
                metadata[filename] = json.loads(meta_json)
            
            return metadata
        except Exception as e:
            print(f"⚠️ Ошибка чтения метаданных: {e}")
            return {}
    
    def clear_cache(self):
        """Очищает весь кэш"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data_cache")
            cursor.execute("DELETE FROM file_metadata")
            conn.commit()
            conn.close()
            print("✅ Кэш очищен")
        except Exception as e:
            print(f"⚠️ Ошибка очистки кэша: {e}")

