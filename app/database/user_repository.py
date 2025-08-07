# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, kullanıcılar (`users` tablosu) ile ilgili tüm veritabanı
# işlemlerini (CRUD) yöneten `UserRepository` sınıfını içerir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER (GÜNCELLENDİ)
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER
# 4.0. USERREPOSITORY SINIFI
#   4.1. Başlatma ve Bağlantı Sahipliği
#     4.1.1. __init__(self, db_connection)
#   4.2. Dahili Bağlantı Yönetimi
#     4.2.1. _ensure_connection(self)
#     4.2.2. _close_if_owned(self)
#   4.3. CRUD (Create, Read, Update, Delete) Metotları
#     4.3.1. create_user(self, username, email, hashed_password, **kwargs)
#     4.3.2. get_user(self, username)
#     4.3.3. get_user_by_email(self, email)
#     4.3.4. get_user_by_id(self, user_id)
#     4.3.5. get_all_users(self)
#     4.3.6. update_user(self, user_id, **kwargs)
#     4.3.7. change_password(self, user_id, new_password_hash)
#     4.3.8. delete_user(self, user_id)
#     4.3.9. check_username_exists(self, username)
#     4.3.10. check_email_exists(self, email)
#     4.3.11. check_username_or_email_exists(self, username, email)
#     4.3.12. get_user_profile(self, user_id)
#     4.3.13. search_users(self, search_term)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER
# =============================================================================
from mysql.connector import Error as MySQLError
from typing import Optional, Dict, List, Tuple
from app.database.db_connection import DatabaseConnection

# =============================================================================
# 4.0. USERREPOSITORY SINIFI
# =============================================================================
class UserRepository:
    """
    Kullanıcı verilerinin veritabanı işlemlerini yönetir.
    """

    # -------------------------------------------------------------------------
    # 4.1. Başlatma ve Bağlantı Sahipliği
    # -------------------------------------------------------------------------
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """4.1.1. Sınıfın kurucu metodu. Harici veya dahili bağlantı kullanır."""
        if db_connection:
            self.db: DatabaseConnection = db_connection
            self.own_connection: bool = False
        else:
            self.db: DatabaseConnection = DatabaseConnection()
            self.own_connection: bool = True

    # -------------------------------------------------------------------------
    # 4.2. Dahili Bağlantı Yönetimi
    # -------------------------------------------------------------------------
    def _ensure_connection(self):
        """4.2.1. Veritabanı bağlantısı kapalıysa yeniden kurar."""
        self.db._ensure_connection()

    def _close_if_owned(self):
        """4.2.2. Eğer bağlantı bu sınıf tarafından oluşturulduysa kapatır."""
        if self.own_connection:
            self.db.close()

    # -------------------------------------------------------------------------
    # 4.3. CRUD (Create, Read, Update, Delete) Metotları
    # -------------------------------------------------------------------------
    def create_user(self, username: str, email: str, hashed_password: str, **kwargs) -> Optional[int]:
        """4.3.1. Veritabanına yeni bir kullanıcı ekler."""
        self._ensure_connection()
        try:
            with self.db as conn:
                # Temel alanlar (name_id otomatik olarak username ile aynı)
                fields = ['username', 'name_id', 'email', 'password_hash']
                values = [username, username, email, hashed_password]
                
                # Opsiyonel alanlar
                optional_fields = [
                    'first_name', 'last_name', 'phone', 'birth_date', 'gender',
                    'school', 'grade_level_id', 'bio', 'avatar_path'
                ]
                
                for field in optional_fields:
                    if field in kwargs and kwargs[field] is not None:
                        fields.append(field)
                        values.append(kwargs[field])
                
                query = f"INSERT INTO users ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"
                conn.cursor.execute(query, values)
                conn.connection.commit()
                user_id = conn.cursor.lastrowid
                return user_id
        except MySQLError as e:
            if e.errno == 1062: # Duplicate entry
                return None
            return None
        finally:
            self._close_if_owned()

    def get_user(self, username: str) -> Optional[Dict]:
        """4.3.2. Kullanıcı adına göre bir kullanıcıyı getirir."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT u.id, u.username, u.email, u.password_hash, u.first_name, u.last_name, 
                           u.phone, u.birth_date, u.gender, u.school, u.grade_level_id,
                           u.bio, u.avatar_path, u.created_at, u.updated_at
                    FROM users u
                    WHERE u.username = %s
                """
                conn.cursor.execute(query, (username,))
                return conn.cursor.fetchone()
        except MySQLError:
            return None
        finally:
            self._close_if_owned()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """4.3.3. Email adresine göre bir kullanıcıyı getirir."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT u.id, u.username, u.email, u.password_hash, u.first_name, u.last_name, 
                           u.phone, u.birth_date, u.gender, u.school, u.grade_level_id,
                           u.bio, u.avatar_path, u.created_at, u.updated_at
                    FROM users u
                    WHERE u.email = %s
                """
                conn.cursor.execute(query, (email,))
                return conn.cursor.fetchone()
        except MySQLError:
            return None
        finally:
            self._close_if_owned()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """4.3.4. ID'ye göre bir kullanıcıyı getirir."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT u.id, u.username, u.email, u.password_hash, u.first_name, u.last_name, 
                           u.phone, u.birth_date, u.gender, u.school, u.grade_level_id,
                           u.bio, u.avatar_path, u.created_at, u.updated_at
                    FROM users u
                    WHERE u.id = %s
                """
                conn.cursor.execute(query, (user_id,))
                result = conn.cursor.fetchone()
                return result
        except MySQLError as e:
            return None
        finally:
            self._close_if_owned()

    def get_all_users(self) -> List[Dict]:
        """4.3.5. Veritabanındaki tüm kullanıcıları getirir."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT u.id, u.username, u.email, u.password_hash, u.first_name, u.last_name, 
                           u.phone, u.birth_date, u.gender, u.school, u.grade_level_id,
                           u.bio, u.avatar_path, u.created_at, u.updated_at
                    FROM users u
                    ORDER BY u.created_at DESC
                """
                conn.cursor.execute(query)
                return conn.cursor.fetchall()
        except MySQLError:
            return []
        finally:
            self._close_if_owned()

    def update_user(self, user_id: int, **kwargs) -> bool:
        """4.3.6. Bir kullanıcının bilgilerini günceller."""
        self._ensure_connection()
        try:
            with self.db as conn:
                # Güncellenebilir alanlar
                updatable_fields = [
                    'username', 'email', 'first_name', 'last_name', 'phone', 
                    'birth_date', 'gender', 'school', 'grade_level_id', 'bio', 'avatar_path'
                ]
                
                # Güncellenecek alanları filtrele
                update_fields = []
                update_values = []
                
                for field in updatable_fields:
                    if field in kwargs and kwargs[field] is not None:
                        update_fields.append(f"{field} = %s")
                        update_values.append(kwargs[field])
                
                if not update_fields:
                    return False
                
                update_values.append(user_id)
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
                
                conn.cursor.execute(query, update_values)
                conn.connection.commit()
                row_count = conn.cursor.rowcount
                return row_count > 0
        except MySQLError as e:
            conn.connection.rollback()
            return False
        except Exception as e:
            return False
        finally:
            self._close_if_owned()

    def change_password(self, user_id: int, new_password_hash: str) -> bool:
        """4.3.7. Bir kullanıcının şifresini günceller."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = "UPDATE users SET password_hash = %s WHERE id = %s"
                conn.cursor.execute(query, (new_password_hash, user_id))
                conn.connection.commit()
                return conn.cursor.rowcount > 0
        except MySQLError:
            conn.connection.rollback()
            return False
        finally:
            self._close_if_owned()

    def delete_user(self, user_id: int) -> bool:
        """4.3.8. Bir kullanıcıyı ID'ye göre siler."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = "DELETE FROM users WHERE id = %s"
                conn.cursor.execute(query, (user_id,))
                conn.connection.commit()
                return conn.cursor.rowcount > 0
        except MySQLError:
            conn.connection.rollback()
            return False
        finally:
            self._close_if_owned()

    def check_username_exists(self, username: str) -> bool:
        """4.3.9. Kullanıcı adının var olup olmadığını kontrol eder."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
                conn.cursor.execute(query, (username,))
                result = conn.cursor.fetchone()
                return result['count'] > 0
        except MySQLError:
            return False
        finally:
            self._close_if_owned()

    def check_email_exists(self, email: str) -> bool:
        """4.3.10. Email adresinin var olup olmadığını kontrol eder."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
                conn.cursor.execute(query, (email,))
                result = conn.cursor.fetchone()
                return result['count'] > 0
        except MySQLError:
            return False
        finally:
            self._close_if_owned()

    def check_username_or_email_exists(self, username: str, email: str) -> Tuple[bool, bool]:
        """4.3.11. Hem kullanıcı adı hem de email'in var olup olmadığını kontrol eder."""
        self._ensure_connection()
        try:
            with self.db as conn:
                # Kullanıcı adı kontrolü
                username_query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
                conn.cursor.execute(username_query, (username,))
                username_result = conn.cursor.fetchone()
                username_exists = username_result['count'] > 0

                # Email kontrolü
                email_query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
                conn.cursor.execute(email_query, (email,))
                email_result = conn.cursor.fetchone()
                email_exists = email_result['count'] > 0

                return username_exists, email_exists
        except MySQLError as e:
            return False, False
        finally:
            self._close_if_owned()

    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """4.3.12. Kullanıcının profil bilgilerini getirir (şifre hariç)."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT id, username, email, first_name, last_name, 
                           phone, birth_date, gender, school, grade_level_id,
                           bio, avatar_path, created_at, updated_at
                    FROM users u
                    WHERE u.id = %s
                """
                conn.cursor.execute(query, (user_id,))
                return conn.cursor.fetchone()
        except MySQLError:
            return None
        finally:
            self._close_if_owned()

    def search_users(self, search_term: str) -> List[Dict]:
        """4.3.13. Kullanıcıları arama terimine göre arar."""
        self._ensure_connection()
        try:
            with self.db as conn:
                query = """
                    SELECT u.id, u.username, u.email, u.first_name, u.last_name, 
                           u.school, u.grade_level_id
                    FROM users u
                    WHERE u.username LIKE %s OR u.email LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s
                    ORDER BY u.username
                    LIMIT 50
                """
                search_pattern = f"%{search_term}%"
                conn.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
                return conn.cursor.fetchall()
        except MySQLError:
            return []
        finally:
            self._close_if_owned()
