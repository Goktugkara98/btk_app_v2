# =============================================================================
# QUIZ SESSION REPOSITORY
# =============================================================================
# Quiz oturumları için veritabanı işlemlerini yöneten repository sınıfı
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. QUIZ SESSION REPOSITORY SINIFI
#   4.1. Constructor ve Başlatma
#   4.2. Quiz Session İşlemleri
#     4.2.1. create_session(self, session_data)
#     4.2.2. get_session(self, session_id)
#     4.2.3. update_session(self, session_id, update_data)
#     4.2.4. complete_session(self, session_id, results)
#   4.3. Quiz Session Questions İşlemleri
#     4.3.1. add_session_questions(self, session_id, questions)
#     4.3.2. get_session_questions(self, session_id)
#     4.3.3. update_answer(self, session_id, question_id, answer_data)
#     4.3.4. get_session_results(self, session_id)
#   4.4. Soru Seçimi İşlemleri
#     4.4.1. get_random_questions(self, topic_id, difficulty, count)
#     4.4.2. get_random_questions_by_subject(self, subject_id, difficulty, count)
#   4.5. Yardımcı İşlemler
#     4.5.1. get_correct_answer(self, question_id)
#     4.5.2. get_question_options(self, question_id)
#     4.5.3. get_question_details(self, question_id)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from typing import Dict, List, Optional, Tuple, Any
from app.database.db_connection import DatabaseConnection

# =============================================================================
# 4.0. QUIZ SESSION REPOSITORY SINIFI
# =============================================================================

class QuizSessionRepository:
    """
    Quiz oturumları için veritabanı işlemlerini yöneten repository sınıfı.
    """
    
    def __init__(self):
        """Repository'yi başlatır."""
        self.db = DatabaseConnection()

    # -------------------------------------------------------------------------
    # 4.2. Quiz Session İşlemleri
    # -------------------------------------------------------------------------
    
    def create_session(self, session_data: Dict[str, Any]) -> Tuple[bool, Optional[int]]:
        """4.2.1. Yeni quiz session'ı oluşturur."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    INSERT INTO quiz_sessions (
                        session_id, user_id, grade_id, subject_id, unit_id, topic_id,
                        difficulty_level, timer_enabled, timer_duration, quiz_mode, question_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_data['session_id'],
                    session_data['user_id'],
                    session_data['grade_id'],
                    session_data['subject_id'],
                    session_data.get('unit_id'),
                    session_data['topic_id'],
                    session_data.get('difficulty_level', 'random'),
                    session_data.get('timer_enabled', True),
                    session_data.get('timer_duration', 30),
                    session_data.get('quiz_mode', 'educational'),
                    session_data.get('question_count', 10)
                ))
                
                session_db_id = conn.cursor.lastrowid
                conn.connection.commit()
                
                return True, session_db_id
                
        except Exception as e:
            # Keep only critical error
            print(f"❌ Quiz session oluşturma hatası: {e}")
            return False, None

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """4.2.2. Session ID'ye göre quiz session'ı getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT qs.*, 
                           g.name as grade_name,
                           s.name as subject_name,
                           u.name as unit_name,
                           t.name as topic_name
                    FROM quiz_sessions qs
                    JOIN grades g ON qs.grade_id = g.id
                    JOIN subjects s ON qs.subject_id = s.id
                    LEFT JOIN units u ON qs.unit_id = u.id
                    LEFT JOIN topics t ON qs.topic_id = t.id
                    WHERE qs.session_id = %s
                """, (session_id,))
                
                session = conn.cursor.fetchone()
                return session
                
        except Exception as e:
            return None

    def get_session_by_id(self, session_db_id: int) -> Optional[Dict[str, Any]]:
        """4.2.2b. Session DB ID'ye göre quiz session'ı getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT qs.*, 
                           g.name as grade_name,
                           s.name as subject_name,
                           u.name as unit_name,
                           t.name as topic_name
                    FROM quiz_sessions qs
                    JOIN grades g ON qs.grade_id = g.id
                    JOIN subjects s ON qs.subject_id = s.id
                    LEFT JOIN units u ON qs.unit_id = u.id
                    LEFT JOIN topics t ON qs.topic_id = t.id
                    WHERE qs.id = %s
                """, (session_db_id,))
                
                session = conn.cursor.fetchone()
                return session
                
        except Exception as e:
            return None

    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """4.2.3. Quiz session'ı günceller."""
        try:
            with self.db as conn:
                # Dinamik olarak güncellenecek alanları oluştur
                set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                values = list(update_data.values()) + [session_id]
                
                conn.cursor.execute(f"""
                    UPDATE quiz_sessions 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, values)
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    def update_session_timer(self, session_id: str, remaining_time_seconds: int) -> bool:
        """4.2.3b. Quiz session timer'ını günceller."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    UPDATE quiz_sessions 
                    SET remaining_time_seconds = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (remaining_time_seconds, session_id))
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    def complete_session(self, session_id: str, results: Dict[str, Any]) -> bool:
        """4.2.4. Quiz session'ı tamamlar ve sonuçları kaydeder."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    UPDATE quiz_sessions 
                    SET status = 'completed',
                        end_time = CURRENT_TIMESTAMP,
                        total_score = %s,
                        correct_answers = %s,
                        completion_time_seconds = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (
                    results['total_score'],
                    results['correct_answers'],
                    results['completion_time_seconds'],
                    session_id
                ))
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    # -------------------------------------------------------------------------
    # 4.3. Quiz Session Questions İşlemleri
    # -------------------------------------------------------------------------
    
    def add_session_questions(self, session_id: int, questions: List[Dict[str, Any]]) -> bool:
        """4.3.1. Session'a soruları ekler."""
        try:
            with self.db as conn:
                for i, question in enumerate(questions, 1):
                    conn.cursor.execute("""
                        INSERT INTO quiz_session_questions (
                            session_id, question_id, question_order
                        ) VALUES (%s, %s, %s)
                    """, (session_id, question['id'], i))
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    def get_session_questions(self, session_id: int) -> List[Dict[str, Any]]:
        """4.3.2. Session'daki soruları getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT qsq.*, 
                           q.name as question_text,
                           q.difficulty_level,
                           q.question_type,
                           q.points
                    FROM quiz_session_questions qsq
                    JOIN questions q ON qsq.question_id = q.id
                    WHERE qsq.session_id = %s
                    ORDER BY qsq.question_order
                """, (session_id,))
                
                questions = conn.cursor.fetchall()
                return questions
                
        except Exception as e:
            return []

    def update_answer(self, session_id: int, question_id: int, answer_data: Dict[str, Any]) -> bool:
        """4.3.3. Soru cevabını günceller."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    UPDATE quiz_session_questions 
                    SET user_answer_option_id = %s,
                        is_correct = %s,
                        points_earned = %s,
                        time_spent_seconds = %s,
                        answered_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s AND question_id = %s
                """, (
                    answer_data.get('user_answer_option_id'),
                    answer_data.get('is_correct'),
                    answer_data.get('points_earned', 0),
                    answer_data.get('time_spent_seconds', 0),
                    session_id,
                    question_id
                ))
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """4.3.4. Session sonuçlarını getirir."""
        try:
            with self.db as conn:
                # Session bilgilerini al
                conn.cursor.execute("""
                    SELECT * FROM quiz_sessions WHERE session_id = %s
                """, (session_id,))
                session = conn.cursor.fetchone()
                
                if not session:
                    return {}
                
                # Soru sonuçlarını al (is_correct ve points_earned dahil)
                conn.cursor.execute("""
                    SELECT qsq.*, 
                           q.name as question_text,
                           q.points,
                           qo.id as correct_answer_id,
                           qo.name as correct_answer_text,
                           uao.id as user_answer_id,
                           uao.name as user_answer_text,
                           CASE 
                               WHEN qsq.user_answer_option_id = qo.id THEN 1 
                               ELSE 0 
                           END as is_correct,
                           CASE 
                               WHEN qsq.user_answer_option_id = qo.id THEN q.points 
                               ELSE 0 
                           END as points_earned
                    FROM quiz_session_questions qsq
                    JOIN questions q ON qsq.question_id = q.id
                    LEFT JOIN question_options qo ON qo.question_id = q.id AND qo.is_correct = 1
                    LEFT JOIN question_options uao ON qsq.user_answer_option_id = uao.id
                    WHERE qsq.session_id = %s
                    ORDER BY qsq.question_order
                """, (session['id'],))
                
                questions = conn.cursor.fetchall()
                
                return {
                    'session': session,
                    'questions': questions
                }
                
        except Exception as e:
            return {}

    # -------------------------------------------------------------------------
    # 4.4. Soru Seçimi İşlemleri
    # -------------------------------------------------------------------------
    
    def get_random_questions(self, topic_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1. Belirli kriterlere göre rasgele sorular getirir."""
        try:
            with self.db as conn:
                # Zorluk seviyesine göre filtreleme
                if difficulty == 'random':
                    difficulty_filter = ""
                    params = (topic_id, count)
                else:
                    difficulty_filter = "AND q.difficulty_level = %s"
                    params = (topic_id, difficulty, count)
                
                conn.cursor.execute(f"""
                    SELECT q.*, 
                           COUNT(qo.id) as option_count
                    FROM questions q
                    LEFT JOIN question_options qo ON q.id = qo.question_id
                    WHERE q.topic_id = %s 
                    AND q.is_active = 1
                    {difficulty_filter}
                    GROUP BY q.id
                    HAVING option_count >= 2
                    ORDER BY RAND()
                    LIMIT %s
                """, params)
                
                questions = conn.cursor.fetchall()
                
                # Her soru için seçenekleri al
                for question in questions:
                    conn.cursor.execute("""
                        SELECT * FROM question_options 
                        WHERE question_id = %s AND is_active = 1
                        ORDER BY RAND()
                    """, (question['id'],))
                    question['options'] = conn.cursor.fetchall()
                
                return questions
                
        except Exception as e:
            return []

    def get_random_questions_by_subject(self, subject_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1b. Subject ID'ye göre rasgele sorular getirir."""
        try:
            with self.db as conn:
                # Zorluk seviyesine göre filtreleme
                if difficulty == 'random':
                    difficulty_filter = ""
                    params = (subject_id, count)
                else:
                    difficulty_filter = "AND q.difficulty_level = %s"
                    params = (subject_id, difficulty, count)
                
                conn.cursor.execute(f"""
                    SELECT q.*, 
                           COUNT(qo.id) as option_count
                    FROM questions q
                    LEFT JOIN question_options qo ON q.id = qo.question_id
                    JOIN topics t ON q.topic_id = t.id
                    JOIN units u ON t.unit_id = u.id
                    WHERE u.subject_id = %s 
                    AND q.is_active = 1
                    {difficulty_filter}
                    GROUP BY q.id
                    HAVING option_count >= 2
                    ORDER BY RAND()
                    LIMIT %s
                """, params)
                
                questions = conn.cursor.fetchall()
                
                # Her soru için seçenekleri al
                for question in questions:
                    conn.cursor.execute("""
                        SELECT * FROM question_options 
                        WHERE question_id = %s AND is_active = 1
                        ORDER BY RAND()
                    """, (question['id'],))
                    question['options'] = conn.cursor.fetchall()
                
                return questions
                
        except Exception as e:
            return []

    # -------------------------------------------------------------------------
    # 4.5. Yardımcı İşlemler
    # -------------------------------------------------------------------------
    
    def get_correct_answer(self, question_id: int) -> Optional[Dict[str, Any]]:
        """4.5.1. Sorunun doğru cevabını getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT id, name
                    FROM question_options 
                    WHERE question_id = %s AND is_correct = 1
                    LIMIT 1
                """, (question_id,))
                
                correct_answer = conn.cursor.fetchone()
                return correct_answer
                
        except Exception as e:
            return None

    def get_question_options(self, question_id: int) -> List[Dict[str, Any]]:
        """4.5.2. Soru seçeneklerini getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT * FROM question_options 
                    WHERE question_id = %s AND is_active = 1
                    ORDER BY RAND()
                """, (question_id,))
                
                options = conn.cursor.fetchall()
                return options
                
        except Exception as e:
            return []

    def get_question_details(self, question_id: int) -> Optional[Dict[str, Any]]:
        """4.5.3. Soru detaylarını getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT q.*, 
                           t.name as topic_name,
                           s.name as subject_name
                    FROM questions q
                    JOIN topics t ON q.topic_id = t.id
                    JOIN units u ON t.unit_id = u.id
                    JOIN subjects s ON u.subject_id = s.id
                    WHERE q.id = %s
                """, (question_id,))
                
                question = conn.cursor.fetchone()
                return question
                
        except Exception as e:
            return None

    def get_answer_option_text(self, answer_option_id: int) -> Optional[str]:
        """4.5.4. Cevap seçeneği metnini getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT name FROM question_options 
                    WHERE id = %s
                """, (answer_option_id,))
                
                result = conn.cursor.fetchone()
                if result:
                    return result[0]
                return None
                
        except Exception as e:
            return None 