# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, Flask uygulamasının ana sayfa rotalarını (endpoints) içerir.
# Diğer sayfa modüllerini birleştirir ve ana blueprint'i oluşturur.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. BLUEPRINT BİRLEŞTİRME
# 5.0. ANA SAYFA ROTALARI (MAIN PAGE ROUTES)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint

# Create the main pages blueprint
pages_bp = Blueprint('pages', __name__)

# =============================================================================
# 4.0. BLUEPRINT BİRLEŞTİRME
# =============================================================================
# Diğer sayfa modüllerinden blueprint'leri import et ve kaydet

# Import main routes
try:
    from .main_routes import main_bp
    pages_bp.register_blueprint(main_bp)
except ImportError as e:
    pass

# Import authentication routes
try:
    from .auth_routes import auth_bp
    pages_bp.register_blueprint(auth_bp)
except ImportError as e:
    pass

# Import quiz routes
try:
    from .quiz_routes import quiz_bp
    pages_bp.register_blueprint(quiz_bp)
except ImportError as e:
    pass

# Import user routes
try:
    from .user_routes import user_bp
    pages_bp.register_blueprint(user_bp)
except ImportError as e:
    pass

# =============================================================================
# 5.0. ANA SAYFA ROTALARI (MAIN PAGE ROUTES)
# =============================================================================
# Bu bölümde sadece ana sayfa seviyesinde olması gereken rotalar bulunur.
# Özel rotalar ilgili modüllerde tanımlanmalıdır.




