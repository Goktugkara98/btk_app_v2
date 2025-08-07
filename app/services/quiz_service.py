# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, quiz ile ilgili iş mantığını yöneten QuizService sınıfını
# içerir. Quiz verileri, sorular, sonuçlar gibi quiz işlemlerini yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. QUIZSERVICE SINIFI
#   4.1. Başlatma (Initialization)
#     4.1.1. __init__(self)
#   4.2. Quiz Veri İşlemleri
#     4.2.1. get_quiz_data(self)
#     4.2.2. get_subjects(self)
#     4.2.3. get_topics(self, subject_id)
#   4.3. Quiz İşlemleri
#     4.3.1. start_quiz(self, user_id, quiz_config)
#     4.3.2. submit_quiz(self, user_id, quiz_data)
#     4.3.3. get_quiz_results(self, user_id)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json
import os

# Import repositories when they are created
try:
    from app.database.quiz_repository import QuizRepository
except ImportError:
    QuizRepository = None

# =============================================================================
# 4.0. QUIZSERVICE SINIFI
# =============================================================================
class QuizService:
    """
    Quiz ile ilgili iş mantığını yönetir.
    """

    # -------------------------------------------------------------------------
    # 4.1. Başlatma (Initialization)
    # -------------------------------------------------------------------------
    def __init__(self):
        """4.1.1. Servisin kurucu metodu. Gerekli repository'leri başlatır."""
        self.quiz_repo = QuizRepository() if QuizRepository else None

    # -------------------------------------------------------------------------
    # 4.2. Quiz Veri İşlemleri
    # -------------------------------------------------------------------------
    def get_quiz_data(self) -> Dict[str, Any]:
        """4.2.1. Quiz verilerini döndürür."""
        try:
            # For now, return static data
            # TODO: Implement dynamic data loading from database
            quiz_data = {
                'subjects': [
                    {'id': 1, 'name': 'Matematik'},
                    {'id': 2, 'name': 'Türkçe'},
                    {'id': 3, 'name': 'Fen Bilgisi'},
                    {'id': 4, 'name': 'Sosyal Bilgiler'}
                ],
                'topics': [
                    {'id': 1, 'subject_id': 1, 'name': 'Sayılar'},
                    {'id': 2, 'subject_id': 1, 'name': 'Geometri'},
                    {'id': 3, 'subject_id': 2, 'name': 'Dilbilgisi'},
                    {'id': 4, 'subject_id': 2, 'name': 'Okuma Anlama'}
                ]
            }
            return quiz_data
        except Exception as e:
            print(f"Error in get_quiz_data service: {e}")
            return {}

    def get_subjects(self) -> List[Dict[str, Any]]:
        """4.2.2. Tüm dersleri listeler."""
        try:
            # TODO: Implement dynamic subject loading from database
            subjects = [
                {'id': 1, 'name': 'Matematik', 'description': 'Matematik dersi'},
                {'id': 2, 'name': 'Türkçe', 'description': 'Türkçe dersi'},
                {'id': 3, 'name': 'Fen Bilgisi', 'description': 'Fen Bilgisi dersi'},
                {'id': 4, 'name': 'Sosyal Bilgiler', 'description': 'Sosyal Bilgiler dersi'}
            ]
            return subjects
        except Exception as e:
            print(f"Error in get_subjects service: {e}")
            return []

    def get_topics(self, subject_id: int) -> List[Dict[str, Any]]:
        """4.2.3. Belirli bir derse ait konuları listeler."""
        try:
            if not subject_id:
                return []
            
            # TODO: Implement dynamic topic loading from database
            all_topics = [
                {'id': 1, 'subject_id': 1, 'name': 'Sayılar', 'description': 'Sayılar konusu'},
                {'id': 2, 'subject_id': 1, 'name': 'Geometri', 'description': 'Geometri konusu'},
                {'id': 3, 'subject_id': 2, 'name': 'Dilbilgisi', 'description': 'Dilbilgisi konusu'},
                {'id': 4, 'subject_id': 2, 'name': 'Okuma Anlama', 'description': 'Okuma Anlama konusu'}
            ]
            
            # Filter topics by subject_id
            filtered_topics = [topic for topic in all_topics if topic['subject_id'] == subject_id]
            return filtered_topics
        except Exception as e:
            print(f"Error in get_topics service: {e}")
            return []

    # -------------------------------------------------------------------------
    # 4.3. Quiz İşlemleri
    # -------------------------------------------------------------------------
    def start_quiz(self, user_id: int, quiz_config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """4.3.1. Yeni bir quiz başlatır."""
        try:
            # Required fields validation
            required_fields = ['subject_id', 'topic_id', 'question_count']
            for field in required_fields:
                if field not in quiz_config:
                    return False, {'message': f'Missing required field: {field}'}

            # TODO: Implement quiz start logic with database
            quiz_session = {
                'id': f'quiz_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'user_id': user_id,
                'subject_id': quiz_config['subject_id'],
                'topic_id': quiz_config['topic_id'],
                'question_count': quiz_config['question_count'],
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }
            
            return True, quiz_session
        except Exception as e:
            print(f"Error in start_quiz service: {e}")
            return False, {'message': 'Quiz başlatılırken bir hata oluştu'}

    def submit_quiz(self, user_id: int, quiz_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """4.3.2. Quiz sonuçlarını gönderir."""
        try:
            # Required fields validation
            required_fields = ['quiz_id', 'answers']
            for field in required_fields:
                if field not in quiz_data:
                    return False, {'message': f'Missing required field: {field}'}

            # TODO: Implement quiz submission logic with database
            quiz_result = {
                'quiz_id': quiz_data['quiz_id'],
                'user_id': user_id,
                'score': 85,  # TODO: Calculate actual score
                'total_questions': len(quiz_data['answers']),
                'correct_answers': 17,  # TODO: Calculate actual correct answers
                'completion_time': '00:15:30',  # TODO: Calculate actual time
                'submitted_at': datetime.now().isoformat()
            }
            
            return True, quiz_result
        except Exception as e:
            print(f"Error in submit_quiz service: {e}")
            return False, {'message': 'Quiz gönderilirken bir hata oluştu'}

    def get_quiz_results(self, user_id: int) -> List[Dict[str, Any]]:
        """4.3.3. Kullanıcının quiz sonuçlarını getirir."""
        try:
            # TODO: Implement quiz results retrieval from database
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
            return results
        except Exception as e:
            print(f"Error in get_quiz_results service: {e}")
            return [] 