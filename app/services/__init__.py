# =============================================================================
# Services Package
# =============================================================================
# Bu paket, Flask uygulamasının iş mantığı servislerini modüler bir yapıda içerir.
# 
# Modüller:
# - services.py: Ana servis fabrikası ve modül birleştirme
# - user_service.py: Kullanıcı ile ilgili iş mantığı
# - quiz_service.py: Quiz ile ilgili iş mantığı
# - system_service.py: Sistem durumu ve sağlık kontrolü
# =============================================================================

# Import the main service factory
from .services import service_factory, get_user_service, get_quiz_service, get_system_service

# Import individual service classes for direct access if needed
try:
    from .user_service import UserService
    from .quiz_service import QuizService
    from .system_service import SystemService
    from .auth_service import AuthenticationService, auth_service
except ImportError as e:
    print(f"Warning: Could not import some service classes: {e}")
    UserService = None
    QuizService = None
    SystemService = None
    AuthenticationService = None
    auth_service = None

__all__ = [
    'service_factory',
    'get_user_service',
    'get_quiz_service', 
    'get_system_service',
    'UserService',
    'QuizService',
    'SystemService',
    'AuthenticationService',
    'auth_service'
] 