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
    QUESTIONS_TABLE_SQL, QUESTIONS_SAMPLE_DATA,
    QUESTION_OPTIONS_TABLE_SQL, QUESTION_OPTIONS_SAMPLE_DATA,
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
            'questions': (QUESTIONS_TABLE_SQL, QUESTIONS_SAMPLE_DATA),
            'question_options': (QUESTION_OPTIONS_TABLE_SQL, QUESTION_OPTIONS_SAMPLE_DATA),
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
        except MySQLError as e:
            print(f"❌ SQL hatası: {e}")
            return False

    def _create_table(self, table_name: str, table_sql: str, sample_data: str) -> bool:
        """Tabloyu oluşturur ve örnek verileri ekler."""
        try:
            # Tabloyu oluştur
            if not self._execute_sql(table_sql):
                return False
            
            # Örnek verileri ekle (eğer varsa)
            if sample_data:
                if not self._execute_sql(sample_data):
                    print(f"   ⚠️  {table_name} için örnek veriler eklenemedi")
            
            return True
            
        except Exception as e:
            print(f"❌ {table_name} tablosu oluşturma hatası: {e}")
            return False

    def _drop_table(self, table_name: str) -> bool:
        """Tabloyu siler."""
        return self._execute_sql(f"DROP TABLE IF EXISTS {table_name}")

    def _populate_from_json(self):
        """JSON dosyalarından verileri yükler ve tablolara ekler."""
        try:
            print("📚 JSON verileri işleniyor...")
            
            # JSON verilerini işle
            grades_sql, subjects_sql, units_sql, topics_sql = self.json_loader.process_all_data()
            
            # Grades tablosunu doldur
            if grades_sql:
                print("📋 Grades tablosu JSON verileriyle dolduruluyor...")
                if not self._execute_sql(grades_sql):
                    print("❌ Grades tablosu doldurulamadı!")
                    return False
                print("   ✅ Grades tablosu başarıyla dolduruldu")
            
            # Subjects tablosunu doldur (grade_id_map gerektirir)
            print("📋 Subjects tablosu JSON verileriyle dolduruluyor...")
            grade_id_map = self.json_loader.get_grade_id_map(self.db)
            
            if grade_id_map:
                subjects_sql = self.json_loader.generate_subjects_sql(grade_id_map)
                if subjects_sql:
                    if not self._execute_sql(subjects_sql):
                        print("❌ Subjects tablosu doldurulamadı!")
                        return False
                    print("   ✅ Subjects tablosu başarıyla dolduruldu")
                else:
                    print("   ⚠️  Subjects için veri bulunamadı")
            else:
                print("   ⚠️  Grade ID map oluşturulamadı")
                return False
            
            # Units tablosunu doldur (subject_id_map gerektirir)
            print("📋 Units tablosu JSON verileriyle dolduruluyor...")
            subject_id_map = self.json_loader.get_subject_id_map(self.db)
            
            if subject_id_map:
                units_sql = self.json_loader.generate_units_sql(subject_id_map)
                if units_sql:
                    if not self._execute_sql(units_sql):
                        print("❌ Units tablosu doldurulamadı!")
                        return False
                    print("   ✅ Units tablosu başarıyla dolduruldu")
                else:
                    print("   ⚠️  Units için veri bulunamadı")
            else:
                print("   ⚠️  Subject ID map oluşturulamadı")
                return False
            
            # Topics tablosunu doldur (unit_id_map gerektirir)
            print("📋 Topics tablosu JSON verileriyle dolduruluyor...")
            unit_id_map = self.json_loader.get_unit_id_map(self.db)
            
            if unit_id_map:
                topics_sql = self.json_loader.generate_topics_sql(unit_id_map)
                if topics_sql:
                    if not self._execute_sql(topics_sql):
                        print("❌ Topics tablosu doldurulamadı!")
                        return False
                    print("   ✅ Topics tablosu başarıyla dolduruldu")
                else:
                    print("   ⚠️  Topics için veri bulunamadı")
            else:
                print("   ⚠️  Unit ID map oluşturulamadı")
            
            return True
            
        except Exception as e:
            print(f"❌ JSON veri yükleme hatası: {e}")
            return False

    def drop_all_tables(self):
        """Tüm tabloları temizler."""
        try:
            print("🧹 Tüm tablolar temizleniyor...")
            
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
                'users'
            ]
            
            for table in tables:
                if self._drop_table(table):
                    print(f"   ✅ {table} tablosu silindi")
                else:
                    print(f"   ⚠️  {table} tablosu silinemedi")
            
            # Foreign key constraint'leri tekrar etkinleştir
            self._execute_sql("SET FOREIGN_KEY_CHECKS = 1")
            
            print("✅ Tablo temizleme tamamlandı!")
            
        except MySQLError as e:
            print(f"❌ Tablo temizleme hatası: {e}")
            raise

    def create_tables(self):
        """Tüm tabloları oluşturur."""
        try:
            print("🚀 Veritabanı tabloları oluşturuluyor...")
            
            # Tabloları sırayla oluştur
            table_descriptions = {
                'grades': 'Grades (Sınıflar)',
                'subjects': 'Subjects (Dersler)',
                'units': 'Units (Üniteler)',
                'topics': 'Topics (Konular)',
                'questions': 'Questions (Sorular)',
                'question_options': 'Question Options (Soru Seçenekleri)',
                'users': 'Users (Kullanıcılar)'
            }
            
            for table_name in self.table_order:
                if table_name not in self.table_schemas:
                    print(f"❌ {table_name} şeması bulunamadı!")
                    return False
                
                table_sql, sample_data = self.table_schemas[table_name]
                description = table_descriptions.get(table_name, table_name)
                
                print(f"📋 {description} oluşturuluyor...")
                if not self._create_table(table_name, table_sql, sample_data):
                    print(f"❌ {description} tablosu oluşturulamadı!")
                    return False
                print(f"   ✅ {description} başarıyla oluşturuldu")

            # JSON verilerini yükle
            if not self._populate_from_json():
                print("❌ JSON verileri yüklenemedi!")
                return False

            print("✅ Tüm tablolar başarıyla oluşturuldu!")
            return True
            
        except MySQLError as e:
            print(f"❌ Tablo oluşturma hatası: {e}")
            return False

    def check_tables_exist(self) -> bool:
        """Tabloların mevcut olup olmadığını kontrol eder."""
        try:
            required_tables = [
                'grades', 'subjects', 'units', 'topics', 'questions', 
                'question_options', 'users', 'quiz_sessions', 'quiz_session_questions'
            ]
            
            with self.db as conn:
                for table in required_tables:
                    try:
                        conn.cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not conn.cursor.fetchone():
                            print(f"❌ Tablo bulunamadı: {table}")
                            return False
                    except MySQLError as e:
                        print(f"❌ Tablo kontrol hatası ({table}): {e}")
                        return False
            
            print("✅ Tüm gerekli tablolar mevcut")
            return True
            
        except MySQLError as e:
            print(f"❌ Genel tablo kontrol hatası: {e}")
            return False

    def run_migrations(self):
        """Ana migration işlemini çalıştırır."""
        try:
            print("🚀 Veritabanı migration başlatılıyor...")
            print("=" * 60)
            
            # Tabloların mevcut olup olmadığını kontrol et
            if self.check_tables_exist():
                print("✅ Tablolar zaten mevcut. Migration atlanıyor...")
                print("   💡 Eğer tabloları yeniden oluşturmak istiyorsanız:")
                print("   💡 migrations.force_recreate() metodunu kullanın.")
                print("=" * 60)
                return
            
            print("📋 Tablolar bulunamadı. Yeni tablolar oluşturuluyor...")
            
            # 1. Tabloları oluştur
            if not self.create_tables():
                raise Exception("Tablolar oluşturulamadı!")
            
            print("=" * 60)
            print("🎉 Veritabanı başarıyla oluşturuldu!")
            print("📊 Oluşturulan tablolar:")
            print("   • grades (Sınıflar) - JSON'dan dinamik")
            print("   • subjects (Dersler) - JSON'dan dinamik")
            print("   • units (Üniteler) - JSON'dan dinamik")
            print("   • topics (Konular) - JSON'dan dinamik")
            print("   • questions (Sorular)")
            print("   • question_options (Soru Seçenekleri)")
            print("   • users (Kullanıcılar)")
            print("   • quiz_sessions (Quiz Oturumları)")
            print("   • quiz_session_questions (Quiz Oturumu Soruları)")
            print("\n📚 Hiyerarşik yapı:")
            print("   Grade → Subject → Unit → Topic → Question → Question Options")
            print("   Quiz Session → Quiz Session Questions")
            
        except Exception as e:
            print(f"❌ Migration hatası: {e}")
            raise

    def force_recreate(self):
        """Tabloları zorla yeniden oluşturur."""
        try:
            print("🚀 Veritabanı zorla yeniden oluşturuluyor...")
            print("⚠️  TÜM VERİLER SİLİNECEK!")
            print("=" * 60)
            
            # Tabloları sil
            self.drop_all_tables()
            
            # Yeni tabloları oluştur
            if not self.create_tables():
                raise Exception("Tablolar oluşturulamadı!")
            
            print("=" * 60)
            print("🎉 Veritabanı başarıyla yeniden oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Yeniden oluşturma hatası: {e}")
            raise

    def get_table_info(self) -> Dict[str, int]:
        """Tablolardaki kayıt sayılarını döner."""
        try:
            table_counts = {}
            with self.db as conn:
                for table_name in self.table_order:
                    try:
                        conn.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        result = conn.cursor.fetchone()
                        count = result['count'] if result else 0
                        table_counts[table_name] = count
                    except MySQLError as e:
                        print(f"⚠️  {table_name} tablosu sayım hatası: {e}")
                        table_counts[table_name] = 0
            
            return table_counts
            
        except Exception as e:
            print(f"❌ Tablo bilgisi alma hatası: {e}")
            return {}

# =============================================================================
# DOĞRUDAN ÇALIŞTIRMA
# =============================================================================
if __name__ == "__main__":
    migrations = DatabaseMigrations()
    migrations.run_migrations()