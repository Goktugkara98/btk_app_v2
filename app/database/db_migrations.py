# =============================================================================
# Veritabanı Migrations - Python Schema Tabanlı Yapı
# =============================================================================
# Bu modül, veritabanı tablolarını oluşturmak için kullanılır.
# Python şemaları app/database/schemas/ klasöründe tutulur.
# JSON verileri app/data/curriculum_structure/ klasöründen dinamik olarak yüklenir.
# =============================================================================

from mysql.connector import Error as MySQLError
from typing import Optional, Dict, List
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.db_connection import DatabaseConnection
from app.database.curriculum_data_loader import JSONDataLoader
from app.database.schemas import (
    GRADES_TABLE_SQL, GRADES_SAMPLE_DATA,
    SUBJECTS_TABLE_SQL, SUBJECTS_SAMPLE_DATA,
    UNITS_TABLE_SQL, UNITS_SAMPLE_DATA,
    TOPICS_TABLE_SQL, TOPICS_SAMPLE_DATA,
    QUESTIONS_TABLE_SQL,
    QUESTION_OPTIONS_TABLE_SQL,
    USERS_TABLE_SQL, USERS_SAMPLE_DATA,
    QUIZ_SESSIONS_TABLE_SQL, QUIZ_SESSIONS_SAMPLE_DATA,
    QUIZ_SESSION_QUESTIONS_TABLE_SQL, QUIZ_SESSION_QUESTIONS_SAMPLE_DATA
)
from app.database.schemas.chat_sessions_schema import get_chat_sessions_schema
from app.database.schemas.chat_messages_schema import get_chat_messages_schema

class DatabaseMigrations:
    """
    Python schema tabanlı veritabanı migration sınıfı.
    Python şemalarını kullanarak tabloları oluşturur.
    JSON dosyalarından dinamik veri yükler.
    """

    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Sınıfın kurucu metodu."""
        if db_connection:
            self.db: DatabaseConnection = db_connection
            self.own_connection: bool = False
        else:
            self.db: DatabaseConnection = DatabaseConnection()
            self.own_connection: bool = True
        
        # JSON veri yükleyici
        self.json_loader = JSONDataLoader()
        
        # Tablo şemaları ve örnek veriler
        self.table_schemas = {
            'grades': (GRADES_TABLE_SQL, ""),  # JSON'dan doldurulacak
            'subjects': (SUBJECTS_TABLE_SQL, ""),  # JSON'dan doldurulacak
            'units': (UNITS_TABLE_SQL, ""),  # JSON'dan doldurulacak
            'topics': (TOPICS_TABLE_SQL, ""),  # JSON'dan doldurulacak
            'questions': (QUESTIONS_TABLE_SQL, ""),
            'question_options': (QUESTION_OPTIONS_TABLE_SQL, ""),
            'users': (USERS_TABLE_SQL, USERS_SAMPLE_DATA),
            'quiz_sessions': (QUIZ_SESSIONS_TABLE_SQL, QUIZ_SESSIONS_SAMPLE_DATA),
            'quiz_session_questions': (QUIZ_SESSION_QUESTIONS_TABLE_SQL, QUIZ_SESSION_QUESTIONS_SAMPLE_DATA),
            'chat_sessions': (get_chat_sessions_schema(), ""),  # Chat sessions
            'chat_messages': (get_chat_messages_schema(), "")  # Chat messages
        }
        
        # Tablo oluşturma sırası (foreign key bağımlılıklarına göre)
        self.table_order = ['grades', 'subjects', 'units', 'topics', 'questions', 'question_options', 'users', 'quiz_sessions', 'quiz_session_questions', 'chat_sessions', 'chat_messages']

    def __del__(self):
        """Destructor - bağlantıyı temizle."""
        if self.own_connection:
            self.db.close()

    def _execute_sql(self, sql: str, params: tuple = None) -> bool:
        """SQL komutunu çalıştırır."""
        try:
            with self.db as conn:
                if params:
                    conn.cursor.execute(sql, params)
                else:
                    conn.cursor.execute(sql)
                conn.connection.commit()
                return True
        except MySQLError:
            return False

    def _create_table(self, table_name: str, table_sql: str, sample_data: str) -> bool:
        """Tabloyu oluşturur ve örnek verileri ekler."""
        try:
            # Tabloyu oluştur
            if not self._execute_sql(table_sql):
                return False
            
            # Örnek verileri ekle (eğer varsa)
            if sample_data:
                self._execute_sql(sample_data)
            
            return True
            
        except Exception:
            return False

    def _migrate_quiz_sessions_schema(self) -> bool:
        """Existing DB'lerde quiz_sessions şemasını Option A için günceller.
        - topic_id: NULLable yapılır
        - selection_scope ENUM('topic','unit','subject','grade','global') DEFAULT 'topic' eklenir
        - idx_sessions_scope indeksi eklenir
        """
        try:
            with self.db as conn:
                # Make topic_id nullable if not already
                try:
                    conn.cursor.execute(
                        "ALTER TABLE quiz_sessions MODIFY COLUMN topic_id INT NULL"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

                # Add selection_scope if missing
                conn.cursor.execute("SHOW COLUMNS FROM quiz_sessions LIKE 'selection_scope'")
                if not conn.cursor.fetchone():
                    try:
                        conn.cursor.execute(
                            """
                            ALTER TABLE quiz_sessions
                            ADD COLUMN selection_scope ENUM('topic','unit','subject','grade','global')
                            NOT NULL DEFAULT 'topic'
                            AFTER topic_id
                            """
                        )
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # Ensure index on selection_scope
                try:
                    conn.cursor.execute(
                        "SHOW INDEX FROM quiz_sessions WHERE Key_name = %s",
                        ("idx_sessions_scope",)
                    )
                    if not conn.cursor.fetchone():
                        conn.cursor.execute(
                            "CREATE INDEX idx_sessions_scope ON quiz_sessions (selection_scope)"
                        )
                        conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False
    def _seed_grades_1_to_12_if_empty(self) -> bool:
        """Grades tablosu boşsa 1'den 12'ye kadar sınıfları sabit grade_id ile ekler."""
        try:
            with self.db as conn:
                conn.cursor.execute("SELECT COUNT(*) AS cnt FROM grades")
                result = conn.cursor.fetchone()
                count = (result or {}).get('cnt', 0)
                if count and count > 0:
                    return True

                # Boşsa 1..12 ekle (explicit grade_id)
                values = []
                for i in range(1, 13):
                    name = f"{i}. Sınıf"
                    desc = f"{name} seviyesi"
                    # Escape quotes just in case
                    name_esc = name.replace("'", "''")
                    desc_esc = desc.replace("'", "''")
                    values.append(f"({i}, '{name_esc}', '{desc_esc}', 1)")

                sql = f"""
INSERT INTO grades (grade_id, grade_name, description, is_active) VALUES
{', '.join(values)}
ON DUPLICATE KEY UPDATE
    grade_name = VALUES(grade_name),
    description = VALUES(description),
    is_active = VALUES(is_active);
"""
                conn.cursor.execute(sql)
                conn.connection.commit()
                return True
        except Exception:
            return False

    def _migrate_units_schema(self) -> bool:
        """Existing DB'lerde units şemasını yeni yapıya dönüştürür.
        - id -> unit_id (PK)
        - name -> unit_name
        - drop name_id
        - indexes/unique: unique (subject_id, unit_name), idx on unit_name, subject_id, is_active
        - FKs: topics.unit_id -> units.unit_id, quiz_sessions.unit_id -> units.unit_id
        """
        try:
            with self.db as conn:
                # 1) Kolon adlarını dönüştür
                # id -> unit_id
                conn.cursor.execute("SHOW COLUMNS FROM units LIKE 'unit_id'")
                has_unit_id = bool(conn.cursor.fetchone())
                if not has_unit_id:
                    conn.cursor.execute("SHOW COLUMNS FROM units LIKE 'id'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE units CHANGE COLUMN id unit_id INT AUTO_INCREMENT PRIMARY KEY"
                        )
                        conn.connection.commit()

                # name -> unit_name
                conn.cursor.execute("SHOW COLUMNS FROM units LIKE 'unit_name'")
                has_unit_name = bool(conn.cursor.fetchone())
                if not has_unit_name:
                    conn.cursor.execute("SHOW COLUMNS FROM units LIKE 'name'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE units CHANGE COLUMN name unit_name VARCHAR(200) NOT NULL"
                        )
                        conn.connection.commit()

                # name_id drop (if exists)
                conn.cursor.execute("SHOW COLUMNS FROM units LIKE 'name_id'")
                if conn.cursor.fetchone():
                    try:
                        conn.cursor.execute("ALTER TABLE units DROP COLUMN name_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # 2) Eski index/unique'leri temizle, yenilerini kur
                def drop_units_index_if_exists(idx_name: str):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM units WHERE Key_name = %s",
                            (idx_name,)
                        )
                        if conn.cursor.fetchone():
                            conn.cursor.execute(f"DROP INDEX {idx_name} ON units")
                            conn.connection.commit()
                    except MySQLError:
                        pass

                for idx in [
                    'idx_units_name',
                    'idx_units_name_id',
                    'idx_units_subject',
                    'idx_units_active',
                    'unique_unit_per_subject',
                    'unique_name_subject'
                ]:
                    drop_units_index_if_exists(idx)

                def ensure_units_index(idx_name: str, expr: str, unique: bool = False):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM units WHERE Key_name = %s",
                            (idx_name,)
                        )
                        exists = bool(conn.cursor.fetchone())
                        if not exists:
                            if unique:
                                conn.cursor.execute(
                                    f"ALTER TABLE units ADD CONSTRAINT {idx_name} UNIQUE ({expr})"
                                )
                            else:
                                conn.cursor.execute(
                                    f"CREATE INDEX {idx_name} ON units ({expr})"
                                )
                            conn.connection.commit()
                    except MySQLError:
                        pass

                ensure_units_index('idx_units_name', 'unit_name')
                ensure_units_index('idx_units_subject', 'subject_id')
                ensure_units_index('idx_units_active', 'is_active')
                ensure_units_index('unique_unit_per_subject', 'subject_id, unit_name', unique=True)

                # 3) Dış anahtarları güncelle: topics.unit_id ve quiz_sessions.unit_id
                def drop_fk_if_exists(table: str, column: str, referenced_table: str):
                    try:
                        conn.cursor.execute(
                            """
                            SELECT CONSTRAINT_NAME 
                            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                            WHERE TABLE_SCHEMA = DATABASE()
                              AND TABLE_NAME = %s
                              AND COLUMN_NAME = %s
                              AND REFERENCED_TABLE_NAME = %s
                            """,
                            (table, column, referenced_table)
                        )
                        row = conn.cursor.fetchone()
                        if row and row.get('CONSTRAINT_NAME'):
                            fk_name = row['CONSTRAINT_NAME']
                            try:
                                conn.cursor.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}")
                                conn.connection.commit()
                            except MySQLError:
                                pass
                    except MySQLError:
                        pass

                # Drop existing FKs (if any)
                drop_fk_if_exists('topics', 'unit_id', 'units')
                drop_fk_if_exists('quiz_sessions', 'unit_id', 'units')

                # Recreate FKs to units(unit_id)
                try:
                    conn.cursor.execute(
                        "ALTER TABLE topics ADD CONSTRAINT fk_topics_unit FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

                try:
                    conn.cursor.execute(
                        "ALTER TABLE quiz_sessions ADD CONSTRAINT fk_quiz_sessions_unit FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE SET NULL"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False

    def _drop_table(self, table_name: str) -> bool:
        """Tabloyu siler."""
        return self._execute_sql(f"DROP TABLE IF EXISTS {table_name}")

    def _populate_from_json(self):
        """JSON dosyalarından verileri yükler ve tablolara ekler."""
        try:
            # JSON verilerini işle
            grades_sql, subjects_sql, units_sql, topics_sql = self.json_loader.process_all_data()
            
            # Grades tablosunu doldur
            if grades_sql:
                self._execute_sql(grades_sql)
            
            # Subjects tablosunu doldur (grade_id_map gerektirir)
            grade_id_map = self.json_loader.get_grade_id_map(self.db)
            
            if grade_id_map:
                subjects_sql = self.json_loader.generate_subjects_sql(grade_id_map)
                if subjects_sql:
                    self._execute_sql(subjects_sql)
            
            # Units tablosunu doldur (subject_id_map gerektirir)
            subject_id_map = self.json_loader.get_subject_id_map(self.db)
            
            if subject_id_map:
                units_sql = self.json_loader.generate_units_sql(subject_id_map)
                if units_sql:
                    self._execute_sql(units_sql)
            
            # Topics tablosunu doldur (unit_id_map gerektirir)
            unit_id_map = self.json_loader.get_unit_id_map(self.db)
            
            if unit_id_map:
                topics_sql = self.json_loader.generate_topics_sql(unit_id_map)
                if topics_sql:
                    self._execute_sql(topics_sql)
            
            return True
            
        except Exception:
            return False

    def drop_all_tables(self):
        """Tüm tabloları temizler."""
        try:
            # Foreign key constraint'leri devre dışı bırak
            self._execute_sql("SET FOREIGN_KEY_CHECKS = 0")
            
            # Tabloları sil (child tablolar önce)
            tables = [
                'quiz_session_questions',
                'quiz_sessions',
                'question_options',
                'questions', 
                'topics',
                'units',
                'subjects',
                'grades',
                'users',
                'chat_messages',
                'chat_sessions'
            ]
            
            for table in tables:
                self._drop_table(table)
            
            # Foreign key constraint'leri tekrar etkinleştir
            self._execute_sql("SET FOREIGN_KEY_CHECKS = 1")
            return True
            
        except MySQLError:
            return False

    def create_tables(self):
        """Tüm tabloları oluşturur."""
        try:
            # Tabloları sırayla oluştur
            for table_name in self.table_order:
                if table_name not in self.table_schemas:
                    return False
                
                table_sql, sample_data = self.table_schemas[table_name]
                if not self._create_table(table_name, table_sql, sample_data):
                    return False

            # İlk çalıştırmada sınıfları seed et (1..12)
            if not self._seed_grades_1_to_12_if_empty():
                return False

            # JSON verilerini yükle (gerekirse açıklamaları/dersleri ekler)
            if not self._populate_from_json():
                return False

            return True
            
        except MySQLError:
            return False

    def check_tables_exist(self) -> bool:
        """Tabloların mevcut olup olmadığını kontrol eder."""
        try:
            required_tables = [
                'grades', 'subjects', 'units', 'topics', 'questions', 
                'question_options', 'users', 'quiz_sessions', 'quiz_session_questions',
                'chat_sessions', 'chat_messages'
            ]
            
            with self.db as conn:
                for table in required_tables:
                    try:
                        conn.cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not conn.cursor.fetchone():
                            return False
                    except MySQLError:
                        return False
            
            return True
            
        except MySQLError:
            return False

    def _migrate_grades_name_column(self) -> bool:
        """Existing DB'lerde grades.name kolonunu grades.grade_name olarak değiştirir."""
        try:
            with self.db as conn:
                # Kolon mevcut mu kontrol et
                conn.cursor.execute("SHOW COLUMNS FROM grades LIKE 'name'")
                if conn.cursor.fetchone():
                    # Kolonu yeniden adlandır
                    conn.cursor.execute(
                        "ALTER TABLE grades CHANGE COLUMN name grade_name VARCHAR(100) NOT NULL"
                    )
                    conn.connection.commit()
            return True
        except Exception:
            return False

    def _migrate_subjects_schema(self) -> bool:
        """Existing DB'lerde subjects şemasını doğru (grade tabanlı) yapıya dönüştürür.
        - id -> subject_id (PK)
        - name -> subject_name
        - drop name_id
        - ensure grade_id (FK -> grades.grade_id), drop unit_id if exists
        - indexes/unique: unique (grade_id, subject_name), idx on subject_name, grade_id, is_active
        - units.subject_id FK -> subjects.subject_id (mevcut durumda korunur)
        """
        try:
            with self.db as conn:
                # 1) Kolon adlarını dönüştür
                # id -> subject_id
                conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'subject_id'")
                has_subject_id = bool(conn.cursor.fetchone())
                if not has_subject_id:
                    conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'id'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE subjects CHANGE COLUMN id subject_id INT AUTO_INCREMENT PRIMARY KEY"
                        )
                        conn.connection.commit()

                # name -> subject_name
                conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'subject_name'")
                has_subject_name = bool(conn.cursor.fetchone())
                if not has_subject_name:
                    conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'name'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE subjects CHANGE COLUMN name subject_name VARCHAR(200) NOT NULL"
                        )
                        conn.connection.commit()

                # name_id drop
                conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'name_id'")
                if conn.cursor.fetchone():
                    try:
                        conn.cursor.execute("ALTER TABLE subjects DROP COLUMN name_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # grade_id ekle (yoksa); geçici olarak NULL olabilir
                conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'grade_id'")
                if not conn.cursor.fetchone():
                    try:
                        conn.cursor.execute("ALTER TABLE subjects ADD COLUMN grade_id INT NULL AFTER subject_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # unit_id varsa kaldırmadan önce ona bağlı indexleri temizle, sonra kolonu kaldır
                conn.cursor.execute("SHOW COLUMNS FROM subjects LIKE 'unit_id'")
                if conn.cursor.fetchone():
                    # unit tabanlı index/unique'leri düşür
                    def drop_index_if_exists_local(idx_name: str):
                        try:
                            conn.cursor.execute(
                                "SHOW INDEX FROM subjects WHERE Key_name = %s",
                                (idx_name,)
                            )
                            if conn.cursor.fetchone():
                                conn.cursor.execute(f"DROP INDEX {idx_name} ON subjects")
                                conn.connection.commit()
                        except MySQLError:
                            pass

                    for idx in [
                        'idx_subjects_unit',
                        'unique_subject_per_unit'
                    ]:
                        drop_index_if_exists_local(idx)

                    try:
                        conn.cursor.execute("ALTER TABLE subjects DROP COLUMN unit_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # 2) Eski index/unique'leri temizle, yenilerini kur
                def drop_index_if_exists(idx_name: str):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM subjects WHERE Key_name = %s",
                            (idx_name,)
                        )
                        if conn.cursor.fetchone():
                            conn.cursor.execute(f"DROP INDEX {idx_name} ON subjects")
                            conn.connection.commit()
                    except MySQLError:
                        pass

                # Muhtemel eski index/unique isimleri
                for idx in [
                    'idx_subjects_name_id',
                    'unique_subject_grade',
                    'unique_name_grade',
                    'idx_subjects_grade',
                    'idx_subjects_unit',
                    'unique_subject_per_unit',
                    'unique_subject_per_grade'
                ]:
                    drop_index_if_exists(idx)

                # Yeni index/unique'leri yoksa ekle
                def ensure_index(idx_name: str, expr: str, unique: bool = False):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM subjects WHERE Key_name = %s",
                            (idx_name,)
                        )
                        exists = bool(conn.cursor.fetchone())
                        if not exists:
                            if unique:
                                conn.cursor.execute(
                                    f"ALTER TABLE subjects ADD CONSTRAINT {idx_name} UNIQUE ({expr})"
                                )
                            else:
                                conn.cursor.execute(
                                    f"CREATE INDEX {idx_name} ON subjects ({expr})"
                                )
                            conn.connection.commit()
                    except MySQLError:
                        pass

                ensure_index('idx_subjects_name', 'subject_name')
                ensure_index('idx_subjects_grade', 'grade_id')
                ensure_index('idx_subjects_active', 'is_active')
                ensure_index('unique_subject_per_grade', 'grade_id, subject_name', unique=True)

                # 3) subjects.grade_id -> grades.grade_id FK'sini garanti altına al
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'subjects'
                          AND COLUMN_NAME = 'grade_id'
                          AND REFERENCED_TABLE_NAME = 'grades'
                        """
                    )
                    row = conn.cursor.fetchone()
                    has_fk = bool(row and row.get('CONSTRAINT_NAME'))
                except MySQLError:
                    has_fk = True  # emin olamıyorsak ikinci eklemeyi denememek için

                if not has_fk:
                    try:
                        conn.cursor.execute(
                            "ALTER TABLE subjects ADD CONSTRAINT fk_subjects_grade FOREIGN KEY (grade_id) REFERENCES grades(grade_id) ON DELETE CASCADE"
                        )
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # 4) units.subject_id dış anahtarını subjects.subject_id'ye sabitle (varsa koru/ekle)
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'units'
                          AND COLUMN_NAME = 'subject_id'
                          AND REFERENCED_TABLE_NAME = 'subjects'
                        """
                    )
                    row = conn.cursor.fetchone()
                    if row and row.get('CONSTRAINT_NAME'):
                        fk_name = row['CONSTRAINT_NAME']
                        try:
                            conn.cursor.execute(f"ALTER TABLE units DROP FOREIGN KEY {fk_name}")
                            conn.connection.commit()
                        except MySQLError:
                            pass
                except MySQLError:
                    pass

                # FK ekle (zaten varsa sessizce geç)
                try:
                    conn.cursor.execute(
                        "ALTER TABLE units ADD CONSTRAINT fk_units_subject FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False

    def _migrate_topics_schema(self) -> bool:
        """Existing DB'lerde topics şemasını yeni yapıya dönüştürür.
        - id -> topic_id (PK)
        - name -> topic_name
        - drop name_id
        - indexes/unique: unique (unit_id, topic_name), idx on topic_name, unit_id, is_active
        - FK: topics.unit_id -> units.unit_id
        """
        try:
            with self.db as conn:
                # id -> topic_id
                conn.cursor.execute("SHOW COLUMNS FROM topics LIKE 'topic_id'")
                has_topic_id = bool(conn.cursor.fetchone())
                if not has_topic_id:
                    conn.cursor.execute("SHOW COLUMNS FROM topics LIKE 'id'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE topics CHANGE COLUMN id topic_id INT AUTO_INCREMENT PRIMARY KEY"
                        )
                        conn.connection.commit()

                # name -> topic_name
                conn.cursor.execute("SHOW COLUMNS FROM topics LIKE 'topic_name'")
                has_topic_name = bool(conn.cursor.fetchone())
                if not has_topic_name:
                    conn.cursor.execute("SHOW COLUMNS FROM topics LIKE 'name'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE topics CHANGE COLUMN name topic_name VARCHAR(200) NOT NULL"
                        )
                        conn.connection.commit()

                # name_id drop (if exists)
                conn.cursor.execute("SHOW COLUMNS FROM topics LIKE 'name_id'")
                if conn.cursor.fetchone():
                    try:
                        conn.cursor.execute("ALTER TABLE topics DROP COLUMN name_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # Drop old indexes if exist
                def drop_topics_index(idx_name: str):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM topics WHERE Key_name = %s",
                            (idx_name,)
                        )
                        if conn.cursor.fetchone():
                            conn.cursor.execute(f"DROP INDEX {idx_name} ON topics")
                            conn.connection.commit()
                    except MySQLError:
                        pass

                for idx in [
                    'idx_topics_name',    # on old name or new name (we will recreate)
                    'idx_topics_name_id',
                    'idx_topics_unit',    # will recreate
                    'idx_topics_active',  # will recreate
                    'unique_topic_unit',
                    'unique_topic_per_unit'
                ]:
                    drop_topics_index(idx)

                # Ensure new indexes/unique
                def ensure_topics_index(idx_name: str, expr: str, unique: bool = False):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM topics WHERE Key_name = %s",
                            (idx_name,)
                        )
                        exists = bool(conn.cursor.fetchone())
                        if not exists:
                            if unique:
                                conn.cursor.execute(
                                    f"ALTER TABLE topics ADD CONSTRAINT {idx_name} UNIQUE ({expr})"
                                )
                            else:
                                conn.cursor.execute(
                                    f"CREATE INDEX {idx_name} ON topics ({expr})"
                                )
                            conn.connection.commit()
                    except MySQLError:
                        pass

                ensure_topics_index('idx_topics_name', 'topic_name')
                ensure_topics_index('idx_topics_unit', 'unit_id')
                ensure_topics_index('idx_topics_active', 'is_active')
                ensure_topics_index('unique_topic_per_unit', 'unit_id, topic_name', unique=True)

                # Ensure FK to units(unit_id)
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'topics'
                          AND COLUMN_NAME = 'unit_id'
                          AND REFERENCED_TABLE_NAME = 'units'
                        """
                    )
                    row = conn.cursor.fetchone()
                    if row and row.get('CONSTRAINT_NAME'):
                        fk_name = row['CONSTRAINT_NAME']
                        try:
                            conn.cursor.execute(f"ALTER TABLE topics DROP FOREIGN KEY {fk_name}")
                            conn.connection.commit()
                        except MySQLError:
                            pass
                except MySQLError:
                    pass

                try:
                    conn.cursor.execute(
                        "ALTER TABLE topics ADD CONSTRAINT fk_topics_unit FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False

    def _migrate_questions_schema(self) -> bool:
        """Existing DB'lerde questions şemasını yeni yapıya dönüştürür.
        - id -> question_id (PK)
        - name -> question_text
        - drop name_id
        - indexes: ensure idx on topic_id, difficulty_level, question_type, is_active
        - FK: questions.topic_id -> topics.topic_id
        """
        try:
            with self.db as conn:
                # 0) PK'yi id -> question_id olarak yeniden adlandır (FK çakışmalarını ele al)
                conn.cursor.execute("SHOW COLUMNS FROM questions LIKE 'question_id'")
                has_qid = bool(conn.cursor.fetchone())
                if not has_qid:
                    # Önce questions.id'ye referans veren FKs'leri düşür
                    def drop_fk_if_exists(table: str, column: str, referenced_table: str):
                        try:
                            conn.cursor.execute(
                                """
                                SELECT CONSTRAINT_NAME 
                                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                                WHERE TABLE_SCHEMA = DATABASE()
                                  AND TABLE_NAME = %s
                                  AND COLUMN_NAME = %s
                                  AND REFERENCED_TABLE_NAME = %s
                                """,
                                (table, column, referenced_table)
                            )
                            row = conn.cursor.fetchone()
                            if row and row.get('CONSTRAINT_NAME'):
                                fk_name = row['CONSTRAINT_NAME']
                                try:
                                    conn.cursor.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}")
                                    conn.connection.commit()
                                except MySQLError:
                                    pass
                        except MySQLError:
                            pass
                    # Child tablolar: question_options, quiz_session_questions
                    drop_fk_if_exists('question_options', 'question_id', 'questions')
                    drop_fk_if_exists('quiz_session_questions', 'question_id', 'questions')

                    # PK kolonu yeniden adlandır
                    conn.cursor.execute("SHOW COLUMNS FROM questions LIKE 'id'")
                    if conn.cursor.fetchone():
                        try:
                            conn.cursor.execute(
                                "ALTER TABLE questions CHANGE COLUMN id question_id INT AUTO_INCREMENT PRIMARY KEY"
                            )
                            conn.connection.commit()
                        except MySQLError:
                            pass

                    # Child FKs'leri question_id'ye yeniden oluştur
                    try:
                        conn.cursor.execute(
                            "ALTER TABLE question_options ADD CONSTRAINT fk_question_options_question FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE"
                        )
                        conn.connection.commit()
                    except MySQLError:
                        pass

                    try:
                        conn.cursor.execute(
                            "ALTER TABLE quiz_session_questions ADD CONSTRAINT fk_session_questions_question FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE"
                        )
                        conn.connection.commit()
                    except MySQLError:
                        pass
                # name -> question_text
                conn.cursor.execute("SHOW COLUMNS FROM questions LIKE 'question_text'")
                has_qtext = bool(conn.cursor.fetchone())
                if not has_qtext:
                    conn.cursor.execute("SHOW COLUMNS FROM questions LIKE 'name'")
                    if conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE questions CHANGE COLUMN name question_text TEXT NOT NULL"
                        )
                        conn.connection.commit()

                # name_id drop (if exists)
                conn.cursor.execute("SHOW COLUMNS FROM questions LIKE 'name_id'")
                if conn.cursor.fetchone():
                    try:
                        conn.cursor.execute("ALTER TABLE questions DROP COLUMN name_id")
                        conn.connection.commit()
                    except MySQLError:
                        pass

                # Drop old indexes if exist
                def drop_questions_index(idx_name: str):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM questions WHERE Key_name = %s",
                            (idx_name,)
                        )
                        if conn.cursor.fetchone():
                            conn.cursor.execute(f"DROP INDEX {idx_name} ON questions")
                            conn.connection.commit()
                    except MySQLError:
                        pass

                for idx in [
                    'idx_questions_name',
                    'idx_questions_name_id',
                    'unique_question_per_topic'
                ]:
                    drop_questions_index(idx)

                # Ensure new indexes
                def ensure_questions_index(idx_name: str, expr: str):
                    try:
                        conn.cursor.execute(
                            "SHOW INDEX FROM questions WHERE Key_name = %s",
                            (idx_name,)
                        )
                        exists = bool(conn.cursor.fetchone())
                        if not exists:
                            conn.cursor.execute(
                                f"CREATE INDEX {idx_name} ON questions ({expr})"
                            )
                            conn.connection.commit()
                    except MySQLError:
                        pass

                ensure_questions_index('idx_questions_topic', 'topic_id')
                ensure_questions_index('idx_questions_difficulty', 'difficulty_level')
                ensure_questions_index('idx_questions_type', 'question_type')
                ensure_questions_index('idx_questions_active', 'is_active')

                # Ensure FK to topics(topic_id)
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'questions'
                          AND COLUMN_NAME = 'topic_id'
                          AND REFERENCED_TABLE_NAME = 'topics'
                        """
                    )
                    row = conn.cursor.fetchone()
                    if row and row.get('CONSTRAINT_NAME'):
                        fk_name = row['CONSTRAINT_NAME']
                        try:
                            conn.cursor.execute(f"ALTER TABLE questions DROP FOREIGN KEY {fk_name}")
                            conn.connection.commit()
                        except MySQLError:
                            pass
                except MySQLError:
                    pass

                try:
                    conn.cursor.execute(
                        "ALTER TABLE questions ADD CONSTRAINT fk_questions_topic FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False

    def _migrate_question_options_schema(self) -> bool:
        """Existing DB'lerde question_options şemasını yeni yapıya dönüştürür.
        - id -> option_id (PK)
        - name -> option_text
        - drop name_id, option_order, is_active
        - ensure created_at, updated_at
        - indexes: idx_options_question (question_id), idx_options_correct (is_correct)
        - FKs: question_options.question_id -> questions.question_id
               quiz_session_questions.user_answer_option_id -> question_options.option_id
        """
        try:
            with self.db as conn:
                # 1) PK id -> option_id
                conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'option_id'")
                has_oid = bool(conn.cursor.fetchone())
                if not has_oid:
                    # Drop FK from quiz_session_questions.user_answer_option_id -> question_options.id if exists
                    try:
                        conn.cursor.execute(
                            """
                            SELECT CONSTRAINT_NAME 
                            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                            WHERE TABLE_SCHEMA = DATABASE()
                              AND TABLE_NAME = 'quiz_session_questions'
                              AND COLUMN_NAME = 'user_answer_option_id'
                              AND REFERENCED_TABLE_NAME = 'question_options'
                            """
                        )
                        row = conn.cursor.fetchone()
                        if row and row.get('CONSTRAINT_NAME'):
                            fk_name = row['CONSTRAINT_NAME']
                            try:
                                conn.cursor.execute(f"ALTER TABLE quiz_session_questions DROP FOREIGN KEY {fk_name}")
                                conn.connection.commit()
                            except MySQLError:
                                pass
                    except MySQLError:
                        pass
                    # Rename id -> option_id
                    conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'id'")
                    if conn.cursor.fetchone():
                        try:
                            conn.cursor.execute(
                                "ALTER TABLE question_options CHANGE COLUMN id option_id INT AUTO_INCREMENT PRIMARY KEY"
                            )
                            conn.connection.commit()
                        except MySQLError:
                            pass

                # 2) name -> option_text
                conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'option_text'")
                has_text = bool(conn.cursor.fetchone())
                if not has_text:
                    conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'name'")
                    if conn.cursor.fetchone():
                        try:
                            conn.cursor.execute(
                                "ALTER TABLE question_options CHANGE COLUMN name option_text TEXT NOT NULL"
                            )
                            conn.connection.commit()
                        except MySQLError:
                            pass

                # 3) Drop legacy columns
                for legacy_col in ['name_id', 'option_order', 'is_active']:
                    try:
                        conn.cursor.execute(f"SHOW COLUMNS FROM question_options LIKE '{legacy_col}'")
                        if conn.cursor.fetchone():
                            try:
                                conn.cursor.execute(f"ALTER TABLE question_options DROP COLUMN {legacy_col}")
                                conn.connection.commit()
                            except MySQLError:
                                pass
                    except MySQLError:
                        pass

                # 4) Ensure timestamp columns
                try:
                    conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'created_at'")
                    if not conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE question_options ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                        )
                        conn.connection.commit()
                except MySQLError:
                    pass
                try:
                    conn.cursor.execute("SHOW COLUMNS FROM question_options LIKE 'updated_at'")
                    if not conn.cursor.fetchone():
                        conn.cursor.execute(
                            "ALTER TABLE question_options ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                        )
                        conn.connection.commit()
                except MySQLError:
                    pass

                # 5) Ensure indexes
                def ensure_options_index(idx_name: str, expr: str):
                    try:
                        conn.cursor.execute("SHOW INDEX FROM question_options WHERE Key_name = %s", (idx_name,))
                        if not conn.cursor.fetchone():
                            conn.cursor.execute(f"CREATE INDEX {idx_name} ON question_options ({expr})")
                            conn.connection.commit()
                    except MySQLError:
                        pass

                ensure_options_index('idx_options_question', 'question_id')
                ensure_options_index('idx_options_correct', 'is_correct')

                # 6) Ensure FK to questions(question_id)
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'question_options'
                          AND COLUMN_NAME = 'question_id'
                          AND REFERENCED_TABLE_NAME = 'questions'
                        """
                    )
                    row = conn.cursor.fetchone()
                    if row and row.get('CONSTRAINT_NAME'):
                        fk_name = row['CONSTRAINT_NAME']
                        try:
                            conn.cursor.execute(f"ALTER TABLE question_options DROP FOREIGN KEY {fk_name}")
                            conn.connection.commit()
                        except MySQLError:
                            pass
                except MySQLError:
                    pass
                try:
                    conn.cursor.execute(
                        "ALTER TABLE question_options ADD CONSTRAINT fk_question_options_question FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

                # 7) Ensure FK from quiz_session_questions.user_answer_option_id -> question_options.option_id
                try:
                    conn.cursor.execute(
                        """
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'quiz_session_questions'
                          AND COLUMN_NAME = 'user_answer_option_id'
                          AND REFERENCED_TABLE_NAME = 'question_options'
                        """
                    )
                    row = conn.cursor.fetchone()
                    if row and row.get('CONSTRAINT_NAME'):
                        fk_name = row['CONSTRAINT_NAME']
                        try:
                            conn.cursor.execute(f"ALTER TABLE quiz_session_questions DROP FOREIGN KEY {fk_name}")
                            conn.connection.commit()
                        except MySQLError:
                            pass
                except MySQLError:
                    pass
                try:
                    conn.cursor.execute(
                        "ALTER TABLE quiz_session_questions ADD CONSTRAINT fk_session_questions_answer_option FOREIGN KEY (user_answer_option_id) REFERENCES question_options(option_id) ON DELETE SET NULL"
                    )
                    conn.connection.commit()
                except MySQLError:
                    pass

            return True
        except Exception:
            return False

    def run_migrations(self):
        """Ana migration işlemini çalıştırır.
        
        Returns:
            bool: Migration işleminin başarılı olup olmadığı
        """
        try:
            # Tabloların mevcut olup olmadığını kontrol et
            if self.check_tables_exist():
                # Mevcut veritabanı için şema migrasyonlarını uygula
                self._migrate_grades_name_column()
                self._migrate_subjects_schema()
                self._migrate_units_schema()
                self._migrate_topics_schema()
                self._migrate_questions_schema()
                self._migrate_question_options_schema()
                self._migrate_quiz_sessions_schema()
                # Mevcut veritabanında da JSON'dan curriculum verilerini senkronize et
                # 1..12 sınıfları seed et (boşsa) ve JSON verilerini yükle
                if not self._seed_grades_1_to_12_if_empty():
                    return False
                if not self._populate_from_json():
                    return False
                return True
            
            # Tabloları oluştur
            if not self.create_tables():
                return False
            
            return True
            
        except Exception:
            return False

    def force_recreate(self) -> bool:
        """Tabloları zorla yeniden oluşturur.
        
        Returns:
            bool: Yeniden oluşturma işleminin başarılı olup olmadığı
        """
        try:
            # Tabloları sil
            if not self.drop_all_tables():
                return False
            
            # Yeni tabloları oluştur
            if not self.create_tables():
                return False
                
            return True
            
        except Exception:
            return False

    def get_table_info(self) -> Dict[str, int]:
        """Tablolardaki kayıt sayılarını döner.
        
        Returns:
            Dict[str, int]: Tablo adlarını kayıt sayılarıyla eşleştiren sözlük
        """
        try:
            table_counts = {}
            with self.db as conn:
                for table_name in self.table_order:
                    try:
                        conn.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        result = conn.cursor.fetchone()
                        table_counts[table_name] = result['count'] if result else 0
                    except MySQLError:
                        table_counts[table_name] = 0
            
            return table_counts
            
        except Exception:
            return {}

# =============================================================================
# DOĞRUDAN ÇALIŞTIRMA
# =============================================================================
if __name__ == "__main__":
    migrations = DatabaseMigrations()
    migrations.run_migrations()