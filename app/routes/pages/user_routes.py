# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, kullanıcı ile ilgili sayfa rotalarını (endpoints) içerir.
# Profil, kullanıcı ayarları gibi kullanıcı sayfalarını yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. KULLANICI SAYFA ROTALARI (USER PAGE ROUTES)
#   4.1. Kullanıcı Sayfaları
#     4.1.1. GET /profile
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, render_template, session, redirect, url_for

# Import authentication service
try:
    from app.services.auth_service import login_required
except ImportError as e:
    login_required = None

# Create the user pages blueprint
user_bp = Blueprint('user', __name__)

# =============================================================================
# 4.0. KULLANICI SAYFA ROTALARI (USER PAGE ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 4.1. Kullanıcı Sayfaları
# -------------------------------------------------------------------------

@user_bp.route('/profile')
@login_required
def profile():
    """4.1.1. Kullanıcı profil sayfasını render eder."""
    # Kullanıcı ID'sini al
    user_id = session.get('user_id')
    
    # UserService'i import et ve kullanıcı verilerini al
    try:
        from app.services.user_service import UserService
        user_service = UserService()
        
        # Kullanıcı profil bilgilerini al
        user_profile = user_service.get_user_profile(user_id)
        
        if not user_profile:
            # Kullanıcı bulunamadıysa session'ı temizle ve login'e yönlendir
            session.clear()
            return redirect(url_for('auth.login'))
        
        return render_template('profile.html', title='Profile', user=user_profile)
        
    except Exception as e:
        return render_template('profile.html', title='Profile', user=None) 