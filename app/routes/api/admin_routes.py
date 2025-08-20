"""
Admin API Routes - Modern & Clean Implementation
Handles all admin panel API endpoints with proper authentication and error handling
"""

from flask import Blueprint, jsonify, request, session
from functools import wraps
import logging
from typing import Dict, List, Any, Optional

# Import services
from app.services.admin_service import AdminService
from app.services.auth_service import AuthenticationService
from app.utils.response_utils import success_response, error_response
from app.utils.validation_utils import validate_required_fields

# Setup logging
logger = logging.getLogger(__name__)

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize services
admin_service = AdminService()
auth_service = AuthenticationService()

# =============================================================================
# DECORATORS
# =============================================================================

def admin_required(f):
    """Admin yetkisi gerektiren endpoint'ler için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in
        if not session.get('logged_in'):
            return error_response('Oturum bulunamadı', 401)
        
        # Then check if user is admin
        if not session.get('is_admin'):
            return error_response('Admin yetkisi gerekli', 403)
        
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# DASHBOARD & OVERVIEW
# =============================================================================

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Dashboard istatistiklerini getirir"""
    try:
        stats = admin_service.get_dashboard_stats()
        return success_response('Dashboard verileri başarıyla yüklendi', stats)
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return error_response('Dashboard verileri yüklenirken hata oluştu', 500)

@admin_bp.route('/dashboard/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    """Son aktiviteleri getirir"""
    try:
        limit = request.args.get('limit', 10, type=int)
        activity = admin_service.get_recent_activity(limit)
        return success_response('Son aktiviteler yüklendi', activity)
    except Exception as e:
        logger.error(f"Recent activity error: {str(e)}")
        return error_response('Aktivite verileri yüklenirken hata oluştu', 500)

# =============================================================================
# CURRICULUM OVERVIEW
# =============================================================================

@admin_bp.route('/curriculum/overview', methods=['GET'])
@admin_required
def get_curriculum_overview():
    """Curriculum genel bakış verilerini getirir"""
    print("=== ADMIN CURRICULUM OVERVIEW DEBUG ===")
    print(f"Session content: {session}")
    print(f"Logged in: {session.get('logged_in')}")
    print(f"Is admin: {session.get('is_admin')}")
    print(f"User ID: {session.get('user_id')}")
    print("=====================================")
    
    try:
        overview = admin_service.get_curriculum_overview()
        return success_response('Curriculum verileri başarıyla yüklendi', overview)
    except Exception as e:
        logger.error(f"Curriculum overview error: {str(e)}")
        return error_response('Curriculum verileri yüklenirken hata oluştu', 500)

# =============================================================================
# GRADES MANAGEMENT
# =============================================================================

@admin_bp.route('/grades', methods=['GET'])
@admin_required
def get_grades():
    """Tüm sınıfları getirir"""
    try:
        grades = admin_service.get_all_grades()
        return success_response('Sınıflar başarıyla yüklendi', grades)
    except Exception as e:
        logger.error(f"Get grades error: {str(e)}")
        return error_response('Sınıflar yüklenirken hata oluştu', 500)

@admin_bp.route('/grades', methods=['POST'])
@admin_required
def create_grade():
    """Yeni sınıf oluşturur"""
    try:
        data = request.get_json()
        required_fields = ['grade_name', 'grade_level']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        grade = admin_service.create_grade(data)
        return success_response('Sınıf başarıyla oluşturuldu', grade, 201)
    except Exception as e:
        logger.error(f"Create grade error: {str(e)}")
        return error_response('Sınıf oluşturulurken hata oluştu', 500)

@admin_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@admin_required
def update_grade(grade_id: int):
    """Sınıf bilgilerini günceller"""
    try:
        data = request.get_json()
        required_fields = ['grade_name', 'grade_level']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        grade = admin_service.update_grade(grade_id, data)
        if not grade:
            return error_response('Sınıf bulunamadı', 404)
        
        return success_response('Sınıf başarıyla güncellendi', grade)
    except Exception as e:
        logger.error(f"Update grade error: {str(e)}")
        return error_response('Sınıf güncellenirken hata oluştu', 500)

@admin_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@admin_required
def delete_grade(grade_id: int):
    """Sınıfı siler"""
    try:
        success = admin_service.delete_grade(grade_id)
        if not success:
            return error_response('Sınıf bulunamadı veya silinemez', 404)
        
        return success_response('Sınıf başarıyla silindi')
    except Exception as e:
        logger.error(f"Delete grade error: {str(e)}")
        return error_response('Sınıf silinirken hata oluştu', 500)

# =============================================================================
# SUBJECTS MANAGEMENT
# =============================================================================

@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    """Tüm dersleri getirir"""
    print("=== ADMIN SUBJECTS DEBUG ===")
    print(f"Session content: {session}")
    print(f"Logged in: {session.get('logged_in')}")
    print(f"Is admin: {session.get('is_admin')}")
    print(f"User ID: {session.get('user_id')}")
    print("===========================")
    
    try:
        subjects = admin_service.get_all_subjects()
        return success_response('Dersler başarıyla yüklendi', subjects)
    except Exception as e:
        logger.error(f"Get subjects error: {str(e)}")
        return error_response('Dersler yüklenirken hata oluştu', 500)

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Yeni ders oluşturur"""
    try:
        data = request.get_json()
        required_fields = ['subject_name', 'grade_id', 'description']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        subject = admin_service.create_subject(data)
        return success_response('Ders başarıyla oluşturuldu', subject, 201)
    except Exception as e:
        logger.error(f"Create subject error: {str(e)}")
        return error_response('Ders oluşturulurken hata oluştu', 500)

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id: int):
    """Ders bilgilerini günceller"""
    try:
        data = request.get_json()
        required_fields = ['subject_name', 'grade_id', 'description']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        subject = admin_service.update_subject(subject_id, data)
        if not subject:
            return error_response('Ders bulunamadı', 404)
        
        return success_response('Ders başarıyla güncellendi', subject)
    except Exception as e:
        logger.error(f"Update subject error: {str(e)}")
        return error_response('Ders güncellenirken hata oluştu', 500)

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id: int):
    """Dersi siler"""
    try:
        success = admin_service.delete_subject(subject_id)
        if not success:
            return error_response('Ders bulunamadı veya silinemez', 404)
        
        return success_response('Ders başarıyla silindi')
    except Exception as e:
        logger.error(f"Delete subject error: {str(e)}")
        return error_response('Ders silinirken hata oluştu', 500)

# =============================================================================
# UNITS MANAGEMENT
# =============================================================================

@admin_bp.route('/units', methods=['GET'])
@admin_required
def get_units():
    """Tüm üniteleri getirir"""
    try:
        units = admin_service.get_all_units()
        return success_response('Üniteler başarıyla yüklendi', units)
    except Exception as e:
        logger.error(f"Get units error: {str(e)}")
        return error_response('Üniteler yüklenirken hata oluştu', 500)

@admin_bp.route('/units', methods=['POST'])
@admin_required
def create_unit():
    """Yeni ünite oluşturur"""
    try:
        data = request.get_json()
        required_fields = ['unit_name', 'subject_id', 'unit_number']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        unit = admin_service.create_unit(data)
        return success_response('Ünite başarıyla oluşturuldu', unit, 201)
    except Exception as e:
        logger.error(f"Create unit error: {str(e)}")
        return error_response('Ünite oluşturulurken hata oluştu', 500)

@admin_bp.route('/units/<int:unit_id>', methods=['PUT'])
@admin_required
def update_unit(unit_id: int):
    """Ünite bilgilerini günceller"""
    try:
        data = request.get_json()
        required_fields = ['unit_name', 'subject_id', 'unit_number']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        unit = admin_service.update_unit(unit_id, data)
        if not unit:
            return error_response('Ünite bulunamadı', 404)
        
        return success_response('Ünite başarıyla güncellendi', unit)
    except Exception as e:
        logger.error(f"Update unit error: {str(e)}")
        return error_response('Ünite güncellenirken hata oluştu', 500)

@admin_bp.route('/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id: int):
    """Üniteyi siler"""
    try:
        success = admin_service.delete_unit(unit_id)
        if not success:
            return error_response('Ünite bulunamadı veya silinemez', 404)
        
        return success_response('Ünite başarıyla silindi')
    except Exception as e:
        logger.error(f"Delete unit error: {str(e)}")
        return error_response('Ünite silinirken hata oluştu', 500)

# =============================================================================
# TOPICS MANAGEMENT
# =============================================================================

@admin_bp.route('/topics', methods=['GET'])
@admin_required
def get_topics():
    """Tüm konuları getirir"""
    try:
        topics = admin_service.get_all_topics()
        return success_response('Konular başarıyla yüklendi', topics)
    except Exception as e:
        logger.error(f"Get topics error: {str(e)}")
        return error_response('Konular yüklenirken hata oluştu', 500)

@admin_bp.route('/topics', methods=['POST'])
@admin_required
def create_topic():
    """Yeni konu oluşturur"""
    try:
        data = request.get_json()
        required_fields = ['topic_name', 'unit_id', 'topic_number']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        topic = admin_service.create_topic(data)
        return success_response('Konu başarıyla oluşturuldu', topic, 201)
    except Exception as e:
        logger.error(f"Create topic error: {str(e)}")
        return error_response('Konu oluşturulurken hata oluştu', 500)

@admin_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@admin_required
def update_topic(topic_id: int):
    """Konu bilgilerini günceller"""
    try:
        data = request.get_json()
        required_fields = ['topic_name', 'unit_id', 'topic_number']
        
        if not validate_required_fields(data, required_fields):
            return error_response('Gerekli alanlar eksik', 400)
        
        topic = admin_service.update_topic(topic_id, data)
        if not topic:
            return error_response('Konu bulunamadı', 404)
        
        return success_response('Konu başarıyla güncellendi', topic)
    except Exception as e:
        logger.error(f"Update topic error: {str(e)}")
        return error_response('Konu güncellenirken hata oluştu', 500)

@admin_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
@admin_required
def delete_topic(topic_id: int):
    """Konuyu siler"""
    try:
        success = admin_service.delete_topic(topic_id)
        if not success:
            return error_response('Konu bulunamadı veya silinemez', 404)
        
        return success_response('Konu başarıyla silindi')
    except Exception as e:
        logger.error(f"Delete topic error: {str(e)}")
        return error_response('Konu silinirken hata oluştu', 500)

# =============================================================================
# USERS MANAGEMENT
# =============================================================================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Tüm kullanıcıları getirir"""
    try:
        users = admin_service.get_all_users()
        return success_response('Kullanıcılar başarıyla yüklendi', users)
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return error_response('Kullanıcılar yüklenirken hata oluştu', 500)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id: int):
    """Kullanıcı bilgilerini günceller"""
    try:
        data = request.get_json()
        user = admin_service.update_user(user_id, data)
        if not user:
            return error_response('Kullanıcı bulunamadı', 404)
        
        return success_response('Kullanıcı başarıyla güncellendi', user)
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return error_response('Kullanıcı güncellenirken hata oluştu', 500)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin_status(user_id: int):
    """Kullanıcının admin durumunu değiştirir"""
    try:
        success = admin_service.toggle_admin_status(user_id)
        if not success:
            return error_response('Kullanıcı bulunamadı', 404)
        
        return success_response('Admin durumu başarıyla güncellendi')
    except Exception as e:
        logger.error(f"Toggle admin status error: {str(e)}")
        return error_response('Admin durumu güncellenirken hata oluştu', 500)

# =============================================================================
# IMPORT/EXPORT
# =============================================================================

@admin_bp.route('/export/curriculum', methods=['GET'])
@admin_required
def export_curriculum():
    """Müfredat verilerini CSV olarak export eder"""
    try:
        format_type = request.args.get('format', 'csv')
        data = admin_service.export_curriculum(format_type)
        return success_response('Müfredat başarıyla export edildi', data)
    except Exception as e:
        logger.error(f"Export curriculum error: {str(e)}")
        return error_response('Export işlemi sırasında hata oluştu', 500)

@admin_bp.route('/import/curriculum', methods=['POST'])
@admin_required
def import_curriculum():
    """CSV dosyasından müfredat verilerini import eder"""
    try:
        if 'file' not in request.files:
            return error_response('Dosya bulunamadı', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('Dosya seçilmedi', 400)
        
        result = admin_service.import_curriculum(file)
        return success_response('Müfredat başarıyla import edildi', result)
    except Exception as e:
        logger.error(f"Import curriculum error: {str(e)}")
        return error_response('Import işlemi sırasında hata oluştu', 500)

# =============================================================================
# SYSTEM & UTILITIES
# =============================================================================

@admin_bp.route('/system/status', methods=['GET'])
@admin_required
def get_system_status():
    """Sistem durumunu getirir"""
    try:
        status = admin_service.get_system_status()
        return success_response('Sistem durumu alındı', status)
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return error_response('Sistem durumu alınırken hata oluştu', 500)

@admin_bp.route('/refresh-session', methods=['POST'])
@admin_required
def refresh_admin_session():
    """Admin session'ını yeniler"""
    try:
        success = auth_service.refresh_session()
        if success:
            return success_response('Session yenilendi', {
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email'),
                'is_admin': session.get('is_admin')
            })
        else:
            return error_response('Session yenilenemedi', 500)
    except Exception as e:
        logger.error(f"Session refresh error: {str(e)}")
        return error_response('Session yenilenirken hata oluştu', 500)

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@admin_bp.errorhandler(404)
def not_found(error):
    """404 hatası için özel response"""
    return error_response('Endpoint bulunamadı', 404)

@admin_bp.errorhandler(500)
def internal_error(error):
    """500 hatası için özel response"""
    return error_response('Sunucu hatası', 500)
