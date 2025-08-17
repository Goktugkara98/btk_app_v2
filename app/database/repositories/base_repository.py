# =============================================================================
# BASE REPOSITORY
# =============================================================================
# Temel veritabanı işlemleri için base repository sınıfı
# =============================================================================

from app.database.db_connection import DatabaseConnection
from typing import List, Dict, Optional, Any

class BaseRepository:
    """Temel veritabanı işlemleri için base repository"""
    
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Birden fazla kayıt getirir"""
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"Database fetch_all error: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Tek kayıt getirir"""
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            print(f"Database fetch_one error: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> int:
        """Query çalıştırır ve etkilenen satır sayısını döner"""
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.db_connection.connection.commit()
            
            # INSERT işlemi için son eklenen ID'yi döner
            if query.strip().upper().startswith('INSERT'):
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
            else:
                # UPDATE/DELETE için etkilenen satır sayısını döner
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Exception as e:
            print(f"Database execute_query error: {e}")
            self.db_connection.connection.rollback()
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Birden fazla query çalıştırır"""
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor()
            
            cursor.executemany(query, params_list)
            self.db_connection.connection.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
            
        except Exception as e:
            print(f"Database execute_many error: {e}")
            self.db_connection.connection.rollback()
            return 0
