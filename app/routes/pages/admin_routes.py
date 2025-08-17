# =============================================================================
# ADMIN PAGE ROUTES
# =============================================================================
# Admin paneli sayfaları için rotalar
# Müfredat yönetimi arayüzü
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash
from functools import wraps

# Blueprint oluştur
admin_pages_bp = Blueprint('admin_pages', __name__, url_prefix='/admin')

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Basit session kontrolü - gerçek uygulamada JWT token kontrolü yapılmalı
        user_id = session.get('user_id')
        if not user_id:
            flash('Bu sayfaya erişim için giriş yapmanız gerekli.', 'error')
            return redirect(url_for('pages.auth.login'))
        
        # is_admin session'da yoksa veritabanından kontrol et
        is_admin = session.get('is_admin')
        if is_admin is None:
            try:
                from app.database.repositories.user_repository import UserRepository
                user_repo = UserRepository()
                user = user_repo.get_user_by_id(user_id)
                if user:
                    is_admin = user.get('is_admin', False)
                    session['is_admin'] = is_admin  # Session'ı güncelle
                else:
                    is_admin = False
            except:
                is_admin = False
        
        if not is_admin:
            flash('Bu sayfaya erişim için admin yetkisi gerekli.', 'error')
            return redirect(url_for('pages.auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# ADMIN PANEL SAYFALARI
# =============================================================================

@admin_pages_bp.route('/debug-session')
def debug_session():
    """Session debug için geçici endpoint"""
    from flask import jsonify
    return jsonify({
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'is_admin': session.get('is_admin'),
        'logged_in': session.get('logged_in'),
        'username': session.get('username')
    })

@admin_pages_bp.route('/')
# @admin_required  # Geçici olarak devre dışı
def dashboard():
    """Admin dashboard ana sayfası"""
    return render_template('admin/dashboard.html', title='Admin Dashboard')

@admin_pages_bp.route('/curriculum')
@admin_required
def curriculum_management():
    """Müfredat yönetimi ana sayfası"""
    return render_template('admin/curriculum.html', title='Müfredat Yönetimi')

@admin_pages_bp.route('/grades')
@admin_required
def grades_management():
    """Sınıf yönetimi sayfası"""
    return render_template('admin/grades.html', title='Sınıf Yönetimi')

@admin_pages_bp.route('/subjects')
@admin_required
def subjects_management():
    """Ders yönetimi sayfası"""
    return render_template('admin/subjects.html', title='Ders Yönetimi')

@admin_pages_bp.route('/units')
@admin_required
def units_management():
    """Ünite yönetimi sayfası"""
    return render_template('admin/units.html', title='Ünite Yönetimi')

@admin_pages_bp.route('/topics')
@admin_required
def topics_management():
    """Konu yönetimi sayfası"""
    return render_template('admin/topics.html', title='Konu Yönetimi')

@admin_pages_bp.route('/import-export')
@admin_required
def import_export():
    """JSON import/export sayfası"""
    return render_template('admin/import_export.html', title='Veri Aktarımı')
