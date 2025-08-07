# =============================================================================
# API Routes Package
# =============================================================================
# Bu paket, Flask uygulamasının API rotalarını modüler bir yapıda içerir.
# 
# Modüller:
# - api_routes.py: Ana API blueprint'i ve modül birleştirme
# - user_routes.py: Kullanıcı ile ilgili API rotaları
# - system_routes.py: Sistem durumu ve sağlık kontrolü rotaları
# - quiz_routes.py: Quiz ile ilgili API rotaları
# =============================================================================

from flask import Blueprint

# Import the main API blueprint from api_routes.py
from .api_routes import api_bp

# Import individual route blueprints for direct access if needed
try:
    from .user_routes import user_bp
    from .system_routes import system_bp
    from .quiz_routes import quiz_bp
except ImportError as e:
    user_bp = None
    system_bp = None
    quiz_bp = None

# This makes the main blueprint available when importing from app.routes.api
__all__ = ['api_bp', 'user_bp', 'system_bp', 'quiz_bp']
