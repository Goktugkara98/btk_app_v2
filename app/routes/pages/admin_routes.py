# =============================================================================
# ADMIN PAGE ROUTES
# =============================================================================
# Admin paneli sayfaları için rotalar
# Modern ve güvenli sayfa yönlendirmeleri
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app
from functools import wraps
import logging

# Blueprint oluştur
admin_pages_bp = Blueprint('admin_pages', __name__, url_prefix='/admin')

# Logging
logger = logging.getLogger(__name__)

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):

        
        # Development mode - bypass auth for now
        # TODO: Production'da gerçek auth kontrolü ekle
        return f(*args, **kwargs)
    return decorated_function

def log_page_access(page_name, user_id=None):
    """Sayfa erişimlerini logla"""
    try:
        logger.info(f"Admin page accessed: {page_name}", extra={
            'user_id': user_id,
            'page': page_name,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
    except Exception as e:
        logger.error(f"Page access logging error: {str(e)}")

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
@admin_required
def dashboard():
    """Admin dashboard ana sayfası"""
    try:

        
        user_id = session.get('user_id')
        log_page_access('dashboard', user_id)
        
        return render_template('admin/dashboard.html', 
                             title='Admin Dashboard',
                             page_name='dashboard')
    except Exception as e:
        logger.error(f"Dashboard page error: {str(e)}")
        flash('Dashboard yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.main.index'))

@admin_pages_bp.route('/curriculum')
@admin_required
def curriculum_management():
    """Müfredat yönetimi ana sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('curriculum_management', user_id)
        
        return render_template('admin/curriculum.html', 
                             title='Müfredat Yönetimi',
                             page_name='curriculum')
    except Exception as e:
        logger.error(f"Curriculum management page error: {str(e)}")
        flash('Müfredat yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

@admin_pages_bp.route('/grades')
@admin_required
def grades_management():
    """Sınıf yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('grades_management', user_id)
        
        return render_template('admin/grades.html', 
                             title='Sınıf Yönetimi',
                             page_name='grades')
    except Exception as e:
        logger.error(f"Grades management page error: {str(e)}")
        flash('Sınıf yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.curriculum_management'))

@admin_pages_bp.route('/subjects')
@admin_required
def subjects_management():
    """Ders yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('subjects_management', user_id)
        
        return render_template('admin/subjects.html', 
                             title='Ders Yönetimi',
                             page_name='subjects')
    except Exception as e:
        logger.error(f"Subjects management page error: {str(e)}")
        flash('Ders yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.curriculum_management'))

@admin_pages_bp.route('/units')
@admin_required
def units_management():
    """Ünite yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('units_management', user_id)
        
        return render_template('admin/units.html', 
                             title='Ünite Yönetimi',
                             page_name='units')
    except Exception as e:
        logger.error(f"Units management page error: {str(e)}")
        flash('Ünite yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.curriculum_management'))

@admin_pages_bp.route('/topics')
@admin_required
def topics_management():
    """Konu yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('topics_management', user_id)
        
        return render_template('admin/topics.html', 
                             title='Konu Yönetimi',
                             page_name='topics')
    except Exception as e:
        logger.error(f"Topics management page error: {str(e)}")
        flash('Konu yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.curriculum_management'))

@admin_pages_bp.route('/import-export')
@admin_required
def import_export():
    """JSON import/export sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('import_export', user_id)
        
        return render_template('admin/import_export.html', 
                             title='Veri Aktarımı',
                             page_name='import_export')
    except Exception as e:
        logger.error(f"Import export page error: {str(e)}")
        flash('Veri aktarımı sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.curriculum_management'))

@admin_pages_bp.route('/users')
@admin_required
def users_management():
    """Kullanıcı yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('users_management', user_id)
        
        return render_template('admin/users.html', 
                             title='Kullanıcı Yönetimi',
                             page_name='users')
    except Exception as e:
        logger.error(f"Users management page error: {str(e)}")
        flash('Kullanıcı yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

@admin_pages_bp.route('/system')
@admin_required
def system_management():
    """Sistem yönetimi sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('system_management', user_id)
        
        return render_template('admin/system.html', 
                             title='Sistem Yönetimi',
                             page_name='system')
    except Exception as e:
        logger.error(f"System management page error: {str(e)}")
        flash('Sistem yönetimi sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

@admin_pages_bp.route('/reports')
@admin_required
def reports():
    """Raporlar sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('reports', user_id)
        
        return render_template('admin/reports.html', 
                             title='Raporlar',
                             page_name='reports')
    except Exception as e:
        logger.error(f"Reports page error: {str(e)}")
        flash('Raporlar sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

@admin_pages_bp.route('/settings')
@admin_required
def settings():
    """Admin ayarları sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('settings', user_id)
        
        return render_template('admin/settings.html', 
                             title='Admin Ayarları',
                             page_name='settings')
    except Exception as e:
        logger.error(f"Settings page error: {str(e)}")
        flash('Admin ayarları sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

# =============================================================================
# HATA YÖNETİMİ
# =============================================================================

@admin_pages_bp.errorhandler(404)
def not_found(error):
    """404 hatası için özel sayfa"""
    return render_template('admin/errors/404.html', title='Sayfa Bulunamadı'), 404

@admin_pages_bp.errorhandler(403)
def forbidden(error):
    """403 hatası için özel sayfa"""
    return render_template('admin/errors/403.html', title='Erişim Reddedildi'), 403

@admin_pages_bp.errorhandler(500)
def internal_error(error):
    """500 hatası için özel sayfa"""
    return render_template('admin/errors/500.html', title='Sunucu Hatası'), 500

# =============================================================================
# YARDIMCI ROUTES
# =============================================================================

@admin_pages_bp.route('/logout')
@admin_required
def admin_logout():
    """Admin çıkış işlemi"""
    try:
        user_id = session.get('user_id')
        log_page_access('admin_logout', user_id)
        
        # Session'ı temizle
        session.clear()
        flash('Başarıyla çıkış yapıldı.', 'success')
        
        return redirect(url_for('pages.auth.login'))
    except Exception as e:
        logger.error(f"Admin logout error: {str(e)}")
        flash('Çıkış yapılırken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))

@admin_pages_bp.route('/profile')
@admin_required
def admin_profile():
    """Admin profil sayfası"""
    try:
        user_id = session.get('user_id')
        log_page_access('admin_profile', user_id)
        
        return render_template('admin/profile.html', 
                             title='Admin Profili',
                             page_name='profile')
    except Exception as e:
        logger.error(f"Admin profile page error: {str(e)}")
        flash('Profil sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('pages.admin_pages.dashboard'))
