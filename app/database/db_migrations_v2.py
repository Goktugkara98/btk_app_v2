# =============================================================================
# Veritabanı Geçişleri - Yeniden Düzenlenmiş Sürüm
# =============================================================================
# Amaç: Bu modül, veritabanı şemalarını yönetir. Tanımlanmış Python
# şemalarından tablolar oluşturur, başlangıç verilerini ekler ve veritabanı
# bakım işlemlerini gerçekleştirir. Tüm işlemler idempotent (tekrarlanabilir)
# olacak şekilde tasarlanmıştır.
#
# İçindekiler:
#
# 1. Kurulum ve Yaşam Döngüsü (Setup & Lifecycle)
#    1.1. __init__(self, db_connection)
#    1.2. __del__(self)
#
# 2. Genel API: Tablo Yönetimi (Public API: Table Management)
#    2.1. run_migrations(self)
#    2.2. create_tables(self)
#    2.3. drop_all_tables(self)
#    2.4. force_recreate(self)
#
# 3. Genel API: Veri Doldurma ve Bakım (Public API: Data Seeding & Maintenance)
#    3.1. seed_initial_data(self)
#    3.2. create_missing_indexes(self)
#    3.3. get_table_info(self)
#
# 4. Dahili Yardımcılar: Veritabanı İşlemleri (Internal Helpers: Database Operations)
#    4.1. _exec(self, conn, sql, params)
#    4.2. _fetchone(self, conn, sql, params)
#    4.3. _ensure_tables(self)
#
# 5. Dahili Yardımcılar: Veri Doldurucular (Internal Helpers: Seeders)
#    5.1. _seed_grades_if_empty(self, conn)
#    5.2. _seed_curriculum_from_json(self, conn)
# =============================================================================

from typing import Optional, Dict
from mysql.connector import Error as MySQLError

from app.database.db_connection import DatabaseConnection
from app.database.migrations import SchemaManager, IndexManager
from app.database.seeders import SeedManager


class DatabaseMigrations:
    """
    Veritabanı şemalarını, verilerini ve index'lerini yönetir.
    - Python şemalarından tablolar oluşturur.
    - Başlangıç verilerini (seed) ekler.
    - Performans için gerekli index'leri oluşturur.
    """

    # =========================================================================
    # 1. Kurulum ve Yaşam Döngüsü (Setup & Lifecycle)
    # =========================================================================

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        """
        1.1. Sınıfı başlatır, veritabanı bağlantısını kurar ve tablo
             şemalarını tanımlar.
        
        Args:
            db_connection: Mevcut bir DatabaseConnection nesnesi. Eğer
                           sağlanmazsa, sınıf kendi bağlantısını oluşturur.
        """
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

        # Yeni yöneticiler (delegasyon)
        self.schema_manager = SchemaManager(self.db)
        self.index_manager = IndexManager(self.db)
        self.seed_manager = SeedManager(self.db)

        # Raporlama ve yardımcı fonksiyonlar için tablo sırası
        self.table_order = self.schema_manager.table_order

    def __del__(self) -> None:
        """
        1.2. Eğer bağlantı bu sınıf tarafından oluşturulduysa, sınıf
             yok edildiğinde veritabanı bağlantısını güvenli bir şekilde kapatır.
        """
        if self.own_connection:
            try:
                self.db.close()
            except Exception:
                # Bağlantı zaten kapalıysa veya bir hata oluşursa sessizce geç.
                pass

    # =========================================================================
    # 2. Genel API: Tablo Yönetimi (Public API: Table Management)
    # =========================================================================

    def run_migrations(self) -> bool:
        """
        2.1. Ana geçiş fonksiyonu. Veritabanındaki tüm tabloların tanımlanmış
             şemalara göre var olmasını sağlar. Sadece eksik tabloları oluşturur.
        
        Returns:
            Tüm tablolar başarıyla oluşturulduysa veya zaten varsa True,
            aksi takdirde False.
        """
        return self.schema_manager.ensure_tables()

    def create_tables(self) -> bool:
        """
        2.2. `run_migrations` için bir takma addır (alias). Anlaşılırlığı artırmak
             için kullanılır.
        """
        return self.run_migrations()

    def drop_all_tables(self) -> bool:
        """
        2.3. Yabancı anahtar (FK) kısıtlamalarına uygun bir sırayla
             tüm yönetilen tabloları veritabanından siler.
        
        Returns:
            İşlem başarılı olursa True, aksi takdirde False.
        """
        return self.schema_manager.drop_all_tables()

    def force_recreate(self) -> bool:
        """
        2.4. Tüm tabloları siler ve ardından şemalara göre yeniden oluşturur.
             Test veya geliştirme ortamlarında veritabanını sıfırlamak için kullanışlıdır.
        
        Returns:
            Silme ve yeniden oluşturma işlemleri başarılı olursa True.
        """
        return self.schema_manager.force_recreate()

    # =========================================================================
    # 3. Genel API: Veri Doldurma ve Bakım (Public API: Data Seeding & Maintenance)
    # =========================================================================

    def seed_initial_data(self) -> bool:
        """
        3.1. Uygulamanın çalışması için gerekli olan başlangıç verilerini
             veritabanına ekler. Önce tabloların var olduğundan emin olur,
             ardından veri doldurma (seeding) işlemlerini çalıştırır.
        
        Returns:
            İşlem başarılı olursa True, aksi takdirde False.
        """
        try:
            if not self.schema_manager.ensure_tables():
                return False
            # Delegasyon seeding
            self.seed_manager.seed_grades_if_empty()
            self.seed_manager.seed_curriculum()
            return True
        except Exception:
            return False

    def create_missing_indexes(self) -> bool:
        """
        3.2. Sık yapılan sorguları hızlandırmak için kritik olan veritabanı
             index'lerini oluşturur. Eğer index zaten varsa, hiçbir işlem yapmaz.
        
        Returns:
            İşlem başarılı olursa True, aksi takdirde False.
        """
        return self.index_manager.ensure_indexes()

    def get_table_info(self) -> Dict[str, int]:
        """
        3.3. Her tablodaki mevcut satır sayısını içeren bir sözlük döndürür.
             Veritabanının durumunu kontrol etmek için kullanılır.
        
        Returns:
            {'tablo_adi': satir_sayisi} formatında bir sözlük.
        """
        info: Dict[str, int] = {}
        try:
            with self.db as conn:
                for table_name in self.table_order:
                    row = self._fetchone(conn, f"SELECT COUNT(*) AS cnt FROM {table_name}")
                    info[table_name] = row.get('cnt') if isinstance(row, dict) and row else 0
        except Exception:
            # Bir tablo henüz yoksa veya başka bir hata oluşursa, o tablo için 0 döndür.
            pass
        return info

    # =========================================================================
    # 4. Dahili Yardımcılar: Veritabanı İşlemleri (Internal Helpers: Database Operations)
    # =========================================================================

    def _exec(self, conn, sql: str, params: tuple | None = None) -> bool:
        """
        4.1. Verilen SQL sorgusunu (INSERT, UPDATE, DELETE, CREATE vb.)
             çalıştırır ve işlemi commit eder. Hata yönetimini basitleştirir.
        """
        try:
            cursor = conn.cursor
            cursor.execute(sql, params or ())
            conn.connection.commit()
            return True
        except MySQLError:
            # Hata durumunda False döndürerek çağıran fonksiyona bilgi ver.
            return False

    def _fetchone(self, conn, sql: str, params: tuple | None = None):
        """
        4.2. Verilen SQL sorgusunu (SELECT) çalıştırır ve tek bir sonuç
             satırını döndürür. Hata yönetimini basitleştirir.
        """
        try:
            cursor = conn.cursor
            cursor.execute(sql, params or ())
            return cursor.fetchone()
        except MySQLError:
            return None

    def _ensure_tables(self) -> bool:
        """Geriye dönük uyumluluk için bıraktık; yeni akış SchemaManager'a delege edilir."""
        return self.schema_manager.ensure_tables()

    # =========================================================================
    # 5. Dahili Yardımcılar: Veri Doldurucular (Internal Helpers: Seeders)
    # =========================================================================

    def _seed_grades_if_empty(self, conn) -> None:
        """Geriye dönük uyumluluk: yeni akış SeedManager üzerinden."""
        self.seed_manager.seed_grades_if_empty()

    def _seed_curriculum_from_json(self, conn) -> None:
        """Geriye dönük uyumluluk: yeni akış SeedManager üzerinden."""
        self.seed_manager.seed_curriculum()
