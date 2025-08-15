from typing import Optional
from app.database.db_connection import DatabaseConnection


class UsersSeeder:
    """Seed default users for development/testing (idempotent).

    Notes:
    - Uses email unique constraint for ON DUPLICATE KEY UPDATE.
    - Password hashes are placeholders and should be replaced in production.
    """

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

    def seed_default_users(self) -> bool:
        try:
            sql = (
                "INSERT INTO users "
                "(username, email, password_hash, first_name, last_name, phone, birth_date, gender, country, city, school, bio, is_admin) VALUES "
                "('admin', 'admin@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Admin', 'User', '+90 555 123 4567', '1990-01-01', 'male', 'Turkey', 'Ankara', 'BTK Akademi', 'Sistem yöneticisi', true),"
                "('demo_user', 'demo@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Demo', 'User', '+90 555 987 6543', '2000-05-15', 'female', 'Turkey', 'Istanbul', 'Demo Okulu', 'Demo kullanıcı hesabı', false),"
                "('test_user', 'test@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Test', 'User', '+90 555 111 2222', '1995-12-20', 'other', 'Turkey', 'Izmir', 'Test Okulu', 'Test kullanıcı hesabı', false) "
                "ON DUPLICATE KEY UPDATE "
                "username = VALUES(username), "
                "first_name = VALUES(first_name), "
                "last_name = VALUES(last_name), "
                "phone = VALUES(phone), "
                "birth_date = VALUES(birth_date), "
                "gender = VALUES(gender), "
                "country = VALUES(country), "
                "city = VALUES(city), "
                "school = VALUES(school), "
                "bio = VALUES(bio)"
            )
            with self.db as conn:
                conn.cursor.execute(sql)
                conn.connection.commit()
            return True
        except Exception:
            return False
