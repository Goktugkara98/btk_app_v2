# =============================================================================
# Veritabanı Geçişleri (V2) - Temiz, Modüler, Idempotent
# =============================================================================
# Amaç: Sadece tanımlanmış şemalardan tablolar oluşturmak.
#
# İçindekiler:
#
# 1. Başlatma ve Sonlandırma (Initialization and Finalization)
#    1.1. __init__(self, db_connection)
#    1.2. __del__(self)
#
# 2. Özel Yardımcı Fonksiyonlar (Private Helper Functions)
#    2.1. _exec(self, conn, sql, params)
#    2.2. _fetchone(self, conn, sql, params)
#    2.3. _ensure_tables(self)
#
# 3. Genel Arayüz (Public Interface)
#    3.1. run_migrations(self)
#    3.2. create_tables(self)
#    3.3. drop_all_tables(self)
#    3.4. force_recreate(self)
#    3.5. get_table_info(self)
#    3.6. seed_initial_data(self)

# 4. Veri Doldurucular (Seeders)
#    4.1. _seed_grades_if_empty(self, conn)
#    4.2. _seed_curriculum_from_json(self, conn)
# =============================================================================

from typing import Optional, Dict
from mysql.connector import Error as MySQLError

from app.database.db_connection import DatabaseConnection
from app.database.schemas import (
    GRADES_TABLE_SQL,
    SUBJECTS_TABLE_SQL,
    UNITS_TABLE_SQL,
    TOPICS_TABLE_SQL,
    QUESTIONS_TABLE_SQL,
    QUESTION_OPTIONS_TABLE_SQL,
    USERS_TABLE_SQL,
    QUIZ_SESSIONS_TABLE_SQL,
    QUIZ_SESSION_QUESTIONS_TABLE_SQL,
)
from app.database.schemas.chat_sessions_schema import get_chat_sessions_schema
from app.database.schemas.chat_messages_schema import get_chat_messages_schema
from app.database.curriculum_data_loader import JSONDataLoader


class DatabaseMigrations:
    """
    Temiz geçiş yöneticisi.
    - Python şemalarından tablolar oluşturur.
    """

    # =========================================================================
    # 1. Başlatma ve Sonlandırma (Initialization and Finalization)
    # =========================================================================

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        """
        1.1. Sınıfı başlatır ve veritabanı bağlantısını ayarlar.
        """
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

        # Şema SQL kayıt defteri
        self.table_schemas = {
            'grades': (GRADES_TABLE_SQL, ''),
            'subjects': (SUBJECTS_TABLE_SQL, ''),
            'units': (UNITS_TABLE_SQL, ''),
            'topics': (TOPICS_TABLE_SQL, ''),
            'questions': (QUESTIONS_TABLE_SQL, ''),
            'question_options': (QUESTION_OPTIONS_TABLE_SQL, ''),
            'users': (USERS_TABLE_SQL, ''),
            'quiz_sessions': (QUIZ_SESSIONS_TABLE_SQL, ''),
            'quiz_session_questions': (QUIZ_SESSION_QUESTIONS_TABLE_SQL, ''),
            'chat_sessions': (get_chat_sessions_schema(), ''),
            'chat_messages': (get_chat_messages_schema(), ''),
        }
        # Yabancı anahtar (FK) kısıtlamalarına uygun oluşturma sırası
        self.table_order = [
            'grades', 'subjects', 'units', 'topics',
            'questions', 'question_options', 'users',
            'quiz_sessions', 'quiz_session_questions',
            'chat_sessions', 'chat_messages'
        ]

    def __del__(self) -> None:
        """
        1.2. Sınıf tarafından oluşturulan veritabanı bağlantısını kapatır.
        """
        if self.own_connection:
            try:
                self.db.close()
            except Exception:
                pass

    # =========================================================================
    # 2. Özel Yardımcı Fonksiyonlar (Private Helper Functions)
    # =========================================================================

    def _exec(self, conn, sql: str, params: tuple | None = None) -> bool:
        """
        2.1. Verilen SQL sorgusunu parametrelerle birlikte çalıştırır ve commit eder.
        """
        try:
            if params:
                conn.cursor.execute(sql, params)
            else:
                conn.cursor.execute(sql)
            conn.connection.commit()
            return True
        except MySQLError:
            return False

    def _fetchone(self, conn, sql: str, params: tuple | None = None):
        """
        2.2. Verilen SQL sorgusunu çalıştırır ve tek bir sonuç satırı döndürür.
        """
        try:
            if params:
                conn.cursor.execute(sql, params)
            else:
                conn.cursor.execute(sql)
            return conn.cursor.fetchone()
        except MySQLError:
            return None

    def _ensure_tables(self) -> bool:
        """
        2.3. Tanımlanmış sıraya göre tüm tabloların veritabanında var olmasını sağlar.
        """
        try:
            with self.db as conn:
                for table in self.table_order:
                    create_sql, _ = self.table_schemas[table]
                    if not self._exec(conn, create_sql):
                        return False
                return True
        except Exception:
            return False

    # =========================================================================
    # 3. Genel Arayüz (Public Interface)
    # =========================================================================

    def run_migrations(self) -> bool:
        """
        3.1. Yalnızca Python şemalarına göre tablolar oluşturur.
             Burada sütun/kısıtlama geçişleri veya veri değişiklikleri yapılmaz.
        """
        return self._ensure_tables()

    def create_tables(self) -> bool:
        """
        3.2. Şemalara göre tabloları oluşturur. `run_migrations` için bir takma addır.
        """
        return self._ensure_tables()

    def drop_all_tables(self) -> bool:
        """
        3.3. Yabancı anahtar (FK) kısıtlamalarını dikkate alarak tüm tabloları siler.
        """
        try:
            with self.db as conn:
                # FK'ları onurlandırmak için ters sırada sil
                for table in reversed(self.table_order):
                    self._exec(conn, f"DROP TABLE IF EXISTS {table}")
            return True
        except Exception:
            return False

    def force_recreate(self) -> bool:
        """
        3.4. Tüm tabloları siler ve ardından yeniden oluşturur.
        """
        return self.drop_all_tables() and self.create_tables()

    def get_table_info(self) -> Dict[str, int]:
        """
        3.5. Her tablodaki satır sayısını içeren bir sözlük döndürür.
        """
        out: Dict[str, int] = {}
        try:
            with self.db as conn:
                for t in self.table_order:
                    row = self._fetchone(conn, f"SELECT COUNT(*) AS cnt FROM {t}")
                    out[t] = (row.get('cnt') if isinstance(row, dict) else 0) if row else 0
        except Exception:
            pass
        return out

    def seed_initial_data(self) -> bool:
        """
        3.6. Uygulama için gerekli başlangıç verilerini (seed) ekler.
             Şemalara göre tabloları garanti altına alır, ardından seed işlemlerini uygular.
        """
        try:
            if not self._ensure_tables():
                return False
            with self.db as conn:
                self._seed_grades_if_empty(conn)
                self._seed_curriculum_from_json(conn)
            return True
        except Exception:
            return False

    # =========================================================================
    # 4. Veri Doldurucular (Seeders)
    # =========================================================================

    def _seed_grades_if_empty(self, conn) -> None:
        """
        4.1. Grades tablosunu 1..12 sınıf temel verileriyle doldurur.
             Zaten veri varsa işlemi atlar; yoksa idempotent şekilde ekler/günceller.
        """
        row = self._fetchone(conn, "SELECT COUNT(*) AS cnt FROM grades")
        count = (row.get('cnt') if isinstance(row, dict) else 0) if row else 0
        if count and count > 0:
            return
        values = []
        for i in range(1, 13):
            name = f"{i}. Sınıf".replace("'", "''")
            desc = f"{i}. Sınıf seviyesi".replace("'", "''")
            values.append(f"({i}, '{name}', '{desc}', 1)")
        sql = (
            "INSERT INTO grades (grade_id, grade_name, description, is_active) VALUES "
            + ", ".join(values)
            + " ON DUPLICATE KEY UPDATE grade_name=VALUES(grade_name), description=VALUES(description), is_active=VALUES(is_active)"
        )
        self._exec(conn, sql)

    def _seed_curriculum_from_json(self, conn) -> None:
        """
        4.2. Müfredat verilerini JSON dosyalarından yükler ve idempotent olarak
             grades/subjects/units/topics tablolarına yazar.
        """
        try:
            loader = JSONDataLoader()
            # JSON'ları yükle ve bellek yapıları oluştur
            loader.load_all_grade_files()
            loader.extract_subjects()
            loader.extract_units()
            loader.extract_topics()

            # Grades: doğrudan SQL üret ve çalıştır
            grades_sql = loader.generate_grades_sql()
            if grades_sql:
                self._exec(conn, grades_sql)

            # Haritaları çıkar ve alt tabloları sırayla doldur
            grade_id_map = loader.get_grade_id_map(conn)
            subjects_sql = loader.generate_subjects_sql(grade_id_map)
            if subjects_sql:
                self._exec(conn, subjects_sql)

            subject_id_map = loader.get_subject_id_map(conn)
            units_sql = loader.generate_units_sql(subject_id_map)
            if units_sql:
                self._exec(conn, units_sql)

            unit_id_map = loader.get_unit_id_map(conn)
            topics_sql = loader.generate_topics_sql(unit_id_map)
            if topics_sql:
                self._exec(conn, topics_sql)
        except Exception:
            # Sessizce geç: JSON yoksa ya da hatalıysa uygulamayı engellemesin
            pass
