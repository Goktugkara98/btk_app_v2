from typing import Optional
from app.database.db_connection import DatabaseConnection
from werkzeug.security import generate_password_hash


class UsersSeeder:
    """Seed default users for development/testing (idempotent).

    Notes:
    - Uses email unique constraint for ON DUPLICATE KEY UPDATE.
    - Default dev password is 'admin123' (only for development/testing!).
      In production, seeders should be disabled and strong passwords enforced.
    """

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

    def seed_default_users(self) -> bool:
        try:
            # Generate a Werkzeug-compatible password hash for dev users
            # IMPORTANT: This is only for local development/testing.
            default_password = 'admin123'
            password_hash = generate_password_hash(default_password)

            sql = (
                "INSERT INTO users "
                "(username, email, password_hash, first_name, last_name, phone, birth_date, gender, country, city, school, bio, is_admin) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
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
                "bio = VALUES(bio), "
                "password_hash = VALUES(password_hash), "
                "is_admin = VALUES(is_admin)"
            )

            data = [
                (
                    'admin', 'admin@btk.com', password_hash, 'Admin', 'User',
                    '+90 555 123 4567', '1990-01-01', 'male', 'Turkey', 'Ankara',
                    'BTK Akademi', 'Sistem yöneticisi', True
                ),
                (
                    'demo_user', 'demo@btk.com', password_hash, 'Demo', 'User',
                    '+90 555 987 6543', '2000-05-15', 'female', 'Turkey', 'Istanbul',
                    'Demo Okulu', 'Demo kullanıcı hesabı', False
                ),
                (
                    'test_user', 'test@btk.com', password_hash, 'Test', 'User',
                    '+90 555 111 2222', '1995-12-20', 'other', 'Turkey', 'Izmir',
                    'Test Okulu', 'Test kullanıcı hesabı', False
                ),
            ]

            with self.db as conn:
                conn.cursor.executemany(sql, data)
                conn.connection.commit()
            return True
        except Exception:
            return False

