# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, kullanıcı ile ilgili API rotalarını (endpoints) içerir.
# Kullanıcı kayıt, giriş, profil güncelleme gibi işlemleri yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. SERVİS BAŞLATMA
# 5.0. KULLANICI API ROTALARI (USER API ROUTES)
#   5.1. Kullanıcı Listeleme ve Oluşturma
#     5.1.1. GET /users
#     5.1.2. POST /users
#   5.2. Kimlik Doğrulama (Authentication)
#     5.2.1. POST /register
#     5.2.2. POST /login
#     5.2.3. POST /logout
#     5.2.4. GET /check-auth
#   5.3. Profil Yönetimi (Profile Management)
#     5.3.1. POST /profile/update
#     5.3.2. POST /profile/avatar
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, jsonify, request, session
from datetime import datetime

# Create the user blueprint
user_bp = Blueprint('user', __name__)

# Import services here to avoid circular imports
try:
    from app.services import get_user_service
    from app.services.auth_service import logout_user
except ImportError as e:
    get_user_service = None

# =============================================================================
# 4.0. SERVİS BAŞLATMA
# =============================================================================
# Servisler endpoint'lerde dinamik olarak alınacak

# =============================================================================
# 5.0. KULLANICI API ROTALARI (USER API ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 5.1. Kullanıcı Listeleme ve Oluşturma
# -------------------------------------------------------------------------

@user_bp.route('/users', methods=['GET'])
def get_users():
    """5.1.1. Tüm kullanıcıları listeler."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    try:
        users = user_service.get_all_users()
        return jsonify({
            'status': 'success',
            'message': 'Users retrieved successfully',
            'data': users
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve users',
            'error': str(e)
        }), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    """5.1.2. Yeni bir kullanıcı oluşturur."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    # Tüm iş mantığı servis katmanına devredildi.
    success, result = user_service.create_new_user(data)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': result
        }), 201  # 201 Created
    else:
        # Hata mesajı servisten geldiği için doğrudan kullanılır.
        return jsonify({
            'status': 'error',
            'message': result.get('message', 'An error occurred'),
            'details': result
        }), 400  # 400 Bad Request

# -------------------------------------------------------------------------
# 5.2. Kimlik Doğrulama (Authentication)
# -------------------------------------------------------------------------

@user_bp.route('/register', methods=['POST'])
def register():
    """5.2.1. Kullanıcı kayıt işlemini gerçekleştirir."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    # Register iş mantığı servis katmanına devredildi.
    success, result = user_service.register_user(data)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Kayıt başarıyla tamamlandı',
            'data': result
        }), 201  # 201 Created
    else:
        # Hata mesajı servisten geldiği için doğrudan kullanılır.
        return jsonify({
            'status': 'error',
            'message': result.get('message', 'Kayıt işlemi başarısız'),
            'details': result
        }), 400  # 400 Bad Request

@user_bp.route('/login', methods=['POST'])
def login():
    """5.2.2. Kullanıcı giriş işlemini gerçekleştirir."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    # Login iş mantığı servis katmanına devredildi.
    success, result = user_service.login_user(data)

    if success:
        # Session'a kullanıcı bilgilerini kaydet
        session['logged_in'] = True
        session['user_id'] = result['id']
        session['username'] = result['username']
        session['email'] = result['email']
        
        return jsonify({
            'status': 'success',
            'message': 'Giriş başarılı',
            'data': result
        }), 200  # 200 OK
    else:
        # Hata mesajı servisten geldiği için doğrudan kullanılır.
        return jsonify({
            'status': 'error',
            'message': result.get('message', 'Giriş işlemi başarısız'),
            'details': result
        }), 401  # 401 Unauthorized

@user_bp.route('/logout', methods=['POST'])
def logout():
    """5.2.3. Kullanıcı çıkış işlemini gerçekleştirir."""
    try:
        logout_user()
        return jsonify({
            'status': 'success',
            'message': 'Çıkış başarılı'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Çıkış işlemi başarısız',
            'error': str(e)
        }), 500

@user_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """5.2.4. Kullanıcının giriş durumunu kontrol eder."""
    if session.get('logged_in'):
        return jsonify({
            'status': 'success',
            'logged_in': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email')
            }
        }), 200
    else:
        return jsonify({
            'status': 'success',
            'logged_in': False
        }), 200

# -------------------------------------------------------------------------
# 5.3. Profil Yönetimi (Profile Management)
# -------------------------------------------------------------------------

@user_bp.route('/profile/update', methods=['POST'])
def update_profile():
    """5.3.1. Kullanıcı profil bilgilerini günceller."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Giriş yapmanız gerekiyor'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    user_id = session.get('user_id')
    success, result = user_service.update_user_profile(user_id, data)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Profil başarıyla güncellendi',
            'data': result
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': result.get('message', 'Profil güncellenemedi'),
            'details': result
        }), 400

@user_bp.route('/profile/avatar', methods=['POST'])
def upload_avatar():
    """5.3.2. Kullanıcı profil fotoğrafını yükler."""
    user_service = get_user_service()
    if not user_service:
        return jsonify({
            'status': 'error',
            'message': 'User service not available'
        }), 500
    
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Giriş yapmanız gerekiyor'}), 401
    
    # Check if file was uploaded
    if 'avatar' not in request.files:
        return jsonify({'status': 'error', 'message': 'Dosya yüklenmedi'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Dosya seçilmedi'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
        return jsonify({'status': 'error', 'message': 'Geçersiz dosya türü'}), 400

    # Validate file size (max 5MB)
    if len(file.read()) > 5 * 1024 * 1024:
        file.seek(0)  # Reset file pointer
        return jsonify({'status': 'error', 'message': 'Dosya boyutu 5MB\'dan küçük olmalıdır'}), 400
    
    file.seek(0)  # Reset file pointer for processing

    try:
        user_id = session.get('user_id')
        success, result = user_service.upload_avatar(user_id, file)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Profil fotoğrafı başarıyla yüklendi',
                'data': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Fotoğraf yüklenemedi'),
                'details': result
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Fotoğraf yüklenirken bir hata oluştu',
            'error': str(e)
        }), 500 