# =============================================================================
# ADMIN API ROUTES
# =============================================================================
# Admin paneli için API rotaları
# Sadece müfredat CRUD işlemleri
# =============================================================================

from flask import Blueprint, request, jsonify
from app.services.admin_service import AdminService
from app.services.curriculum_service import CurriculumService
from functools import wraps
import logging

# Blueprint oluştur
admin_bp = Blueprint('admin', __name__, url_prefix='')

# Servis instance'ları
admin_service = AdminService()
curriculum_service = CurriculumService()

# Logging
logger = logging.getLogger(__name__)

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # DEBUG: API decorator'a gelen session bilgilerini print yap (sadece development modunda)
        from flask import session, current_app
        if current_app.debug:
            print("=== API ADMIN_REQUIRED DECORATOR DEBUG ===")
            print(f"Session data: {dict(session)}")
            print(f"user_id: {session.get('user_id')}")
            print(f"user_id: {session.get('user_id')}")
            print(f"is_admin: {session.get('is_admin')}")
            print(f"logged_in: {session.get('logged_in')}")
            print(f"username: {session.get('username')}")
            print("=========================================")
        
        # Development mode - bypass auth for now
        # TODO: Production'da gerçek auth kontrolü ekle
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# MÜFREDAT GENEL BAKIŞ
# =============================================================================

@admin_bp.route('/admin/curriculum/overview', methods=['GET'])
@admin_required
def get_curriculum_overview():
    """Müfredat genel bakış"""
    try:
        # DEBUG: API endpoint'e gelen session bilgilerini print yap (sadece development modunda)
        from flask import session, current_app
        if current_app.debug:
            print("=== CURRICULUM OVERVIEW API DEBUG ===")
            print(f"Session data: {dict(session)}")
            print(f"user_id: {session.get('user_id')}")
            print(f"is_admin: {session.get('is_admin')}")
            print(f"logged_in: {session.get('logged_in')}")
            print(f"username: {session.get('username')}")
            print("=====================================")
        
        overview = admin_service.get_curriculum_overview()
        if current_app.debug:
            print(f"Curriculum overview data: {overview}")
        return jsonify(overview)
    except Exception as e:
        logger.error(f"Curriculum overview error: {str(e)}")
        return jsonify({
            'total_grades': 0,
            'total_subjects': 0,
            'total_units': 0,
            'total_topics': 0
        })

# =============================================================================
# GRADES (SINIFLAR) YÖNETİMİ
# =============================================================================

@admin_bp.route('/admin/grades', methods=['GET'])
@admin_required
def get_grades():
    """Tüm sınıfları getir"""
    try:
        grades = curriculum_service.get_all_grades()
        return jsonify(grades)
    except Exception as e:
        logger.error(f"Grades error: {str(e)}")
        return jsonify([])

@admin_bp.route('/admin/grades', methods=['POST'])
@admin_required
def create_grade():
    """Yeni sınıf oluştur"""
    try:
        data = request.get_json()
        grade_name = data.get('grade_name')
        description = data.get('description', '')
        is_active = data.get('is_active', True)
        
        if not grade_name:
            return jsonify({'error': 'Sınıf adı gerekli'}), 400
        
        grade_id = curriculum_service.create_grade(grade_name, description, is_active)
        if grade_id:
            return jsonify({'success': True, 'grade_id': grade_id})
        else:
            return jsonify({'error': 'Sınıf oluşturulamadı'}), 500
    except Exception as e:
        logger.error(f"Grade creation error: {str(e)}")
        return jsonify({'error': f'Sınıf oluşturulurken hata: {str(e)}'}), 500

@admin_bp.route('/admin/grades/<int:grade_id>', methods=['PUT'])
@admin_required
def update_grade(grade_id):
    """Sınıf güncelle"""
    try:
        data = request.get_json()
        grade_name = data.get('grade_name')
        description = data.get('description', '')
        is_active = data.get('is_active')
        
        if not grade_name:
            return jsonify({'error': 'Sınıf adı gerekli'}), 400
        
        success = curriculum_service.update_grade(grade_id, grade_name, description, is_active)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Sınıf güncellenemedi'}), 404
    except Exception as e:
        logger.error(f"Grade update error: {str(e)}")
        return jsonify({'error': f'Sınıf güncellenirken hata: {str(e)}'}), 500

@admin_bp.route('/admin/grades/<int:grade_id>', methods=['DELETE'])
@admin_required
def delete_grade(grade_id):
    """Sınıf sil"""
    try:
        success = curriculum_service.delete_grade(grade_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Sınıf silinemedi'}), 404
    except Exception as e:
        logger.error(f"Grade deletion error: {str(e)}")
        return jsonify({'error': f'Sınıf silinirken hata: {str(e)}'}), 500

# =============================================================================
# SUBJECTS (DERSLER) YÖNETİMİ
# =============================================================================

@admin_bp.route('/admin/subjects', methods=['GET'])
@admin_required
def get_subjects():
    """Tüm dersleri getir"""
    try:
        subjects = curriculum_service.get_all_subjects()
        return jsonify(subjects)
    except Exception as e:
        logger.error(f"Subjects error: {str(e)}")
        return jsonify([])

@admin_bp.route('/admin/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Yeni ders oluştur"""
    try:
        data = request.get_json()
        subject_name = data.get('subject_name')
        grade_id = data.get('grade_id')
        description = data.get('description', '')
        is_active = data.get('is_active', True)
        
        if not subject_name or not grade_id:
            return jsonify({'error': 'Ders adı ve sınıf ID gerekli'}), 400
        
        subject_id = curriculum_service.create_subject(subject_name, grade_id, description, is_active)
        if subject_id:
            return jsonify({'success': True, 'subject_id': subject_id})
        else:
            return jsonify({'error': 'Ders oluşturulamadı'}), 500
    except Exception as e:
        logger.error(f"Subject creation error: {str(e)}")
        return jsonify({'error': f'Ders oluşturulurken hata: {str(e)}'}), 500

@admin_bp.route('/admin/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    """Ders güncelle"""
    try:
        data = request.get_json()
        subject_name = data.get('subject_name')
        grade_id = data.get('grade_id')
        description = data.get('description', '')
        is_active = data.get('is_active')
        
        if not subject_name or not grade_id:
            return jsonify({'error': 'Ders adı ve sınıf ID gerekli'}), 400
        
        success = curriculum_service.update_subject(subject_id, subject_name, grade_id, description, is_active)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Ders güncellenemedi'}), 404
    except Exception as e:
        logger.error(f"Subject update error: {str(e)}")
        return jsonify({'error': f'Ders güncellenirken hata: {str(e)}'}), 500

@admin_bp.route('/admin/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    """Ders sil"""
    try:
        success = curriculum_service.delete_subject(subject_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Ders silinemedi'}), 404
    except Exception as e:
        logger.error(f"Subject deletion error: {str(e)}")
        return jsonify({'error': f'Ders silinirken hata: {str(e)}'}), 500

# =============================================================================
# UNITS (ÜNİTELER) YÖNETİMİ
# =============================================================================

@admin_bp.route('/admin/units', methods=['GET'])
@admin_required
def get_units():
    """Tüm üniteleri getir"""
    try:
        units = curriculum_service.get_all_units()
        return jsonify(units)
    except Exception as e:
        logger.error(f"Units error: {str(e)}")
        return jsonify([])

@admin_bp.route('/admin/units', methods=['POST'])
@admin_required
def create_unit():
    """Yeni ünite oluştur"""
    try:
        data = request.get_json()
        unit_name = data.get('unit_name')
        subject_id = data.get('subject_id')
        description = data.get('description', '')
        is_active = data.get('is_active', True)
        
        if not unit_name or not subject_id:
            return jsonify({'error': 'Ünite adı ve ders ID gerekli'}), 400
        
        unit_id = curriculum_service.create_unit(unit_name, subject_id, description, is_active)
        if unit_id:
            return jsonify({'success': True, 'unit_id': unit_id})
        else:
            return jsonify({'error': 'Ünite oluşturulamadı'}), 500
    except Exception as e:
        logger.error(f"Unit creation error: {str(e)}")
        return jsonify({'error': f'Ünite oluşturulurken hata: {str(e)}'}), 500

@admin_bp.route('/admin/units/<int:unit_id>', methods=['PUT'])
@admin_required
def update_unit(unit_id):
    """Ünite güncelle"""
    try:
        data = request.get_json()
        unit_name = data.get('unit_name')
        subject_id = data.get('subject_id')
        description = data.get('description', '')
        is_active = data.get('is_active')
        
        if not unit_name or not subject_id:
            return jsonify({'error': 'Ünite adı ve ders ID gerekli'}), 400
        
        success = curriculum_service.update_unit(unit_id, unit_name, subject_id, description, is_active)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Ünite güncellenemedi'}), 404
    except Exception as e:
        logger.error(f"Unit update error: {str(e)}")
        return jsonify({'error': f'Ünite güncellenirken hata: {str(e)}'}), 500

@admin_bp.route('/admin/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id):
    """Ünite sil"""
    try:
        success = curriculum_service.delete_unit(unit_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Ünite silinemedi'}), 404
    except Exception as e:
        logger.error(f"Unit deletion error: {str(e)}")
        return jsonify({'error': f'Ünite silinirken hata: {str(e)}'}), 500

# =============================================================================
# TOPICS (KONULAR) YÖNETİMİ
# =============================================================================

@admin_bp.route('/admin/topics', methods=['GET'])
@admin_required
def get_topics():
    """Tüm konuları getir"""
    try:
        topics = curriculum_service.get_all_topics()
        return jsonify(topics)
    except Exception as e:
        logger.error(f"Topics error: {str(e)}")
        return jsonify([])

@admin_bp.route('/admin/topics', methods=['POST'])
@admin_required
def create_topic():
    """Yeni konu oluştur"""
    try:
        data = request.get_json()
        topic_name = data.get('topic_name')
        unit_id = data.get('unit_id')
        description = data.get('description', '')
        is_active = data.get('is_active', True)
        
        if not topic_name or not unit_id:
            return jsonify({'error': 'Konu adı ve ünite ID gerekli'}), 400
        
        topic_id = curriculum_service.create_topic(topic_name, unit_id, description, is_active)
        if topic_id:
            return jsonify({'success': True, 'topic_id': topic_id})
        else:
            return jsonify({'error': 'Konu oluşturulamadı'}), 500
    except Exception as e:
        logger.error(f"Topic creation error: {str(e)}")
        return jsonify({'error': f'Konu oluşturulurken hata: {str(e)}'}), 500

@admin_bp.route('/admin/topics/<int:topic_id>', methods=['PUT'])
@admin_required
def update_topic(topic_id):
    """Konu güncelle"""
    try:
        data = request.get_json()
        topic_name = data.get('topic_name')
        unit_id = data.get('unit_id')
        description = data.get('description', '')
        is_active = data.get('is_active')
        
        if not topic_name or not unit_id:
            return jsonify({'error': 'Konu adı ve ünite ID gerekli'}), 400
        
        success = curriculum_service.update_topic(topic_id, topic_name, unit_id, description, is_active)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Konu güncellenemedi'}), 404
    except Exception as e:
        logger.error(f"Topic update error: {str(e)}")
        return jsonify({'error': f'Konu güncellenirken hata: {str(e)}'}), 500

@admin_bp.route('/admin/topics/<int:topic_id>', methods=['DELETE'])
@admin_required
def delete_topic(topic_id):
    """Konu sil"""
    try:
        success = curriculum_service.delete_topic(topic_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Konu silinemedi'}), 404
    except Exception as e:
        logger.error(f"Topic deletion error: {str(e)}")
        return jsonify({'error': f'Konu silinirken hata: {str(e)}'}), 500

# =============================================================================
# VERİ AKTARIMI
# =============================================================================

@admin_bp.route('/admin/import-export/export', methods=['GET'])
@admin_required
def export_curriculum():
    """Müfredat verilerini export et"""
    try:
        export_data = curriculum_service.export_curriculum_data()
        return jsonify(export_data)
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'error': f'Export işlemi sırasında hata: {str(e)}'}), 500

@admin_bp.route('/admin/import-export/import', methods=['POST'])
@admin_required
def import_curriculum():
    """Müfredat verilerini import et"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Import verisi gerekli'}), 400
        
        success = curriculum_service.import_curriculum_data(data)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Import işlemi başarısız'}), 500
    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        return jsonify({'error': f'Import işlemi sırasında hata: {str(e)}'}), 500
