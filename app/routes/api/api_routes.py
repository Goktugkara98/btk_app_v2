# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, Flask uygulamasının ana API rotalarını (endpoints) içerir.
# Diğer API modüllerini birleştirir ve ana blueprint'i oluşturur.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. BLUEPRINT BİRLEŞTİRME
# 5.0. ANA API ROTALARI (MAIN API ROUTES)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint

# Create the main API blueprint
api_bp = Blueprint('api', __name__)

# =============================================================================
# 4.0. BLUEPRINT BİRLEŞTİRME
# =============================================================================
# Diğer API modüllerinden blueprint'leri import et ve kaydet

# Import user routes
try:
    from .user_routes import user_bp
    api_bp.register_blueprint(user_bp)
except ImportError as e:
    pass

# Import system routes
try:
    from .system_routes import system_bp
    api_bp.register_blueprint(system_bp)
except ImportError as e:
    pass

# Import quiz routes
try:
    from .quiz_routes import quiz_bp
    api_bp.register_blueprint(quiz_bp)
except ImportError as e:
    pass

# Import AI chat routes
try:
    from .ai_chat_v2_routes import ai_chat_v2_bp
    api_bp.register_blueprint(ai_chat_v2_bp)
except ImportError as e:
    pass

# =============================================================================
# 5.0. ANA API ROTALARI (MAIN API ROUTES)
# =============================================================================
# Bu bölümde sadece ana API seviyesinde olması gereken rotalar bulunur.
# Özel rotalar ilgili modüllerde tanımlanmalıdır.


