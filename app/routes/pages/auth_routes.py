# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, kimlik doğrulama ile ilgili sayfa rotalarını (endpoints) içerir.
# Giriş, kayıt gibi kimlik doğrulama sayfalarını yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. KİMLİK DOĞRULAMA SAYFA ROTALARI (AUTH PAGE ROUTES)
#   4.1. Giriş ve Kayıt
#     4.1.1. GET /login
#     4.1.2. GET /register
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, render_template

# Create the authentication pages blueprint
auth_bp = Blueprint('auth', __name__)

# =============================================================================
# 4.0. KİMLİK DOĞRULAMA SAYFA ROTALARI (AUTH PAGE ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 4.1. Giriş ve Kayıt
# -------------------------------------------------------------------------

@auth_bp.route('/login')
def login():
    """4.1.1. Giriş sayfasını render eder."""
    return render_template('login.html', title='Login')

@auth_bp.route('/register')
def register():
    """4.1.2. Kayıt sayfasını render eder."""
    return render_template('register.html', title='Register') 