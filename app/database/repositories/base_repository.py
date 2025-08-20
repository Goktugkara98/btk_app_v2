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
        cursor = None
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(dictionary=True, buffered=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Database fetch_all error: {e}")
            return []
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Warning: Error closing cursor: {e}")
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Tek kayıt getirir"""
        cursor = None
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(dictionary=True, buffered=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Database fetch_one error: {e}")
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Warning: Error closing cursor: {e}")
    
    def execute_query(self, query: str, params: tuple = None) -> int:
        """Query çalıştırır ve etkilenen satır sayısını döner"""
        cursor = None
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(buffered=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.db_connection.connection.commit()
            
            # INSERT işlemi için son eklenen ID'yi döner
            if query.strip().upper().startswith('INSERT'):
                last_id = cursor.lastrowid
                return last_id
            else:
                # UPDATE/DELETE için etkilenen satır sayısını döner
                affected_rows = cursor.rowcount
                return affected_rows
                
        except Exception as e:
            print(f"Database execute_query error: {e}")
            if self.db_connection.connection:
                try:
                    self.db_connection.connection.rollback()
                except Exception as rollback_error:
                    print(f"Warning: Rollback error: {rollback_error}")
            return 0
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Warning: Error closing cursor: {e}")
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Birden fazla query çalıştırır"""
        cursor = None
        try:
            self.db_connection._ensure_connection()
            cursor = self.db_connection.connection.cursor(buffered=True)
            
            cursor.executemany(query, params_list)
            self.db_connection.connection.commit()
            
            affected_rows = cursor.rowcount
            return affected_rows
            
        except Exception as e:
            print(f"Database execute_many error: {e}")
            if self.db_connection.connection:
                try:
                    self.db_connection.connection.rollback()
                except Exception as rollback_error:
                    print(f"Warning: Rollback error: {rollback_error}")
            return 0
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Warning: Error closing cursor: {e}")
