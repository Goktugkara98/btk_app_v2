# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, sistem ile ilgili API rotalarını (endpoints) içerir.
# Sistem durumu, sağlık kontrolü gibi genel sistem işlemlerini yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. SİSTEM API ROTALARI (SYSTEM API ROUTES)
#   4.1. Sistem Durumu ve Sağlık Kontrolü
#     4.1.1. GET /health
#     4.1.2. GET /status
#     4.1.3. GET /version
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, jsonify
from datetime import datetime
import platform
import sys

# Import services here to avoid circular imports
try:
    from app.services.system_service import SystemService
except ImportError as e:
    SystemService = None

# Create the system blueprint
system_bp = Blueprint('system', __name__)

# =============================================================================
# 4.0. SERVİS BAŞLATMA
# =============================================================================
# Rotaların kullanacağı servis sınıfından bir örnek oluşturulur.
system_service = SystemService() if SystemService else None

# =============================================================================
# 4.0. SİSTEM API ROTALARI (SYSTEM API ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 4.1. Sistem Durumu ve Sağlık Kontrolü
# -------------------------------------------------------------------------

@system_bp.route('/health', methods=['GET'])
def health_check():
    """4.1.1. Sistem durumunu kontrol eder."""
    if system_service:
        health_status = system_service.get_health_status()
        return jsonify(health_status), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'System service not available',
            'timestamp': datetime.now().isoformat()
        }), 500

@system_bp.route('/status', methods=['GET'])
def system_status():
    """4.1.2. Detaylı sistem durumunu döndürür."""
    if system_service:
        status = system_service.get_system_status()
        return jsonify(status), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'System service not available',
            'timestamp': datetime.now().isoformat()
        }), 500

@system_bp.route('/version', methods=['GET'])
def get_version():
    """4.1.3. API versiyon bilgisini döndürür."""
    if system_service:
        version_info = system_service.get_version_info()
        return jsonify(version_info), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'System service not available',
            'timestamp': datetime.now().isoformat()
        }), 500 