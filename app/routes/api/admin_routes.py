# =============================================================================
# ADMIN ROUTES
# =============================================================================
# Admin paneli için API rotaları
# Müfredat yönetimi ve sistem yönetimi endpoint'leri
# =============================================================================

from flask import Blueprint, request, jsonify
from app.services.curriculum_service import CurriculumService
from app.services.auth_service import AuthenticationService
from functools import wraps

# Blueprint oluştur
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Servis instance'ları
curriculum_service = CurriculumService()
auth_service = AuthenticationService()

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Development mode - bypass auth for now
        # TODO: Implement proper JWT token authentication
        return f(*args, **kwargs)
        
        # Production auth code (commented out for development)
        # auth_header = request.headers.get('Authorization')
        # if not auth_header:
        #     return jsonify({'error': 'Yetkilendirme gerekli'}), 401
        # 
        # try:
        #     token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        #     user = auth_service.verify_token(token)
        #     if not user or not user.get('is_admin'):
        #         return jsonify({'error': 'Admin yetkisi gerekli'}), 403
        # except:
        #     return jsonify({'error': 'Geçersiz token'}), 401
        # 
        # return f(*args, **kwargs)
    return decorated_function

def handle_response(success, data=None, message=None, status_code=200):
    """Standart API response formatı"""
    response = {'success': success}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status_code

# =============================================================================
# DASHBOARD VE İSTATİSTİKLER
# =============================================================================

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Admin dashboard istatistikleri"""
    try:
        stats = curriculum_service.get_curriculum_statistics()
        return handle_response(True, stats, "Dashboard verileri başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Dashboard verileri alınırken hata: {str(e)}", status_code=500)

# =============================================================================
# GRADES (SINIFLAR) YÖNETİMİ
# =============================================================================

@admin_bp.route('/grades', methods=['GET'])
@admin_required
def get_grades():
    """Tüm sınıfları listele"""
    try:
        grades = curriculum_service.get_all_grades()
        return handle_response(True, grades, "Sınıflar başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Sınıflar getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/grades/active', methods=['GET'])
@admin_required
def get_active_grades():
    """Aktif sınıfları listele"""
    try:
        grades = curriculum_service.get_all_grades()
        active_grades = [g for g in grades if g.get('is_active', True)]
        return handle_response(True, active_grades, "Aktif sınıflar başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Aktif sınıflar getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/grades/<int:grade_id>', methods=['GET'])
@admin_required
def get_grade(grade_id):
    """Belirli bir sınıfı getir"""
    try:
        grade = curriculum_service.get_grade_by_id(grade_id)
        if not grade:
            return handle_response(False, message="Sınıf bulunamadı", status_code=404)
        return handle_response(True, grade, "Sınıf başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Sınıf getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/grades', methods=['POST'])
@admin_required
def create_grade():
    """Yeni sınıf oluştur"""
    try:
        data = request.get_json()
        if not data or not data.get('grade_name'):
            return handle_response(False, message="Sınıf adı gerekli", status_code=400)
        
        grade_id = curriculum_service.create_grade(
            grade_name=data['grade_name'],
            description=data.get('description')
        )
        
        return handle_response(True, {'grade_id': grade_id}, "Sınıf başarıyla oluşturuldu", 201)
    except Exception as e:
        return handle_response(False, message=f"Sınıf oluşturulurken hata: {str(e)}", status_code=500)

@admin_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@admin_required
def update_grade(grade_id):
    """Sınıf bilgilerini güncelle"""
    try:
        data = request.get_json()
        if not data or not data.get('grade_name'):
            return handle_response(False, message="Sınıf adı gerekli", status_code=400)
        
        success = curriculum_service.update_grade(
            grade_id=grade_id,
            grade_name=data['grade_name'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        if success:
            return handle_response(True, message="Sınıf başarıyla güncellendi")
        else:
            return handle_response(False, message="Sınıf güncellenemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Sınıf güncellenirken hata: {str(e)}", status_code=500)

@admin_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@admin_required
def delete_grade(grade_id):
    """Sınıfı sil"""
    try:
        success = curriculum_service.delete_grade(grade_id)
        if success:
            return handle_response(True, message="Sınıf başarıyla silindi")
        else:
            return handle_response(False, message="Sınıf silinemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Sınıf silinirken hata: {str(e)}", status_code=500)

# =============================================================================
# SUBJECTS (DERSLER) YÖNETİMİ
# =============================================================================

@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    """Tüm dersleri listele"""
    try:
        grade_id = request.args.get('grade_id', type=int)
        if grade_id:
            subjects = curriculum_service.get_subjects_by_grade(grade_id)
        else:
            subjects = curriculum_service.get_all_subjects()
        return handle_response(True, subjects, "Dersler başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Dersler getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/subjects/active', methods=['GET'])
@admin_required
def get_active_subjects():
    """Aktif dersleri listele"""
    try:
        subjects = curriculum_service.get_all_subjects()
        active_subjects = [s for s in subjects if s.get('is_active', True)]
        return handle_response(True, active_subjects, "Aktif dersler başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Aktif dersler getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    """Belirli bir dersi getir"""
    try:
        subject = curriculum_service.get_subject_by_id(subject_id)
        if not subject:
            return handle_response(False, message="Ders bulunamadı", status_code=404)
        return handle_response(True, subject, "Ders başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Ders getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Yeni ders oluştur"""
    try:
        data = request.get_json()
        if not data or not data.get('subject_name') or not data.get('grade_id'):
            return handle_response(False, message="Ders adı ve sınıf ID'si gerekli", status_code=400)
        
        subject_id = curriculum_service.create_subject(
            grade_id=data['grade_id'],
            subject_name=data['subject_name'],
            description=data.get('description')
        )
        
        return handle_response(True, {'subject_id': subject_id}, "Ders başarıyla oluşturuldu", 201)
    except Exception as e:
        return handle_response(False, message=f"Ders oluşturulurken hata: {str(e)}", status_code=500)

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    """Ders bilgilerini güncelle"""
    try:
        data = request.get_json()
        if not data or not data.get('subject_name') or not data.get('grade_id'):
            return handle_response(False, message="Ders adı ve sınıf ID'si gerekli", status_code=400)
        
        success = curriculum_service.update_subject(
            subject_id=subject_id,
            grade_id=data['grade_id'],
            subject_name=data['subject_name'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        if success:
            return handle_response(True, message="Ders başarıyla güncellendi")
        else:
            return handle_response(False, message="Ders güncellenemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Ders güncellenirken hata: {str(e)}", status_code=500)

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    """Dersi sil"""
    try:
        success = curriculum_service.delete_subject(subject_id)
        if success:
            return handle_response(True, message="Ders başarıyla silindi")
        else:
            return handle_response(False, message="Ders silinemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Ders silinirken hata: {str(e)}", status_code=500)

# =============================================================================
# UNITS (ÜNİTELER) YÖNETİMİ
# =============================================================================

@admin_bp.route('/units', methods=['GET'])
@admin_required
def get_units():
    """Tüm üniteleri listele"""
    try:
        subject_id = request.args.get('subject_id', type=int)
        if subject_id:
            units = curriculum_service.get_units_by_subject(subject_id)
        else:
            units = curriculum_service.get_all_units()
        return handle_response(True, units, "Üniteler başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Üniteler getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/units/<int:unit_id>', methods=['GET'])
@admin_required
def get_unit(unit_id):
    """Belirli bir üniteyi getir"""
    try:
        unit = curriculum_service.get_unit_by_id(unit_id)
        if not unit:
            return handle_response(False, message="Ünite bulunamadı", status_code=404)
        return handle_response(True, unit, "Ünite başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Ünite getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/units', methods=['POST'])
@admin_required
def create_unit():
    """Yeni ünite oluştur"""
    try:
        data = request.get_json()
        if not data or not data.get('unit_name') or not data.get('subject_id'):
            return handle_response(False, message="Ünite adı ve ders ID'si gerekli", status_code=400)
        
        unit_id = curriculum_service.create_unit(
            subject_id=data['subject_id'],
            unit_name=data['unit_name'],
            description=data.get('description'),
            order_number=data.get('order_number')
        )
        
        return handle_response(True, {'unit_id': unit_id}, "Ünite başarıyla oluşturuldu", 201)
    except Exception as e:
        return handle_response(False, message=f"Ünite oluşturulurken hata: {str(e)}", status_code=500)

@admin_bp.route('/units/<int:unit_id>', methods=['PUT'])
@admin_required
def update_unit(unit_id):
    """Ünite bilgilerini güncelle"""
    try:
        data = request.get_json()
        if not data or not data.get('unit_name') or not data.get('subject_id'):
            return handle_response(False, message="Ünite adı ve ders ID'si gerekli", status_code=400)
        
        success = curriculum_service.update_unit(
            unit_id=unit_id,
            subject_id=data['subject_id'],
            unit_name=data['unit_name'],
            description=data.get('description'),
            is_active=data.get('is_active', True),
            order_number=data.get('order_number')
        )
        
        if success:
            return handle_response(True, message="Ünite başarıyla güncellendi")
        else:
            return handle_response(False, message="Ünite güncellenemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Ünite güncellenirken hata: {str(e)}", status_code=500)

@admin_bp.route('/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id):
    """Üniteyi sil"""
    try:
        success = curriculum_service.delete_unit(unit_id)
        if success:
            return handle_response(True, message="Ünite başarıyla silindi")
        else:
            return handle_response(False, message="Ünite silinemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Ünite silinirken hata: {str(e)}", status_code=500)

# =============================================================================
# TOPICS (KONULAR) YÖNETİMİ
# =============================================================================

@admin_bp.route('/topics', methods=['GET'])
@admin_required
def get_topics():
    """Tüm konuları listele"""
    try:
        unit_id = request.args.get('unit_id', type=int)
        if unit_id:
            topics = curriculum_service.get_topics_by_unit(unit_id)
        else:
            topics = curriculum_service.get_all_topics()
        return handle_response(True, topics, "Konular başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Konular getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/topics/<int:topic_id>', methods=['GET'])
@admin_required
def get_topic(topic_id):
    """Belirli bir konuyu getir"""
    try:
        topic = curriculum_service.get_topic_by_id(topic_id)
        if not topic:
            return handle_response(False, message="Konu bulunamadı", status_code=404)
        return handle_response(True, topic, "Konu başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"Konu getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/topics', methods=['POST'])
@admin_required
def create_topic():
    """Yeni konu oluştur"""
    try:
        data = request.get_json()
        if not data or not data.get('topic_name') or not data.get('unit_id'):
            return handle_response(False, message="Konu adı ve ünite ID'si gerekli", status_code=400)
        
        topic_id = curriculum_service.create_topic(
            unit_id=data['unit_id'],
            topic_name=data['topic_name'],
            description=data.get('description')
        )
        
        return handle_response(True, {'topic_id': topic_id}, "Konu başarıyla oluşturuldu", 201)
    except Exception as e:
        return handle_response(False, message=f"Konu oluşturulurken hata: {str(e)}", status_code=500)

@admin_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@admin_required
def update_topic(topic_id):
    """Konu bilgilerini güncelle"""
    try:
        data = request.get_json()
        if not data or not data.get('topic_name') or not data.get('unit_id'):
            return handle_response(False, message="Konu adı ve ünite ID'si gerekli", status_code=400)
        
        success = curriculum_service.update_topic(
            topic_id=topic_id,
            unit_id=data['unit_id'],
            topic_name=data['topic_name'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        if success:
            return handle_response(True, message="Konu başarıyla güncellendi")
        else:
            return handle_response(False, message="Konu güncellenemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Konu güncellenirken hata: {str(e)}", status_code=500)

@admin_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
@admin_required
def delete_topic(topic_id):
    """Konuyu sil"""
    try:
        success = curriculum_service.delete_topic(topic_id)
        if success:
            return handle_response(True, message="Konu başarıyla silindi")
        else:
            return handle_response(False, message="Konu silinemedi", status_code=404)
    except Exception as e:
        return handle_response(False, message=f"Konu silinirken hata: {str(e)}", status_code=500)

# =============================================================================
# JSON DOSYALARI YÖNETİMİ
# =============================================================================

@admin_bp.route('/curriculum/json-files', methods=['GET'])
@admin_required
def get_json_files():
    """Mevcut JSON müfredat dosyalarını listele"""
    try:
        files = curriculum_service.get_curriculum_json_files()
        return handle_response(True, files, "JSON dosyaları başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"JSON dosyaları getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/curriculum/json/<filename>', methods=['GET'])
@admin_required
def get_json_content(filename):
    """JSON dosyası içeriğini getir"""
    try:
        content = curriculum_service.load_curriculum_from_json(filename)
        if content is None:
            return handle_response(False, message="JSON dosyası bulunamadı veya okunamadı", status_code=404)
        return handle_response(True, content, "JSON içeriği başarıyla getirildi")
    except Exception as e:
        return handle_response(False, message=f"JSON içeriği getirilirken hata: {str(e)}", status_code=500)

@admin_bp.route('/curriculum/import/<filename>', methods=['POST'])
@admin_required
def import_json_to_db(filename):
    """JSON dosyasından veritabanına aktarım"""
    try:
        result = curriculum_service.import_json_to_database(filename)
        if result['success']:
            return handle_response(True, result['imported'], result['message'])
        else:
            return handle_response(False, message=result['message'], status_code=400)
    except Exception as e:
        return handle_response(False, message=f"JSON aktarımında hata: {str(e)}", status_code=500)

@admin_bp.route('/curriculum/export/<int:grade_id>', methods=['GET'])
@admin_required
def export_db_to_json(grade_id):
    """Veritabanından JSON formatında export"""
    try:
        data = curriculum_service.export_database_to_json(grade_id)
        if data is None:
            return handle_response(False, message="Sınıf bulunamadı veya export edilemedi", status_code=404)
        return handle_response(True, data, "Veriler başarıyla export edildi")
    except Exception as e:
        return handle_response(False, message=f"Export işleminde hata: {str(e)}", status_code=500)

@admin_bp.route('/curriculum/save-json', methods=['POST'])
@admin_required
def save_json_file():
    """JSON dosyasını kaydet"""
    try:
        data = request.get_json()
        if not data or not data.get('filename') or not data.get('content'):
            return handle_response(False, message="Dosya adı ve içerik gerekli", status_code=400)
        
        success = curriculum_service.save_curriculum_to_json(data['filename'], data['content'])
        if success:
            return handle_response(True, message="JSON dosyası başarıyla kaydedildi")
        else:
            return handle_response(False, message="JSON dosyası kaydedilemedi", status_code=500)
    except Exception as e:
        return handle_response(False, message=f"JSON kaydetme hatası: {str(e)}", status_code=500)

# =============================================================================
# HATA YÖNETİMİ
# =============================================================================

@admin_bp.errorhandler(404)
def not_found(error):
    return handle_response(False, message="Endpoint bulunamadı", status_code=404)

@admin_bp.errorhandler(405)
def method_not_allowed(error):
    return handle_response(False, message="HTTP metodu desteklenmiyor", status_code=405)

@admin_bp.errorhandler(500)
def internal_error(error):
    return handle_response(False, message="Sunucu hatası", status_code=500)
