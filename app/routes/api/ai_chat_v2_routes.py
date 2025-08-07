# =============================================================================
# AI CHAT V2 ROUTES - REFACTORED
# =============================================================================
# Bu modül, yeni servis yapısı ile AI sohbet rotalarını içerir.
# Modüler servis yapısı: GeminiAPI + ChatSession + ChatMessage services
# =============================================================================

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any
import traceback

# Create the AI chat v2 blueprint
ai_chat_v2_bp = Blueprint('ai_chat_v2', __name__)

# Import new modular services
try:
    from app.services.gemini_api_service import GeminiAPIService
    from app.services.chat_session_service import ChatSessionService
    from app.services.chat_message_service import ChatMessageService
    from app.services.quiz_session_service import QuizSessionService
    from app.database.db_connection import DatabaseConnection
except ImportError as e:
    GeminiAPIService = None
    ChatSessionService = None
    ChatMessageService = None
    QuizSessionService = None
    DatabaseConnection = None

# Global service instances
db_connection = DatabaseConnection() if DatabaseConnection else None
gemini_service = GeminiAPIService() if GeminiAPIService else None
chat_session_service = ChatSessionService(db_connection) if ChatSessionService else None
chat_message_service = ChatMessageService() if ChatMessageService else None

# ===========================================================================
# SYSTEM ROUTES
# ===========================================================================

@ai_chat_v2_bp.route('/ai/system/status', methods=['GET'])
def system_status():
    """AI sistem durumunu döndürür"""
    try:
        if not gemini_service:
            return jsonify({
                'status': 'error',
                'message': 'AI services not available'
            }), 503
        
        status_data = gemini_service.get_service_status()
        
        return jsonify({
            'status': 'success',
            'message': 'AI system status retrieved successfully',
            'data': {
                **status_data,
                'services': {
                    'gemini_api': bool(gemini_service and gemini_service.is_available()),
                    'chat_session': bool(chat_session_service),
                    'chat_message': bool(chat_message_service)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get AI system status',
            'error': str(e)
        }), 500

@ai_chat_v2_bp.route('/ai/system/health', methods=['GET'])
def system_health():
    """AI sistem sağlığını test eder"""
    try:
        if not gemini_service or not gemini_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Gemini API service not available',
                'healthy': False
            }), 503
        
        # Connection test
        connection_ok = gemini_service.test_connection()
        
        return jsonify({
            'status': 'success',
            'message': 'Health check completed',
            'data': {
                'healthy': connection_ok,
                'gemini_connection': connection_ok,
                'services_loaded': bool(chat_session_service and chat_message_service)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'healthy': False,
            'error': str(e)
        }), 500

# ===========================================================================
# SESSION ROUTES
# ===========================================================================

@ai_chat_v2_bp.route('/ai/session/start', methods=['POST'])
def start_chat_session():
    """Yeni chat session başlatır"""
    try:
        if not all([gemini_service, chat_session_service, chat_message_service]):
            return jsonify({
                'status': 'error',
                'message': 'AI services not fully available'
            }), 503
        
        data = request.get_json()
        if not data or 'quiz_session_id' not in data or 'question_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Quiz session ID and question ID are required'
            }), 400
        
        quiz_session_id = data['quiz_session_id']
        question_id = data['question_id']
        
        # Quiz session bilgilerini al
        if QuizSessionService:
            quiz_service = QuizSessionService()
            quiz_info = quiz_service.get_session_info(quiz_session_id)
            
            if not quiz_info:
                return jsonify({
                    'status': 'error',
                    'message': 'Quiz session not found'
                }), 404
            
            user_context = {
                'subject': quiz_info['session'].get('subject_name'),
                'topic': quiz_info['session'].get('topic_name'),
                'difficulty': quiz_info['session'].get('difficulty_level'),
                'quiz_mode': quiz_info['session'].get('quiz_mode')
            }
        else:
            user_context = data.get('context', {})
        
        # Chat session oluştur veya mevcut olanı bul (soru bazlı)
        user_id = session.get('user_id')  # Flask session'dan user ID al
        chat_session_id = chat_session_service.create_session_for_question(
            quiz_session_id, question_id, user_context, user_id
        )
        
        # Eğer yeni session oluşturulduysa welcome mesajı ekle
        if chat_session_id and not chat_session_service.get_session(chat_session_id):
            welcome_message = chat_message_service.create_system_message('session_started')
            chat_session_service.add_message(
                chat_session_id, 'system', welcome_message, 
                metadata={'question_id': question_id}
            )
        
        return jsonify({
            'status': 'success',
            'message': 'Chat session started successfully',
            'data': {
                'chat_session_id': chat_session_id,
                'quiz_session_id': quiz_session_id,
                'context': user_context
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to start chat session',
            'error': str(e)
        }), 500


@ai_chat_v2_bp.route('/ai/chat/history', methods=['GET'])
def get_chat_history():
    """Belirli bir chat session için chat history'yi getirir"""
    try:
        chat_session_id = request.args.get('chat_session_id')
        
        if not chat_session_id:
            return jsonify({
                'status': 'error',
                'message': 'chat_session_id parameter is required'
            }), 400
        
        # Chat history'yi getir
        messages = chat_message_service.get_chat_history(chat_session_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Chat history retrieved successfully',
            'data': {
                'messages': messages
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@ai_chat_v2_bp.route('/ai/session/<chat_session_id>/info', methods=['GET'])
def get_session_info(chat_session_id):
    """Chat session bilgilerini döndürür"""
    try:
        if not chat_session_service:
            return jsonify({
                'status': 'error',
                'message': 'Chat session service not available'
            }), 503
        
        session_info = chat_session_service.get_session(chat_session_id)
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Chat session not found'
            }), 404
        
        # Stats ekle
        stats = chat_session_service.get_session_stats(chat_session_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Session info retrieved successfully',
            'data': {
                'session_info': {
                    'chat_session_id': chat_session_id,
                    'quiz_session_id': session_info['quiz_session_id'],
                    'context': session_info['user_context'],
                    'status': session_info['status'],
                    'created_at': session_info['created_at'].isoformat()
                },
                'stats': stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get session info',
            'error': str(e)
        }), 500

# ===========================================================================
# CHAT ROUTES
# ===========================================================================

@ai_chat_v2_bp.route('/ai/chat/message', methods=['POST'])
def send_chat_message():
    """Chat mesajı gönderir ve AI yanıtı alır"""
    try:
        if not all([gemini_service, chat_session_service, chat_message_service]):
            return jsonify({
                'status': 'error',
                'message': 'AI services not fully available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request data is required'
            }), 400
        
        # Required fields
        required_fields = ['message', 'chat_session_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400
        
        message = data['message']
        chat_session_id = data['chat_session_id']
        question_id = data.get('question_id')
        question_context = data.get('question_context')  # Yeni: Soru ve şıkların içeriği
        
        # Mesaj validasyonu
        is_valid, error_msg = chat_message_service.validate_message(message)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
        
        # Chat session kontrol
        session_info = chat_session_service.get_session(chat_session_id)
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Chat session not found'
            }), 404
        
        # Mesajı sanitize et
        sanitized_message = chat_message_service.sanitize_message(message)
        
        # User mesajını veritabanına kaydet
        import time
        start_time = time.time()
        
        user_metadata = chat_message_service.create_message_metadata('user', question_id=question_id)
        user_message_id = chat_session_service.add_message(
            chat_session_id, 'user', sanitized_message, 
            action_type='general', metadata=user_metadata
        )
        
        # AI için prompt oluştur - question_context varsa ekle
        if question_context:
            # Soru ve şıkların içeriğini prompt'a ekle
            context_message = f"""
SORU İÇERİĞİ:
{question_context.get('question_text', 'Soru metni bulunamadı')}

ŞIKLAR:
"""
            for i, option in enumerate(question_context.get('options', []), 1):
                context_message += f"{i}. {option.get('option_text', 'Şık metni bulunamadı')}\n"
            
            context_message += f"\nKULLANICI MESAJI: {sanitized_message}"
            
            print(f"[AI_CHAT_V2] First message with question context: {context_message}")
            
            prompt = chat_session_service.build_prompt(chat_session_id, context_message, 'general')
        else:
            # Normal prompt oluştur
            prompt = chat_session_service.build_prompt(chat_session_id, sanitized_message, 'general')
        
        # Token sınırı uyarısını prompt'un sonuna ekle
        prompt += "\n\nÖNEMLİ: Cevabında 5000 token geçmemeye çalış. Kısa ve öz cevaplar ver."
        
        # AI'dan yanıt al
        ai_response = gemini_service.generate_content(prompt)
        
        # Response time hesapla
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if not ai_response:
            error_msg = chat_message_service.get_error_message('api_error')
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 500
        
        # AI yanıtını format et
        formatted_response = chat_message_service.format_ai_response(ai_response)
        
        # AI mesajını veritabanına kaydet
        ai_metadata = chat_message_service.create_message_metadata('ai', question_id=question_id)
        ai_message_id = chat_session_service.add_message(
            chat_session_id, 'ai', formatted_response,
            action_type='general',
            ai_model='gemini-2.5-flash',
            prompt_used=prompt,
            response_time_ms=response_time_ms,
            metadata=ai_metadata
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Chat message processed successfully',
            'data': {
                'ai_response': formatted_response,
                'chat_session_id': chat_session_id
            }
        }), 200
        
    except Exception as e:
        error_msg = chat_message_service.get_error_message('general_error') if chat_message_service else 'System error'
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'error': str(e)
        }), 500

@ai_chat_v2_bp.route('/ai/chat/quick-action', methods=['POST'])
def quick_action():
    """Hızlı eylemler (açıkla, ipucu)"""
    try:
        if not all([gemini_service, chat_session_service, chat_message_service]):
            return jsonify({
                'status': 'error',
                'message': 'AI services not fully available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request data is required'
            }), 400
        
        # Required fields
        required_fields = ['action', 'chat_session_id', 'question_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400
        
        action = data['action']
        chat_session_id = data['chat_session_id']
        question_id = data['question_id']
        question_context = data.get('question_context')  # Yeni: Soru ve şıkların içeriği
        
        # Chat session kontrol
        session_info = chat_session_service.get_session(chat_session_id)
        if not session_info:
            return jsonify({
                'status': 'error',
                'message': 'Chat session not found'
            }), 404
        
        # Soru bilgilerini al - önce question_context'ten, yoksa veritabanından
        if question_context:
            # Frontend'den gelen soru bilgilerini kullan
            question_data = {
                'question_text': question_context.get('question_text', ''),
                'topic_name': session_info['user_context'].get('topic', ''),
                'options': question_context.get('options', [])
            }
        elif QuizSessionService:
            # Veritabanından soru bilgilerini al
            quiz_service = QuizSessionService()
            question_details = quiz_service.get_question_details(question_id)
            question_options = quiz_service.get_question_options(question_id)
            
            if not question_details:
                return jsonify({
                    'status': 'error',
                    'message': 'Question not found'
                }), 404
            
            question_data = {
                'question_text': question_details.get('question_text', ''),
                'topic_name': session_info['user_context'].get('topic', ''),
                'options': question_options
            }
        else:
            return jsonify({
                'status': 'error',
                'message': 'Quiz service not available'
            }), 503
        
        # Quick action prompt oluştur
        prompt = chat_message_service.create_quick_action_prompt(action, question_data)
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Invalid action type'
            }), 400
        
        # Context ekle
        full_prompt = chat_session_service.get_conversation_context(chat_session_id, question_id) + "\n\n" + prompt
        
        # Token sınırı uyarısını prompt'un sonuna ekle
        full_prompt += "\n\nÖNEMLİ: Cevabında 20000 token geçmemeye çalış. Kısa ve öz cevaplar ver."
        
        # AI'dan yanıt al
        ai_response = gemini_service.generate_content(full_prompt)
        
        if not ai_response:
            error_msg = chat_message_service.get_error_message('api_error')
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 500
        
        # AI yanıtını format et
        formatted_response = chat_message_service.format_ai_response(ai_response)
        
        # AI mesajını session'a ekle
        ai_metadata = chat_message_service.create_message_metadata('ai', action=action, question_id=question_id)
        chat_session_service.add_message(chat_session_id, 'ai', formatted_response, ai_metadata)
        
        return jsonify({
            'status': 'success',
            'message': f'Quick action {action} processed successfully',
            'data': {
                'action': action,
                'ai_response': formatted_response,
                'question_id': question_id,
                'chat_session_id': chat_session_id
            }
        }), 200
        
    except Exception as e:
        error_msg = chat_message_service.get_error_message('general_error') if chat_message_service else 'System error'
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'error': str(e)
        }), 500

# ===========================================================================
# UTILITY ROUTES
# ===========================================================================

@ai_chat_v2_bp.route('/ai/session/cleanup', methods=['POST'])
def cleanup_sessions():
    """Eski session'ları temizler"""
    try:
        if not chat_session_service:
            return jsonify({
                'status': 'error',
                'message': 'Chat session service not available'
            }), 503
        
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        chat_session_service.cleanup_old_sessions(max_age_hours)
        
        return jsonify({
            'status': 'success',
            'message': 'Session cleanup completed'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to cleanup sessions',
            'error': str(e)
        }), 500