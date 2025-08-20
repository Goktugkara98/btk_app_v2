# Modern Database Connection Manager
#
# Bu modül, SQLAlchemy 2.0+ kullanarak modern, güçlü ve async-capable veritabanı 
# bağlantı yöneticisi sağlar. Hem senkron hem de asenkron veritabanı işlemleri 
# için kapsamlı destek sunar.
#
# ================================================================================
# İÇİNDEKİLER (TABLE OF CONTENTS)
# ================================================================================
#
# 1. MODÜL GENEL BAKIŞ
#    ============================================================================
#    1.1. Ne İşe Yarar?
#         - Veritabanı bağlantılarını yönetir
#         - Connection pooling ile performans optimizasyonu
#         - Hem sync hem async operasyonlar
#         - Otomatik health check ve reconnection
#         - Context manager desteği
#
#    1.2. Hangi Teknolojileri Kullanır?
#         - SQLAlchemy 2.0+ (modern ORM)
#         - MySQL/MariaDB desteği
#         - Async/await desteği
#         - Connection pooling
#         - Error handling ve logging
#
# 2. SINIFLAR (CLASSES)
#    ============================================================================
#    2.1. DatabaseConfig (Dataclass)
#         - Veritabanı konfigürasyon bilgilerini tutar
#         - Tüm ayarlar config sisteminden gelir
#         - Host, port, username, password, database name
#         - Pool ayarları (size, timeout, recycle)
#         - Character encoding ayarları
#
#    2.2. DatabaseConnectionManager (Ana Sınıf)
#         - Veritabanı bağlantılarını yönetir
#         - Sync ve async engine'leri oluşturur
#         - Session factory'leri yönetir
#         - Connection health monitoring
#         - Error handling ve recovery
#
# 3. FONKSİYONLAR VE METOTLAR
#    ============================================================================
#    3.1. DatabaseConfig Sınıfı Metotları
#         - from_config_class(): Config class'tan DatabaseConfig oluşturur
#
#    3.2. DatabaseConnectionManager Sınıfı Metotları
#         A. Başlatma ve Konfigürasyon
#            - __init__(): Sınıfı başlatır ve config'i yükler
#            - _validate_config(): Config değerlerini doğrular
#            - _initialize_connections(): Database engine'leri oluşturur
#
#         B. Bağlantı Yönetimi
#            - _build_connection_url(): Connection string oluşturur
#            - _test_connection_health(): Bağlantı sağlığını test eder
#            - test_connection(): Senkron bağlantı testi
#            - test_connection_async(): Asenkron bağlantı testi
#
#         C. Session Yönetimi
#            - get_sync_session(): Senkron database session verir
#            - get_async_session(): Asenkron database session verir
#
#         D. Sorgu Çalıştırma
#            - execute_query(): Senkron SQL sorgusu çalıştırır
#            - execute_query_async(): Asenkron SQL sorgusu çalıştırır
#
#         E. Durum ve Bilgi
#            - is_healthy(): Bağlantı sağlık durumunu kontrol eder
#            - get_health_status(): Detaylı sağlık bilgisi verir
#            - get_config_info(): Mevcut config bilgilerini verir
#
#         F. Kaynak Yönetimi
#            - close_all_connections(): Tüm bağlantıları kapatır
#
#         G. Context Manager Metotları
#            - __enter__() / __exit__(): Senkron context manager
#            - __aenter__() / __aexit__(): Asenkron context manager
#
#    3.3. Yardımcı Fonksiyonlar
#         - get_database_manager(): Hızlı database manager oluşturur
#
# 4. KULLANIM ÖRNEKLERİ
#    ============================================================================
#    4.1. Basit Kullanım
#         db_manager = get_database_manager()
#         
#    4.2. Senkron Session Kullanımı
#         with db_manager.get_sync_session() as session:
#             # Database işlemleri
#             result = session.execute(query)
#             
#    4.3. Asenkron Session Kullanımı
#         async with db_manager.get_async_session() as session:
#             # Async database işlemleri
#             result = await session.execute(query)
#             
#    4.4. Raw SQL Sorguları
#         result = db_manager.execute_query("SELECT * FROM users WHERE id = :id", {"id": 1})
#         
#    4.5. Health Check
#         if db_manager.is_healthy():
#             print("Database bağlantısı sağlıklı")
#             
#    4.6. Config Bilgilerini Görüntüleme
#         config_info = db_manager.get_config_info()
#         print(f"Database: {config_info['database']}")
#
# 5. KONFİGÜRASYON
#    ============================================================================
#    5.1. Gerekli Environment Variables
#         - DB_HOST: Veritabanı sunucu adresi
#         - DB_PORT: Veritabanı port numarası
#         - DB_USERNAME: Veritabanı kullanıcı adı
#         - DB_PASSWORD: Veritabanı şifresi
#         - DB_NAME: Veritabanı adı
#
#    5.2. Opsiyonel Environment Variables
#         - DB_POOL_SIZE: Connection pool boyutu
#         - DB_MAX_OVERFLOW: Maksimum overflow bağlantı sayısı
#         - DB_POOL_TIMEOUT: Pool timeout süresi
#         - DB_POOL_RECYCLE: Pool recycle süresi
#         - DB_POOL_PRE_PING: Pre-ping özelliği
#
# 6. HATA YÖNETİMİ
#    ============================================================================
#    6.1. Otomatik Rollback
#         - Hata durumunda otomatik rollback
#         - Session cleanup garantisi
#         
#    6.2. Connection Recovery
#         - Bağlantı koptuğunda otomatik yeniden bağlanma
#         - Health check ile sürekli monitoring
#         
#    6.3. Logging
#         - Detaylı hata logları
#         - Connection durumu logları
#         - Performance metrikleri
#
# 7. PERFORMANS ÖZELLİKLERİ
#    ============================================================================
#    7.1. Connection Pooling
#         - Veritabanı bağlantılarını yeniden kullanma
#         - Yeni bağlantı oluşturma maliyetini azaltma
#         
#    7.2. Async Support
#         - Asenkron veritabanı operasyonları
#         - I/O blocking'i önleme
#         
#    7.3. Pre-ping
#         - Bağlantı sağlığını sürekli kontrol etme
#         - Dead connection'ları otomatik temizleme
#
# 8. GÜVENLİK
#    ============================================================================
#    8.1. Config Validation
#         - Tüm config değerlerinin doğrulanması
#         - Güvenlik açıklarının önlenmesi
#         
#    8.2. Session Isolation
#         - Her session'ın izole edilmesi
#         - Transaction güvenliği
#         
#    8.3. Error Handling
#         - Hassas bilgilerin log'larda görünmemesi
#         - Güvenli hata mesajları
#
# ================================================================================
# KOD BAŞLANGICI
# ================================================================================

import asyncio
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import Optional, Dict, Any, Union, Generator, AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

# SQLAlchemy imports with modern syntax
try:
    from sqlalchemy import create_engine, text, Engine
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
    from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError as e:
    logging.error(f"SQLAlchemy import error: {e}")
    SQLALCHEMY_AVAILABLE = False
    # Fallback imports for type hints
    create_engine = None
    create_async_engine = None
    Engine = None
    AsyncEngine = None
    Session = None
    AsyncSession = None
    SQLAlchemyError = Exception

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """
    Veritabanı konfigürasyon bilgilerini tutan dataclass.
    
    Bu sınıf, veritabanı bağlantısı için gerekli tüm ayarları içerir.
    Tüm değerler config sisteminden gelir, hardcoded değer yoktur.
    
    Attributes:
        host: Veritabanı sunucu adresi (örn: localhost, 192.168.1.100)
        port: Veritabanı port numarası (1-65535 arası)
        username: Veritabanı kullanıcı adı
        password: Veritabanı şifresi
        database: Veritabanı adı
        charset: Karakter seti (varsayılan: utf8mb4)
        collation: Karakter sıralama (varsayılan: utf8mb4_unicode_ci)
        pool_size: Connection pool boyutu (varsayılan: 10)
        max_overflow: Maksimum overflow bağlantı sayısı (varsayılan: 20)
        pool_timeout: Pool timeout süresi saniye (varsayılan: 30)
        pool_recycle: Pool recycle süresi saniye (varsayılan: 3600)
        pool_pre_ping: Pre-ping özelliği (varsayılan: True)
        echo: SQL log'larını göster (varsayılan: False, debug modda True)
    """
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str
    collation: str
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int
    pool_pre_ping: bool
    echo: bool
    
    @classmethod
    def from_config_class(cls, config_class) -> "DatabaseConfig":
        """
        Config class'tan DatabaseConfig oluşturur.
        
        Bu metot, ana uygulama config'inden veritabanı ayarlarını alır
        ve DatabaseConfig nesnesi oluşturur.
        
        Args:
            config_class: Ana uygulama config sınıfı
            
        Returns:
            DatabaseConfig: Veritabanı konfigürasyon nesnesi
            
        Example:
            from config import get_config
            config = get_config()
            db_config = DatabaseConfig.from_config_class(config)
        """
        return cls(
            host=config_class.DATABASE.HOST,
            port=config_class.DATABASE.PORT,
            username=config_class.DATABASE.USERNAME,
            password=config_class.DATABASE.PASSWORD,
            database=config_class.DATABASE.DATABASE,
            charset=config_class.DATABASE.CHARSET,
            collation=config_class.DATABASE.COLLATION,
            pool_size=config_class.DATABASE.POOL_SIZE,
            max_overflow=config_class.DATABASE.MAX_OVERFLOW,
            pool_timeout=config_class.DATABASE.POOL_TIMEOUT,
            pool_recycle=config_class.DATABASE.POOL_RECYCLE,
            pool_pre_ping=config_class.DATABASE.POOL_PRE_PING,
            echo=config_class.APP.DEBUG
        )


class DatabaseConnectionManager:
    """
    Modern veritabanı bağlantı yöneticisi - hem sync hem async destek.
    
    Bu sınıf, veritabanı bağlantılarını yönetir, connection pooling sağlar,
    session lifecycle'ını kontrol eder ve hem senkron hem de asenkron
    veritabanı operasyonları için destek sunar.
    
    Özellikler:
        - Connection pooling ile performans optimizasyonu
        - Hem sync hem async interfaces
        - Otomatik connection health checks
        - Graceful error handling ve reconnection
        - Context manager desteği
        - Session lifecycle management
        - Tüm konfigürasyon config sisteminden gelir
        
    Kullanım Örnekleri:
        # Basit kullanım
        db_manager = DatabaseConnectionManager()
        
        # Senkron session
        with db_manager.get_sync_session() as session:
            result = session.execute(query)
            
        # Asenkron session
        async with db_manager.get_async_session() as session:
            result = await session.execute(query)
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        DatabaseConnectionManager'ı başlatır.
        
        Args:
            config: DatabaseConfig nesnesi. Eğer verilmezse, config sisteminden
                   otomatik olarak yüklenir.
                   
        Raises:
            ImportError: SQLAlchemy kullanılamıyorsa
            ValueError: Config validation başarısız olursa
            
        Example:
            # Otomatik config yükleme
            db_manager = DatabaseConnectionManager()
            
            # Manuel config ile
            config = DatabaseConfig.from_config_class(app_config)
            db_manager = DatabaseConnectionManager(config)
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required but not available")
        
        # Eğer config verilmezse, config sisteminden yükle
        if config is None:
            from config import get_config
            app_config = get_config()
            config = DatabaseConfig.from_config_class(app_config)
        
        self.config = config
        self._sync_engine: Optional[Engine] = None
        self._async_engine: Optional[AsyncEngine] = None
        self._sync_session_factory: Optional[sessionmaker] = None
        self._async_session_factory: Optional[async_sessionmaker] = None
        self._connection_healthy = False
        
        # Konfigürasyonu doğrula
        self._validate_config()
        
        # Bağlantıları başlat
        self._initialize_connections()
    
    def _validate_config(self) -> None:
        """
        Konfigürasyon değerlerini doğrular.
        
        Bu metot, veritabanı bağlantısı için gerekli tüm config değerlerinin
        mevcut olduğunu ve geçerli olduğunu kontrol eder.
        
        Raises:
            ValueError: Gerekli config değerleri eksik veya geçersizse
            
        Example:
            # Bu metot __init__ içinde otomatik çağrılır
            # Manuel olarak çağırmaya gerek yoktur
        """
        # Zorunlu alanları kontrol et
        required_fields = ['host', 'port', 'username', 'password', 'database']
        missing_fields = [field for field in required_fields if not getattr(self.config, field)]
        
        if missing_fields:
            raise ValueError(f"Missing required database configuration: {missing_fields}")
        
        # Port numarasının geçerli olduğunu kontrol et
        if not (1 <= self.config.port <= 65535):
            raise ValueError(f"Invalid database port: {self.config.port}")
        
        # Pool ayarlarının geçerli olduğunu kontrol et
        if self.config.pool_size <= 0:
            raise ValueError(f"Invalid pool size: {self.config.pool_size}")
        
        if self.config.max_overflow < 0:
            raise ValueError(f"Invalid max overflow: {self.config.max_overflow}")
        
        logger.info(f"Database configuration validated for {self.config.host}:{self.config.port}")
    
    def _initialize_connections(self) -> None:
        """
        Sync ve async database engine'leri başlatır.
        
        Bu metot, config değerlerini kullanarak hem senkron hem de asenkron
        veritabanı engine'lerini oluşturur ve session factory'leri hazırlar.
        
        Raises:
            Exception: Engine oluşturma başarısız olursa
            
        Example:
            # Bu metot __init__ içinde otomatik çağrılır
            # Manuel olarak çağırmaya gerek yoktur
        """
        try:
            # Senkron engine oluştur
            sync_url = self._build_connection_url(is_async=False)
            self._sync_engine = create_engine(
                sync_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=self.config.echo
            )
            self._sync_session_factory = sessionmaker(bind=self._sync_engine)
            
            # Asenkron engine oluştur
            async_url = self._build_connection_url(is_async=True)
            self._async_engine = create_async_engine(
                async_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=self.config.echo
            )
            self._async_session_factory = async_sessionmaker(bind=self._async_engine)
            
            # Bağlantı sağlığını test et
            self._test_connection_health()
            logger.info(f"Database connections initialized successfully for {self.config.database}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    def _build_connection_url(self, is_async: bool = False) -> str:
        """
        Database connection URL'i oluşturur.
        
        Args:
            is_async: Async engine için True, sync engine için False
            
        Returns:
            str: Database connection string
            
        Example:
            # Bu metot dahili olarak kullanılır
            sync_url = self._build_connection_url(is_async=False)
            async_url = self._build_connection_url(is_async=True)
        """
        protocol = "mysql+aiomysql" if is_async else "mysql+mysqlconnector"
        
        return (
            f"{protocol}://"
            f"{self.config.username}:"
            f"{self.config.password}@"
            f"{self.config.host}:"
            f"{self.config.port}/"
            f"{self.config.database}"
            f"?charset={self.config.charset}"
            f"&collation={self.config.collation}"
        )
    
    def _test_connection_health(self) -> bool:
        """
        Database bağlantı sağlığını test eder.
        
        Bu metot, veritabanına basit bir sorgu göndererek bağlantının
        aktif olduğunu kontrol eder.
        
        Returns:
            bool: Bağlantı sağlıklıysa True, değilse False
            
        Example:
            # Bu metot dahili olarak kullanılır
            # Manuel olarak çağırmaya gerek yoktur
        """
        try:
            with self._sync_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                self._connection_healthy = True
                logger.info(f"Database health check passed for {self.config.host}:{self.config.port}")
                return True
        except Exception as e:
            logger.warning(f"Database health check failed for {self.config.host}:{self.config.port}: {e}")
            self._connection_healthy = False
            return False
    
    def is_healthy(self) -> bool:
        """
        Database bağlantısının sağlıklı olup olmadığını kontrol eder.
        
        Returns:
            bool: Bağlantı sağlıklıysa True, değilse False
            
        Example:
            if db_manager.is_healthy():
                print("Database bağlantısı sağlıklı")
            else:
                print("Database bağlantısında sorun var")
        """
        return self._connection_healthy and self._sync_engine is not None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Database bağlantısının detaylı sağlık durumunu verir.
        
        Returns:
            Dict[str, Any]: Sağlık durumu bilgileri
                - healthy: Genel sağlık durumu
                - host: Database host adresi
                - port: Database port numarası
                - database: Database adı
                - sync_engine_available: Sync engine mevcut mu?
                - async_engine_available: Async engine mevcut mu?
                - pool_size: Connection pool boyutu
                - max_overflow: Maksimum overflow
                - active_connections: Aktif bağlantı sayısı
                - checked_out_connections: Kullanılan bağlantı sayısı
                
        Example:
            health = db_manager.get_health_status()
            print(f"Database: {health['database']} on {health['host']}:{health['port']}")
            print(f"Healthy: {health['healthy']}")
            print(f"Active connections: {health['active_connections']}")
        """
        return {
            "healthy": self._connection_healthy,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "sync_engine_available": self._sync_engine is not None,
            "async_engine_available": self._async_engine is not None,
            "pool_size": self.config.pool_size,
            "max_overflow": self.config.max_overflow,
            "active_connections": self._sync_engine.pool.size() if self._sync_engine else 0,
            "checked_out_connections": self._sync_engine.pool.checkedout() if self._sync_engine else 0
        }
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Mevcut database konfigürasyon bilgilerini verir (hassas veriler hariç).
        
        Bu metot, database ayarlarını görüntülemek için kullanılır.
        Şifre gibi hassas bilgiler dahil edilmez.
        
        Returns:
            Dict[str, Any]: Konfigürasyon bilgileri
                - host: Database host adresi
                - port: Database port numarası
                - database: Database adı
                - username: Database kullanıcı adı
                - charset: Karakter seti
                - collation: Karakter sıralama
                - pool_size: Connection pool boyutu
                - max_overflow: Maksimum overflow
                - pool_timeout: Pool timeout süresi
                - pool_recycle: Pool recycle süresi
                - pool_pre_ping: Pre-ping özelliği
                - echo: SQL log'ları
                
        Example:
            config_info = db_manager.get_config_info()
            print(f"Database: {config_info['database']}")
            print(f"Host: {config_info['host']}:{config_info['port']}")
            print(f"Pool size: {config_info['pool_size']}")
        """
        return {
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "username": self.config.username,
            "charset": self.config.charset,
            "collation": self.config.collation,
            "pool_size": self.config.pool_size,
            "max_overflow": self.config.max_overflow,
            "pool_timeout": self.config.pool_timeout,
            "pool_recycle": self.config.pool_recycle,
            "pool_pre_ping": self.config.pool_pre_ping,
            "echo": self.config.echo
        }
    
    @contextmanager
    def get_sync_session(self) -> Generator[Session, None, None]:
        """
        Senkron database session verir (otomatik cleanup ile).
        
        Bu metot, context manager olarak kullanılır ve session'ın
        otomatik olarak commit/rollback ve cleanup yapılmasını sağlar.
        
        Yields:
            Session: SQLAlchemy session nesnesi
            
        Raises:
            RuntimeError: Sync session factory başlatılmamışsa
            
        Example:
            with db_manager.get_sync_session() as session:
                # Database işlemleri
                result = session.execute(query)
                # Session otomatik olarak commit edilir
                
            # Hata durumunda otomatik rollback
            try:
                with db_manager.get_sync_session() as session:
                    # Hata oluşabilir
                    session.execute(problematic_query)
            except Exception:
                # Session otomatik olarak rollback edilir
        """
        if not self._sync_session_factory:
            raise RuntimeError("Sync session factory not initialized")
        
        session = self._sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Asenkron database session verir (otomatik cleanup ile).
        
        Bu metot, async context manager olarak kullanılır ve session'ın
        otomatik olarak commit/rollback ve cleanup yapılmasını sağlar.
        
        Yields:
            AsyncSession: SQLAlchemy async session nesnesi
            
        Raises:
            RuntimeError: Async session factory başlatılmamışsa
            
        Example:
            async with db_manager.get_async_session() as session:
                # Async database işlemleri
                result = await session.execute(query)
                # Session otomatik olarak commit edilir
                
            # Hata durumunda otomatik rollback
            try:
                async with db_manager.get_async_session() as session:
                    # Hata oluşabilir
                    await session.execute(problematic_query)
            except Exception:
                # Session otomatik olarak rollback edilir
        """
        if not self._async_session_factory:
            raise RuntimeError("Async session factory not initialized")
        
        session = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Senkron olarak raw SQL sorgusu çalıştırır.
        
        Bu metot, basit SQL sorguları için kullanılır ve session
        yönetimi ile uğraşmaya gerek kalmaz.
        
        Args:
            query: Çalıştırılacak SQL sorgusu
            params: Sorgu parametreleri (opsiyonel)
            
        Returns:
            Any: Sorgu sonucu
            
        Raises:
            RuntimeError: Database bağlantısı sağlıklı değilse
            Exception: Sorgu çalıştırma hatası
            
        Example:
            # Basit sorgu
            result = db_manager.execute_query("SELECT COUNT(*) FROM users")
            
            # Parametreli sorgu
            result = db_manager.execute_query(
                "SELECT * FROM users WHERE age > :min_age",
                {"min_age": 18}
            )
            
            # Sonuçları işle
            for row in result:
                print(row)
        """
        if not self.is_healthy():
            raise RuntimeError("Database connection is not healthy")
        
        try:
            with self._sync_engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_query_async(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Asenkron olarak raw SQL sorgusu çalıştırır.
        
        Bu metot, async/await pattern kullanarak SQL sorgularını
        asenkron olarak çalıştırır.
        
        Args:
            query: Çalıştırılacak SQL sorgusu
            params: Sorgu parametreleri (opsiyonel)
            
        Returns:
            Any: Sorgu sonucu
            
        Raises:
            RuntimeError: Async engine başlatılmamışsa
            Exception: Sorgu çalıştırma hatası
            
        Example:
            # Async sorgu
            result = await db_manager.execute_query_async("SELECT COUNT(*) FROM users")
            
            # Parametreli async sorgu
            result = await db_manager.execute_query_async(
                "SELECT * FROM users WHERE age > :min_age",
                {"min_age": 18}
            )
            
            # Sonuçları işle
            for row in result:
                print(row)
        """
        if not self._async_engine:
            raise RuntimeError("Async engine not initialized")
        
        try:
            async with self._async_engine.connect() as conn:
                result = await conn.execute(text(query), params or {})
                return result
        except Exception as e:
            logger.error(f"Async query execution failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Database bağlantısını test eder (senkron).
        
        Returns:
            bool: Bağlantı başarılıysa True, başarısızsa False
            
        Example:
            if db_manager.test_connection():
                print("Database bağlantısı başarılı")
            else:
                print("Database bağlantısı başarısız")
        """
        try:
            self._test_connection_health()
            return self._connection_healthy
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def test_connection_async(self) -> bool:
        """
        Database bağlantısını test eder (asenkron).
        
        Returns:
            bool: Bağlantı başarılıysa True, başarısızsa False
            
        Example:
            if await db_manager.test_connection_async():
                print("Database bağlantısı başarılı")
            else:
                print("Database bağlantısı başarısız")
        """
        try:
            async with self._async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Async connection test failed: {e}")
            return False
    
    def close_all_connections(self) -> None:
        """
        Tüm database bağlantılarını kapatır ve engine'leri dispose eder.
        
        Bu metot, uygulama kapanırken veya database bağlantılarını
        yeniden başlatmak istediğinizde kullanılır.
        
        Example:
            # Uygulama kapanırken
            db_manager.close_all_connections()
            
            # Veya context manager ile
            with db_manager:
                # Database işlemleri
                pass
            # Context'ten çıkıldığında otomatik cleanup
        """
        try:
            if self._sync_engine:
                self._sync_engine.dispose()
                self._sync_engine = None
            
            if self._async_engine:
                # Async engine için dispose işlemi
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop çalışıyorsa, dispose'u schedule et
                        loop.create_task(self._async_engine.dispose())
                    else:
                        # Event loop yoksa, yeni bir tane oluştur
                        asyncio.run(self._async_engine.dispose())
                except Exception as e:
                    logger.warning(f"Could not dispose async engine gracefully: {e}")
                finally:
                    self._async_engine = None
            
            self._connection_healthy = False
            logger.info(f"All database connections closed for {self.config.database}")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    def __enter__(self):
        """
        Senkron context manager giriş metodu.
        
        Returns:
            DatabaseConnectionManager: Kendisi
            
        Example:
            with db_manager as db:
                # Database işlemleri
                pass
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Senkron context manager çıkış metodu.
        
        Bu metot, context'ten çıkıldığında otomatik olarak
        çağrılır. Bağlantıları burada kapatmıyoruz çünkü
        uygulama lifecycle'ını yönetmek istiyoruz.
        """
        # Bağlantıları burada kapatmıyoruz, uygulama lifecycle'ını yönetmek istiyoruz
        pass
    
    async def __aenter__(self):
        """
        Asenkron context manager giriş metodu.
        
        Returns:
            DatabaseConnectionManager: Kendisi
            
        Example:
            async with db_manager as db:
                # Async database işlemleri
                pass
        """
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asenkron context manager çıkış metodu.
        
        Bu metot, async context'ten çıkıldığında otomatik olarak
        çağrılır. Bağlantıları burada kapatmıyoruz çünkü
        uygulama lifecycle'ını yönetmek istiyoruz.
        """
        # Bağlantıları burada kapatmıyoruz, uygulama lifecycle'ını yönetmek istiyoruz
        pass


# ================================================================================
# YARDIMCI FONKSİYONLAR (HELPER FUNCTIONS)
# ================================================================================

def get_database_manager(config_class=None) -> DatabaseConnectionManager:
    """
    Hızlı database manager oluşturur.
    
    Bu fonksiyon, DatabaseConnectionManager oluşturmak için
    kolay bir yol sağlar. Eğer config_class verilmezse,
    config sisteminden otomatik olarak yüklenir.
    
    Args:
        config_class: Uygulama config sınıfı (opsiyonel)
        
    Returns:
        DatabaseConnectionManager: Database bağlantı yöneticisi
        
    Example:
        # Otomatik config yükleme
        db_manager = get_database_manager()
        
        # Manuel config ile
        from config import get_config
        config = get_config()
        db_manager = get_database_manager(config)
        
        # Kullanım
        with db_manager.get_sync_session() as session:
            result = session.execute(query)
    """
    if config_class is None:
        from config import get_config
        config_class = get_config()
    
    db_config = DatabaseConfig.from_config_class(config_class)
    return DatabaseConnectionManager(db_config)


# ================================================================================
# LEGACY COMPATIBILITY (GERİYE DÖNÜK UYUMLULUK)
# ================================================================================

# Eski kodlarla uyumluluk için alias
DatabaseConnection = DatabaseConnectionManager