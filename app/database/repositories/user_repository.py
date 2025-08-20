"""
User Repository - User Management
Handles all database operations for users
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Kullanıcıları yöneten repository"""
    
    def __init__(self):
        """User repository'yi başlatır"""
        super().__init__()
        self.table_name = 'users'
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm kullanıcıları getirir"""
        try:
            query = """
                SELECT id, username, email, first_name, last_name, is_admin, is_active, 
                       last_login, created_at, updated_at
                FROM users 
                ORDER BY created_at DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre kullanıcı getirir"""
        try:
            query = """
                SELECT user_id, username, email, password_hash, first_name, last_name, is_admin, is_active, 
                       created_at, updated_at
                FROM users WHERE user_id = %s
            """
            return self.fetch_one(query, (user_id,))
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı adına göre kullanıcı getirir"""
        try:
            query = """
                SELECT id, username, email, first_name, last_name, is_admin, is_active, 
                       last_login, created_at, updated_at
                FROM users WHERE username = %s
            """
            return self.fetch_one(query, (username,))
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Email'e göre kullanıcı getirir"""
        print('=== LOGIN DEBUG (USER REPOSITORY) ===')
        print(f'Looking up user by email: {email}')
        
        try:
            query = """
                SELECT user_id, username, email, password_hash, first_name, last_name, is_admin, is_active, 
                       created_at, updated_at
                FROM users WHERE email = %s
            """
            print(f'Executing query: {query}')
            print(f'Query parameters: {(email,)}')
            
            result = self.fetch_one(query, (email,))
            
            if result:
                # Don't print password_hash for security, but show that it exists
                safe_result = dict(result)
                if 'password_hash' in safe_result:
                    safe_result['password_hash'] = f'[HASH_EXISTS: {bool(safe_result["password_hash"])}]'
                print(f'User found: {safe_result}')
            else:
                print('User not found')
            
            return result
            
        except Exception as e:
            print(f"ERROR: Exception in get_by_email: {e}")
            import traceback
            print(f'Traceback: {traceback.format_exc()}')
            return None
    
    def create_user(self, username: str, email: str, hashed_password: str, **kwargs) -> Optional[int]:
        """Yeni kullanıcı oluşturur"""
        try:
            query = """
                INSERT INTO users (username, email, password_hash, first_name, last_name, 
                                 is_admin, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            params = (
                username,
                email,
                hashed_password,
                kwargs.get('first_name', ''),
                kwargs.get('last_name', ''),
                kwargs.get('is_admin', False),
                kwargs.get('is_active', True)
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini günceller"""
        try:
            # Sadece güncellenebilir alanları al
            updateable_fields = ['first_name', 'last_name', 'is_active']
            update_data = {}
            
            for field in updateable_fields:
                if field in data:
                    update_data[field] = data[field]
            
            if not update_data:
                return False
            
            # SQL query oluştur
            set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
            query = f"""
                UPDATE users 
                SET {set_clause}, updated_at = NOW()
                WHERE id = %s
            """
            
            params = list(update_data.values()) + [user_id]
            return self.execute_query(query, tuple(params)) > 0
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def count_all(self) -> int:
        """Toplam kullanıcı sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    def count_active(self) -> int:
        """Aktif kullanıcı sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE is_active = 1"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting active users: {e}")
            return 0
    
    def count_recent_logins(self, days: int = 7) -> int:
        """Son X günde giriş yapan kullanıcı sayısını getirir"""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM users 
                WHERE last_login >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            result = self.fetch_one(query, (days,))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting recent logins: {e}")
            return 0
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """Arama terimine göre kullanıcı arar"""
        try:
            query = """
                SELECT id, username, email, first_name, last_name, is_admin, is_active, 
                       last_login, created_at, updated_at
                FROM users 
                WHERE username LIKE %s OR email LIKE %s OR first_name LIKE %s OR last_name LIKE %s
                ORDER BY created_at DESC
            """
            search_pattern = f"%{search_term}%"
            return self.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Sadece aktif kullanıcıları getirir"""
        try:
            query = """
                SELECT id, username, email, first_name, last_name, is_admin, is_active, 
                       last_login, created_at, updated_at
                FROM users 
                WHERE is_active = 1
                ORDER BY created_at DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting active users: {e}")
            return []
    
    def get_admin_users(self) -> List[Dict[str, Any]]:
        """Sadece admin kullanıcıları getirir"""
        try:
            query = """
                SELECT id, username, email, first_name, last_name, is_admin, is_active, 
                       last_login, created_at, updated_at
                FROM users 
                WHERE is_admin = 1
                ORDER BY created_at DESC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting admin users: {e}")
            return []
    
    def bulk_update_status(self, user_ids: List[int], is_active: bool) -> bool:
        """Birden fazla kullanıcının durumunu toplu günceller"""
        try:
            if not user_ids:
                return True
            
            placeholders = ','.join(['%s'] * len(user_ids))
            query = f"""
                UPDATE users 
                SET is_active = %s, updated_at = NOW()
                WHERE id IN ({placeholders})
            """
            
            params = [is_active] + user_ids
            return self.execute_query(query, tuple(params)) > 0
            
        except Exception as e:
            print(f"Error bulk updating user status: {e}")
            return False
