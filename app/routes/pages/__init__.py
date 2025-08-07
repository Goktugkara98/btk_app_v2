# =============================================================================
# Page Routes Package
# =============================================================================
# Bu paket, Flask uygulamasının sayfa rotalarını modüler bir yapıda içerir.
# 
# Modüller:
# - routes.py: Ana sayfa blueprint'i ve modül birleştirme
# - main_routes.py: Ana sayfa rotaları (index, about, contact)
# - auth_routes.py: Kimlik doğrulama sayfa rotaları (login, register)
# - quiz_routes.py: Quiz sayfa rotaları (quiz, quiz/start, quiz/results)
# - user_routes.py: Kullanıcı sayfa rotaları (profile)
# =============================================================================

from flask import Blueprint

# Import the main page blueprint from routes.py
from .routes import pages_bp

# Import individual route blueprints for direct access if needed
try:
    from .main_routes import main_bp
    from .auth_routes import auth_bp
    from .quiz_routes import quiz_bp
    from .user_routes import user_bp
except ImportError as e:
    main_bp = None
    auth_bp = None
    quiz_bp = None
    user_bp = None

# This makes the main blueprint available when importing from app.routes.pages
__all__ = ['pages_bp', 'main_bp', 'auth_bp', 'quiz_bp', 'user_bp']
