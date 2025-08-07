# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, sistem ile ilgili iş mantığını yöneten SystemService sınıfını
# içerir. Sistem durumu, sağlık kontrolü gibi genel sistem işlemlerini yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. SYSTEMERVICE SINIFI
#   4.1. Başlatma (Initialization)
#     4.1.1. __init__(self)
#   4.2. Sistem Durumu İşlemleri
#     4.2.1. get_health_status(self)
#     4.2.2. get_system_status(self)
#     4.2.3. get_version_info(self)
#   4.3. Sistem Yönetimi
#     4.3.1. check_database_connection(self)
#     4.3.2. get_system_metrics(self)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import platform
import sys
import psutil
import os

# Import database connection for health checks
try:
    from app.database.db_connection import DatabaseConnection
except ImportError:
    DatabaseConnection = None

# =============================================================================
# 4.0. SYSTEMERVICE SINIFI
# =============================================================================
class SystemService:
    """
    Sistem ile ilgili iş mantığını yönetir.
    """

    # -------------------------------------------------------------------------
    # 4.1. Başlatma (Initialization)
    # -------------------------------------------------------------------------
    def __init__(self):
        """4.1.1. Servisin kurucu metodu."""
        self.app_name = "BTK Quiz API"
        self.version = "1.0.0"
        self.environment = "production"

    # -------------------------------------------------------------------------
    # 4.2. Sistem Durumu İşlemleri
    # -------------------------------------------------------------------------
    def get_health_status(self) -> Dict[str, Any]:
        """4.2.1. Sistem sağlık durumunu döndürür."""
        try:
            health_status = {
                'status': 'healthy',
                'message': 'API is running',
                'timestamp': datetime.now().isoformat(),
                'service': self.app_name,
                'version': self.version,
                'environment': self.environment
            }
            return health_status
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': 'Health check failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def get_system_status(self) -> Dict[str, Any]:
        """4.2.2. Detaylı sistem durumunu döndürür."""
        try:
            # Get system information
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': sys.version,
                'architecture': platform.architecture()[0],
                'processor': platform.processor()
            }
            
            # Get system metrics
            system_metrics = self.get_system_metrics()
            
            status = {
                'status': 'success',
                'message': 'System status retrieved successfully',
                'data': {
                    'timestamp': datetime.now().isoformat(),
                    'service': self.app_name,
                    'version': self.version,
                    'environment': self.environment,
                    'system': system_info,
                    'metrics': system_metrics
                }
            }
            return status
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to retrieve system status',
                'error': str(e)
            }

    def get_version_info(self) -> Dict[str, Any]:
        """4.2.3. API versiyon bilgisini döndürür."""
        try:
            version_info = {
                'status': 'success',
                'data': {
                    'version': self.version,
                    'name': self.app_name,
                    'description': 'BTK Quiz uygulaması için REST API',
                    'author': 'BTK Development Team',
                    'timestamp': datetime.now().isoformat(),
                    'environment': self.environment
                }
            }
            return version_info
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to retrieve version info',
                'error': str(e)
            }

    # -------------------------------------------------------------------------
    # 4.3. Sistem Yönetimi
    # -------------------------------------------------------------------------
    def check_database_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """4.3.1. Veritabanı bağlantısını kontrol eder."""
        try:
            if not DatabaseConnection:
                return False, {'message': 'Database connection module not available'}
            
            db = DatabaseConnection()
            with db as conn:
                conn.cursor.execute("SELECT 1")
                result = conn.cursor.fetchone()
                
                if result and result[0] == 1:
                    return True, {'message': 'Database connection successful'}
                else:
                    return False, {'message': 'Database connection test failed'}
                    
        except Exception as e:
            return False, {'message': 'Database connection failed', 'error': str(e)}

    def get_system_metrics(self) -> Dict[str, Any]:
        """4.3.2. Sistem metriklerini döndürür."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            }
            
            # Network info
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'timestamp': datetime.now().isoformat()
            }
            
            return metrics
        except Exception as e:
            return {
                'error': 'Failed to retrieve system metrics',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            } 