# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, MySQL veritabanı bağlantısını yönetmek için bir sarmalayıcı
# (wrapper) olan `DatabaseConnection` sınıfını içerir. Bağlantı kurma,
# sonlandırma ve bağlantının sürekliliğini sağlama işlemlerini merkezileştirir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER
# 4.0. MODÜL SEVİYESİ YAPILANDIRMA
# 5.0. DATABASECONNECTION SINIFI
#   5.1. Başlatma (Initialization)
#     5.1.1. __init__(self)
#   5.2. Bağlantı Yönetimi (Connection Management)
#     5.2.1. connect(self)
#     5.2.2. close(self)
#     5.2.3. _ensure_connection(self)
#   5.3. Context Manager Metotları
#     5.3.1. __enter__(self)
#     5.3.2. __exit__(self, exc_type, exc_val, exc_tb)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER
# =============================================================================
import os
import mysql.connector
from mysql.connector import Error as MySQLError
from typing import Optional, Dict, Any

# =============================================================================
# 4.0. MODÜL SEVİYESİ YAPILANDIRMA
# =============================================================================
# Ortam değişkenlerinden (environment variables) yapılandırmayı yükle
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'btk_app'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

# =============================================================================
# 5.0. DATABASECONNECTION SINIFI
# =============================================================================
class DatabaseConnection:
    """
    MySQL veritabanı bağlantısını yönetmek için bir sarmalayıcı (wrapper) sınıf.
    """

    # -------------------------------------------------------------------------
    # 5.1. Başlatma (Initialization)
    # -------------------------------------------------------------------------
    def __init__(self):
        """5.1.1. Sınıfın kurucu metodu."""
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursor] = None
        self.db_config: Dict[str, Any] = DB_CONFIG
        # Bağlantıyı hemen kur
        self.connect()

    # -------------------------------------------------------------------------
    # 5.2. Bağlantı Yönetimi (Connection Management)
    # -------------------------------------------------------------------------
    def connect(self):
        """5.2.1. Yapılandırma dosyasındaki bilgileri kullanarak veritabanına bağlanır."""
        try:
            if self.connection and self.connection.is_connected():
                return True
            self.connection = mysql.connector.connect(**self.db_config)
            # Cursor'ı da oluştur
            if not self.cursor:
                self.cursor = self.connection.cursor(dictionary=True)
            return True
        except MySQLError as e:
            # Critical connection error - keep this print
            print(f"Veritabanı bağlantı hatası: {e}")
            self.connection = None
            self.cursor = None
            return False

    def close(self):
        """5.2.2. Veritabanı bağlantısını ve (varsa) cursor'u kapatır."""
        try:
            if self.cursor:
                try:
                    self.cursor.close()
                except Exception as e:
                    # Cursor kapatılırken hata oluşursa yine de devam et
                    pass
            self.cursor = None
            
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
        except Exception as e:
            # Hata yönetimi
            raise MySQLError(f"Error closing database connection: {e}")

    def _ensure_connection(self):
        """5.2.3. Bağlantının aktif olup olmadığını kontrol eder. Değilse, yeniden bağlanır."""
        try:
            if not self.connection or not self.connection.is_connected():
                # Keep only critical reconnection message
                if not self.connect():
                    raise MySQLError("Veritabanına bağlanılamadı")
        except Exception as e:
            # Critical connection error - keep this print
            print(f"❌ Bağlantı kontrol hatası: {e}")
            raise MySQLError(f"Veritabanı bağlantı hatası: {e}")

    # -------------------------------------------------------------------------
    # 5.3. Context Manager Metotları
    # -------------------------------------------------------------------------
    def __enter__(self):
        """5.3.1. 'with' bloğu için giriş metodu. Bağlantıyı sağlar ve yeni bir cursor döner."""
        self._ensure_connection()
        # Her 'with' bloğu için yeni bir cursor oluşturmak, izolasyon sağlar.
        if not self.cursor:
            self.cursor = self.connection.cursor(dictionary=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """5.3.2. 'with' bloğundan çıkıldığında sadece cursor'u kapatır, bağlantıyı korur."""
        # Sadece cursor'u kapat, bağlantıyı koru
        if self.cursor:
            try:
                self.cursor.close()
            except Exception as e:
                pass
        self.cursor = None
        
        # Hata durumunda rollback, başarılı durumda commit
        if exc_type and self.connection:
            try:
                self.connection.rollback()
            except Exception as e:
                pass
        elif self.connection:
            try:
                self.connection.commit()
            except Exception as e:
                pass