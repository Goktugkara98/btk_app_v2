# =============================================================================
# AUTHENTICATION SERVICE
# =============================================================================
# Bu modül, kullanıcı kimlik doğrulama ile ilgili iş mantığını yönetir.
# Session kontrolü, login durumu kontrolü, authentication decorator'ları
# ve güvenlik işlemleri burada yer alır.
# =============================================================================

from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from typing import Optional, Dict, Any, Callable
from werkzeug.security import check_password_hash
from app.database.repositories.user_repository import UserRepository

class AuthenticationService:
    """
    Kullanıcı kimlik doğrulama işlemlerini yöneten servis sınıfı.
    """
    
    def __init__(self):
        """Authentication servisini başlatır."""
        self.user_repo = UserRepository()
    
    def login_required(self, f: Callable) -> Callable:
        """
        Decorator: Kullanıcının giriş yapmış olmasını zorunlu kılar.
        Giriş yapmamış kullanıcıları login sayfasına yönlendirir.
        
        Args:
            f: Dekore edilecek fonksiyon
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Debug: Log session state
            from flask import current_app
            if current_app.debug:
                print("=== AUTH DEBUG (login_required) ===")
                print(f"Request path: {request.path}")
                print(f"Session data: {dict(session)}")
                print(f"is_logged_in: {self.is_logged_in()}")
                print(f"User ID in session: {session.get('user_id')}")
                print("=================================")
            
            if not self.is_logged_in():
                # AJAX istekleri için JSON yanıt
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'error',
                        'message': 'Giriş yapmanız gerekiyor',
                        'redirect': '/login',
                        'debug': {
                            'session': dict(session),
                            'is_logged_in': self.is_logged_in(),
                            'headers': dict(request.headers)
                        }
                    }), 401
                # Auth sayfaları 'pages.auth' blueprint'indedir.
                return redirect(url_for('pages.auth.login') + f'?next={request.path}')
            return f(*args, **kwargs)
        return decorated_function
    
    def admin_required(self, f: Callable) -> Callable:
        """
        Decorator: Kullanıcının admin yetkisine sahip olmasını zorunlu kılar.
        
        Args:
            f: Dekore edilecek fonksiyon
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Debug: Log session state
            from flask import current_app
            if current_app.debug:
                print("=== AUTH DEBUG ===")
                print(f"Request path: {request.path}")
                print(f"Session data: {dict(session)}")
                print(f"is_logged_in: {self.is_logged_in()}")
                print(f"User ID in session: {session.get('user_id')}")
                print(f"is_admin in session: {session.get('is_admin')}")
                print("==================")
            
            if not self.is_logged_in():
                # AJAX istekleri için JSON yanıt (API kullanımı için uygun)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'error',
                        'message': 'Giriş yapmanız gerekiyor',
                        'redirect': '/login',
                        'debug': {
                            'session': dict(session),
                            'is_logged_in': self.is_logged_in(),
                            'headers': dict(request.headers)
                        }
                    }), 401
                # Auth sayfaları 'pages.auth' blueprint'indedir.
                return redirect(url_for('pages.auth.login') + f'?next={request.path}')
            
            current_user = self.get_current_user()
            if not current_user or not current_user.get('is_admin'):
                return jsonify({
                    'status': 'error',
                    'message': 'Bu işlem için yetkiniz bulunmuyor'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Session'dan mevcut kullanıcı bilgilerini döndürür.
        Kullanıcı giriş yapmamışsa None döner.
        
        Returns:
            Kullanıcı bilgileri sözlüğü veya None
        """
        if self.is_logged_in():
            user_id = session.get('user_id')
            if user_id:
                # Veritabanından güncel kullanıcı bilgilerini al
                user = self.user_repo.get_user_by_id(user_id)
                if user:
                    return {
                        'id': user.get('id'),
                        'username': user.get('username'),
                        'email': user.get('email'),
                        'is_admin': user.get('is_admin', False),
                        'created_at': user.get('created_at')
                    }
            
            # Session'dan temel bilgileri döndür
            return {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email'),
                'is_admin': session.get('is_admin', False)
            }
        return None
    
    def is_logged_in(self) -> bool:
        """
        Kullanıcının giriş yapıp yapmadığını kontrol eder.
        
        Returns:
            True if logged in, False otherwise
        """
        return session.get('logged_in', False)
    
    def login_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Kullanıcıyı sisteme giriş yapar (session'a kaydeder).
        
        Args:
            user_data: Kullanıcı bilgileri
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session['logged_in'] = True
            session['user_id'] = user_data.get('id')
            session['username'] = user_data.get('username')
            session['email'] = user_data.get('email')
            session['is_admin'] = user_data.get('is_admin', False)
            return True
        except Exception as e:
            return False
    
    def logout_user(self) -> bool:
        """
        Kullanıcıyı çıkış yapar (session'ı temizler).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session.clear()
            return True
        except Exception as e:
            return False
    
    def validate_session(self) -> bool:
        """
        Mevcut session'ın geçerli olup olmadığını kontrol eder.
        
        Returns:
            True if session is valid, False otherwise
        """
        if not self.is_logged_in():
            return False
        
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        # Veritabanından kullanıcının hala var olup olmadığını kontrol et
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            self.logout_user()
            return False
        
        return True
    
    def refresh_session(self) -> bool:
        """
        Session'ı yeniler (kullanıcı bilgilerini günceller).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_logged_in():
            return False
        
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        # Veritabanından güncel kullanıcı bilgilerini al
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            self.logout_user()
            return False
        
        # Session'ı güncelle
        session['username'] = user.get('username')
        session['email'] = user.get('email')
        session['is_admin'] = user.get('is_admin', False)
        
        return True

# Global authentication service instance
auth_service = AuthenticationService()

# Convenience functions for backward compatibility
def login_required(f: Callable) -> Callable:
    """Decorator: Kullanıcının giriş yapmış olmasını zorunlu kılar."""
    return auth_service.login_required(f)

def admin_required(f: Callable) -> Callable:
    """Decorator: Kullanıcının admin yetkisine sahip olmasını zorunlu kılar."""
    return auth_service.admin_required(f)

def get_current_user() -> Optional[Dict[str, Any]]:
    """Session'dan mevcut kullanıcı bilgilerini döndürür."""
    return auth_service.get_current_user()

def is_logged_in() -> bool:
    """Kullanıcının giriş yapıp yapmadığını kontrol eder."""
    return auth_service.is_logged_in()

def logout_user() -> bool:
    """Kullanıcıyı çıkış yapar (session'ı temizler)."""
    return auth_service.logout_user() 