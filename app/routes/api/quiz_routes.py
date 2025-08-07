# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, quiz ile ilgili API rotalarını (endpoints) içerir.
# Quiz verileri, sorular, sonuçlar gibi quiz işlemlerini yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. SERVİS BAŞLATMA
# 5.0. QUIZ API ROTALARI (QUIZ API ROUTES)
#   5.1. Quiz Verileri
#     5.1.1. GET /quiz/grades
#     5.1.2. GET /quiz/subjects
#     5.1.3. GET /quiz/topics
#     5.1.4. GET /quiz/data
#   5.2. Quiz İşlemleri
#     5.2.1. POST /quiz/start
#     5.2.2. POST /quiz/submit
#     5.2.3. GET /quiz/results
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, jsonify, request, session
from datetime import datetime

# Create the quiz blueprint
quiz_bp = Blueprint('quiz', __name__)

# Import services here to avoid circular imports
try:
    from app.services import get_quiz_service
    from app.services.quiz_session_service import QuizSessionService
    from app.services.auth_service import login_required
    from app.database.db_connection import DatabaseConnection
except ImportError as e:
    get_quiz_service = None
    QuizSessionService = None
    login_required = None
    DatabaseConnection = None

# =============================================================================
# 4.0. SERVİS BAŞLATMA
# =============================================================================
# Servisler endpoint'lerde dinamik olarak alınacak

# =============================================================================
# 5.0. QUIZ API ROTALARI (QUIZ API ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 5.1. Quiz Verileri
# -------------------------------------------------------------------------

@quiz_bp.route('/quiz/grades', methods=['GET'])
def get_grades():
    """5.1.1. Tüm sınıfları listeler."""
    try:
        if not DatabaseConnection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection not available'
            }), 500
        
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT id, name, level, description 
                FROM grades 
                WHERE is_active = 1 
                ORDER BY level
            """)
            grades = conn.cursor.fetchall()
            
            # Convert to list of dictionaries
            grades_list = []
            for grade in grades:
                grades_list.append({
                    'id': grade['id'],
                    'name': grade['name'],
                    'level': grade['level'],
                    'description': grade['description']
                })
            
            return jsonify({
                'status': 'success',
                'message': 'Grades retrieved successfully',
                'data': grades_list
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve grades',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/subjects', methods=['GET'])
def get_subjects():
    """5.1.2. Belirli bir sınıfa ait dersleri listeler."""
    grade_id = request.args.get('grade_id', type=int)
    
    if not grade_id:
        return jsonify({
            'status': 'error',
            'message': 'Grade ID is required'
        }), 400
    
    try:
        if not DatabaseConnection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection not available'
            }), 500
        
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT s.id, s.name, s.name_id, s.description, g.name as grade_name
                FROM subjects s 
                JOIN grades g ON s.grade_id = g.id
                WHERE s.grade_id = %s AND s.is_active = 1 
                ORDER BY s.name
            """, (grade_id,))
            subjects = conn.cursor.fetchall()
            
            # Convert to list of dictionaries
            subjects_list = []
            for subject in subjects:
                subjects_list.append({
                    'id': subject['id'],
                    'name': subject['name'],
                    'name_id': subject['name_id'],
                    'description': subject['description'],
                    'grade_name': subject['grade_name']
                })
            
            return jsonify({
                'status': 'success',
                'message': 'Subjects retrieved successfully',
                'data': subjects_list
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve subjects',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/units', methods=['GET'])
def get_units():
    """5.1.3. Belirli bir derse ait üniteleri listeler."""
    subject_id = request.args.get('subject_id', type=int)
    
    if not subject_id:
        return jsonify({
            'status': 'error',
            'message': 'Subject ID is required'
        }), 400
    
    try:
        if not DatabaseConnection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection not available'
            }), 500
        
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT u.id, u.name, u.name_id, u.description, s.name as subject_name
                FROM units u 
                JOIN subjects s ON u.subject_id = s.id
                WHERE u.subject_id = %s AND u.is_active = 1 
                ORDER BY u.name
            """, (subject_id,))
            units = conn.cursor.fetchall()
            
            # Convert to list of dictionaries
            units_list = []
            for unit in units:
                units_list.append({
                    'id': unit['id'],
                    'name': unit['name'],
                    'name_id': unit['name_id'],
                    'description': unit['description'],
                    'subject_name': unit['subject_name']
                })
            
            return jsonify({
                'status': 'success',
                'message': 'Units retrieved successfully',
                'data': units_list
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve units',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/topics', methods=['GET'])
def get_topics():
    """5.1.4. Belirli bir üniteye ait konuları listeler."""
    unit_id = request.args.get('unit_id', type=int)
    
    if not unit_id:
        return jsonify({
            'status': 'error',
            'message': 'Unit ID is required'
        }), 400
    
    try:
        if not DatabaseConnection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection not available'
            }), 500
        
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT t.id, t.name, t.description, u.name as unit_name
                FROM topics t 
                JOIN units u ON t.unit_id = u.id
                WHERE t.unit_id = %s AND t.is_active = 1 
                ORDER BY t.name
            """, (unit_id,))
            topics = conn.cursor.fetchall()
            
            # Convert to list of dictionaries
            topics_list = []
            for topic in topics:
                topics_list.append({
                    'id': topic['id'],
                    'name': topic['name'],
                    'description': topic['description'],
                    'unit_name': topic['unit_name']
                })
            
            return jsonify({
                'status': 'success',
                'message': 'Topics retrieved successfully',
                'data': topics_list
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve topics',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/data', methods=['GET'])
def get_quiz_data():
    """5.1.4. Quiz verilerini döndürür."""
    quiz_service = get_quiz_service()
    if not quiz_service:
        return jsonify({
            'status': 'error',
            'message': 'Quiz service not available'
        }), 500
    
    try:
        quiz_data = quiz_service.get_quiz_data()
        return jsonify({
            'status': 'success',
            'message': 'Quiz data retrieved successfully',
            'data': quiz_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve quiz data',
            'error': str(e)
        }), 500

# -------------------------------------------------------------------------
# 5.2. Quiz İşlemleri
# -------------------------------------------------------------------------

@quiz_bp.route('/quiz/start', methods=['POST'])
# @login_required  # Temporarily disabled for testing
def start_quiz():
    """5.2.1. Yeni bir quiz başlatır."""
    # Temporarily bypass authentication for testing
    # if not session.get('logged_in'):
    #     return jsonify({'status': 'error', 'message': 'Giriş yapmanız gerekiyor'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
    
    # Required fields - only grade_id and subject_id are required
    required_fields = ['grade_id', 'subject_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {field}'
            }), 400
    
    # Set default values for optional fields
    if 'unit_id' not in data:
        data['unit_id'] = None
    if 'topic_id' not in data:
        data['topic_id'] = None
    
    try:
        # Use default user ID for testing
        user_id = session.get('user_id', 4)  # Default to user ID 4 for testing (existing user)
        
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        # Quiz session service'ini başlat
        session_service = QuizSessionService()
        
        # Quiz session'ı başlat
        success, result = session_service.start_quiz_session(user_id, data)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Failed to start quiz')
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz started successfully',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to start quiz',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>', methods=['GET'])
# @login_required  # Temporarily disabled for testing
def get_quiz_session(session_id):
    """5.2.2. Quiz session bilgilerini getirir."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        session_info = session_service.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Session info retrieved successfully',
            'data': session_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get session info',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/status', methods=['GET'])
# @login_required  # Temporarily disabled for testing
def get_session_status(session_id):
    """5.2.2b. Quiz session durumunu getirir."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        session_info = session_service.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        # Session durumunu hesapla
        total_questions = len(session_info['questions'])
        answered_questions = len([q for q in session_info['questions'] if q['user_answer_option_id'] is not None])
        progress_percentage = round((answered_questions / total_questions * 100) if total_questions > 0 else 0, 2)
        
        # Calculate remaining time
        remaining_time_seconds = 0
        if session_info['session']['timer_enabled'] and session_info['session']['timer_duration']:
            start_time = session_info['session']['start_time']
            timer_duration = session_info['session']['timer_duration']
            
            if start_time:
                try:
                    from datetime import datetime
                    # Handle different datetime formats
                    if isinstance(start_time, str):
                        # Remove timezone info if present and parse
                        start_time_clean = start_time.split('+')[0].split('Z')[0]
                        start_datetime = datetime.fromisoformat(start_time_clean)
                    else:
                        start_datetime = start_time
                    
                    current_datetime = datetime.now()
                    elapsed_seconds = int((current_datetime - start_datetime).total_seconds())
                    remaining_time_seconds = max(0, (timer_duration * 60) - elapsed_seconds)
                    
                    
                except Exception as e:
                    remaining_time_seconds = 0
            else:
                pass
        else:
            pass
        
        # Aktif sorunun bilgilerini al
        current_question_info = None
        if session_info['questions'] and answered_questions < total_questions:
            current_question = session_info['questions'][answered_questions]
            if current_question:
                # Aktif sorunun detaylarını al
                question_details = session_service.get_question_details(current_question['question_id'])
                if question_details:
                    current_question_info = {
                        'subject_name': question_details.get('subject_name'),
                        'topic_name': question_details.get('topic_name'),
                        'difficulty_level': question_details.get('difficulty_level')
                    }
        
        status_data = {
            'session_id': session_id,
            'is_completed': session_info['session']['status'] == 'completed',
            'timer_enabled': session_info['session']['timer_enabled'],
            'timer_duration': session_info['session']['timer_duration'],
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'progress_percentage': progress_percentage,
            'current_question': answered_questions + 1 if answered_questions < total_questions else total_questions,
            # Aktif sorunun bilgilerini kullan, yoksa session bilgilerini kullan
            'subject': current_question_info.get('subject_name') if current_question_info else session_info['session'].get('subject_name'),
            'topic': current_question_info.get('topic_name') if current_question_info else session_info['session'].get('topic_name'),
            'difficulty': current_question_info.get('difficulty_level') if current_question_info else session_info['session'].get('difficulty_level'),
            'quiz_mode': session_info['session'].get('quiz_mode'),
            'remaining_time_seconds': remaining_time_seconds
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Session status retrieved successfully',
            'data': status_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get session status',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/timer', methods=['PUT'])
# @login_required  # Temporarily disabled for testing
def update_session_timer(session_id):
    """5.2.2c. Quiz session timer'ını günceller."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        data = request.get_json()
        if not data or 'remaining_time_seconds' not in data:
            return jsonify({
                'status': 'error',
                'message': 'remaining_time_seconds is required'
            }), 400
        
        remaining_time_seconds = data['remaining_time_seconds']
        
        session_service = QuizSessionService()
        success = session_service.update_session_timer(session_id, remaining_time_seconds)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Session not found or update failed'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Timer updated successfully',
            'data': {
                'session_id': session_id,
                'remaining_time_seconds': remaining_time_seconds
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to update timer',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/questions', methods=['GET'])
# @login_required  # Temporarily disabled for testing
def get_all_questions(session_id):
    """5.2.2c. Tüm soruları getirir."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        
        # Session'ın var olup olmadığını kontrol et
        session = session_service.session_repo.get_session(session_id)
        if not session:
            return jsonify({
                'status': 'error',
                'message': f'Session not found: {session_id}'
            }), 404
        
        session_info = session_service.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Session info not available'
            }), 404
        
        # Tüm soruları hazırla
        questions = session_info['questions']
        all_questions = []
        
        for i, question in enumerate(questions):
            # Her soru için seçenekleri yükle
            question_options = session_service.get_question_options(question['question_id'])
            
            # Her soru için detayları (açıklama dahil) yükle
            question_details = session_service.get_question_details(question['question_id'])
            
            # Educational features için veri hazırla
            hint = None
            related_topics = []
            
            # Quiz modu educational ise ek verileri ekle
            if session.get('quiz_mode') == 'educational':
                # İpucu - şimdilik açıklamadan türet
                if question_details and question_details.get('description'):
                    hint = f"Bu soru için ipucu: {question_details['description'][:100]}..."
                
                # İlgili konular - şimdilik topic adından türet
                if question_details and question_details.get('topic_name'):
                    related_topics = [question_details['topic_name']]
            
            question_data = {
                'question_number': i + 1,
                'total_questions': len(questions),
                'question': {
                    'id': question['question_id'],
                    'text': question['question_text'],
                    'explanation': question_details['description'] if question_details else None,
                    'hint': hint,
                    'related_topics': related_topics,
                    'difficulty_level': question_details['difficulty_level'] if question_details else None,
                    'points': question_details['points'] if question_details else None,
                    'subject_name': question_details['subject_name'] if question_details else None,
                    'topic_name': question_details['topic_name'] if question_details else None,
                    'options': question_options
                },
                'user_answer_option_id': question['user_answer_option_id'],
                'progress': {
                    'current': i + 1,
                    'total': len(questions),
                    'percentage': round(((i + 1) / len(questions) * 100), 2)
                }
            }
            all_questions.append(question_data)
        
        return jsonify({
            'status': 'success',
            'message': 'All questions retrieved successfully',
            'data': {
                'session_id': session_id,
                'total_questions': len(questions),
                'questions': all_questions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get all questions',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/question', methods=['GET'])
# @login_required  # Temporarily disabled for testing
def get_current_question(session_id):
    """5.2.2c. Mevcut soruyu getirir."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        session_info = session_service.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        # Mevcut soruyu bul
        questions = session_info['questions']
        current_question = None
        
        for i, question in enumerate(questions):
            if question['user_answer_option_id'] is None:
                # Soru detaylarını al
                question_details = session_service.get_question_details(question['question_id'])
                
                # Educational features için veri hazırla
                hint = None
                related_topics = []
                
                # Quiz modu educational ise ek verileri ekle
                if session_info['session'].get('quiz_mode') == 'educational':
                    # İpucu - şimdilik açıklamadan türet
                    if question_details and question_details.get('description'):
                        hint = f"Bu soru için ipucu: {question_details['description'][:100]}..."
                    
                    # İlgili konular - şimdilik topic adından türet
                    if question_details and question_details.get('topic_name'):
                        related_topics = [question_details['topic_name']]
                
                current_question = {
                    'question_number': i + 1,
                    'total_questions': len(questions),
                    'question': {
                        'id': question['question_id'],
                        'text': question['question_text'],
                        'explanation': question_details['description'] if question_details else None,
                        'hint': hint,
                        'related_topics': related_topics,
                        'options': []  # Seçenekleri ayrıca yüklenecek
                    },
                    'progress': {
                        'current': i + 1,
                        'total': len(questions),
                        'percentage': round(((i + 1) / len(questions) * 100), 2)
                    }
                }
                break
        
        if not current_question:
            return jsonify({
                'status': 'error',
                'message': 'No more questions available'
            }), 404
        
        # Soru seçeneklerini yükle
        question_options = session_service.get_question_options(current_question['question']['id'])
        current_question['question']['options'] = question_options
        
        return jsonify({
            'status': 'success',
            'message': 'Current question retrieved successfully',
            'data': current_question
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get current question',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/answer', methods=['POST'])
# @login_required  # Temporarily disabled for testing
def submit_answer(session_id):
    """5.2.3. Soru cevabını gönderir."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
    
    # Required fields
    required_fields = ['question_id', 'user_answer_option_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {field}'
            }), 400
    
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        success, result = session_service.submit_answer(session_id, data['question_id'], data)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Failed to submit answer')
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Answer submitted successfully',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit answer',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/complete', methods=['POST'])
# @login_required  # Temporarily disabled for testing
def complete_quiz(session_id):
    """5.2.4. Quiz session'ı tamamlar."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        success, result = session_service.complete_session(session_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Failed to complete quiz')
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz completed successfully',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to complete quiz',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/session/<session_id>/results', methods=['GET'])
# @login_required  # Temporarily disabled for testing
def get_session_results(session_id):
    """5.2.5. Quiz session sonuçlarını getirir."""
    try:
        if not QuizSessionService:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session service not available'
            }), 500
        
        session_service = QuizSessionService()
        results = session_service.calculate_session_results(session_id)
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': 'Session results not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Session results retrieved successfully',
            'data': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get session results',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    """5.2.5. Quiz sonuçlarını gönderir (Legacy - deprecated)."""
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
    
    # Required fields
    required_fields = ['quiz_id', 'answers']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {field}'
            }), 400
    
    try:
        user_id = session.get('user_id')
        # TODO: Implement quiz submission logic
        quiz_result = {
            'quiz_id': data['quiz_id'],
            'user_id': user_id,
            'score': 85,
            'total_questions': len(data['answers']),
            'correct_answers': 17,
            'completion_time': '00:15:30',
            'submitted_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz submitted successfully',
            'data': quiz_result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit quiz',
            'error': str(e)
        }), 500

@quiz_bp.route('/quiz/results', methods=['GET'])
@login_required
def get_quiz_results():
    """5.2.3. Kullanıcının quiz sonuçlarını getirir."""
    
    try:
        user_id = session.get('user_id')
        # TODO: Implement quiz results retrieval
        results = [
            {
                'id': 1,
                'quiz_id': 'quiz_123',
                'subject': 'Matematik',
                'topic': 'Sayılar',
                'score': 85,
                'total_questions': 20,
                'correct_answers': 17,
                'completion_time': '00:15:30',
                'completed_at': '2024-01-15T10:30:00'
            },
            {
                'id': 2,
                'quiz_id': 'quiz_124',
                'subject': 'Türkçe',
                'topic': 'Dilbilgisi',
                'score': 90,
                'total_questions': 15,
                'correct_answers': 13,
                'completion_time': '00:12:45',
                'completed_at': '2024-01-14T14:20:00'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz results retrieved successfully',
            'data': results
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve quiz results',
            'error': str(e)
        }), 500 