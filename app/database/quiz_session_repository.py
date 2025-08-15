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
import os
import time
import random
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
        # PERF logging toggle (env PERF_LOG = 1/true)
        try:
            self._perf = str(os.getenv('PERF_LOG', '0')).lower() in ('1', 'true', 't', 'yes', 'y')
        except Exception:
            self._perf = False

    # -------------------------------------------------------------------------
    # 4.2. Quiz Session İşlemleri
    # -------------------------------------------------------------------------
    
    def create_session(self, session_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """4.2.1. Yeni quiz session'ı oluşturur."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    INSERT INTO quiz_sessions (
                        session_id, user_id, grade_id, subject_id, unit_id, topic_id,
                        selection_scope, difficulty_level, timer_enabled, timer_duration_seconds, quiz_mode, question_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_data['session_id'],
                    session_data['user_id'],
                    session_data['grade_id'],
                    session_data['subject_id'],
                    session_data.get('unit_id'),
                    session_data.get('topic_id'),
                    session_data.get('selection_scope', 'topic'),
                    session_data.get('difficulty_level', 'random'),
                    session_data.get('timer_enabled', True),
                    int(session_data.get('timer_duration', 30)) * 60,
                    session_data.get('quiz_mode', 'educational'),
                    session_data.get('question_count', 10)
                ))
                conn.connection.commit()
                return True, session_data['session_id']
                
        except Exception as e:
            return False, None

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """4.2.2. Session ID'ye göre quiz session'ı getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT qs.*, 
                           g.grade_name as grade_name,
                           s.subject_name as subject_name,
                           u.unit_name as unit_name,
                           t.topic_name as topic_name
                    FROM quiz_sessions qs
                    LEFT JOIN grades g ON qs.grade_id = g.grade_id
                    LEFT JOIN subjects s ON qs.subject_id = s.subject_id
                    LEFT JOIN units u ON qs.unit_id = u.unit_id
                    LEFT JOIN topics t ON qs.topic_id = t.topic_id
                    WHERE qs.session_id = %s
                """, (session_id,))
                
                session = conn.cursor.fetchone()
                return session
                
        except Exception as e:
            return None

    # get_session_by_id removed: session_id string is the primary identifier

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
    
    def add_session_questions(self, session_id: str, questions: List[Dict[str, Any]]) -> bool:
        """4.3.1. Session'a soruları ekler."""
        try:
            with self.db as conn:
                for i, question in enumerate(questions, 1):
                    conn.cursor.execute("""
                        INSERT INTO quiz_session_questions (
                            session_id, question_id, question_order
                        ) VALUES (%s, %s, %s)
                    """, (session_id, question['question_id'], i))
                
                conn.connection.commit()
                return True
                
        except Exception as e:
            return False

    def get_session_questions(self, session_id: str) -> List[Dict[str, Any]]:
        """4.3.2. Session'daki soruları getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT qsq.*, 
                           q.question_text as question_text,
                           q.difficulty_level,
                           q.question_type,
                           q.points
                    FROM quiz_session_questions qsq
                    JOIN questions q ON qsq.question_id = q.question_id
                    WHERE qsq.session_id = %s
                    ORDER BY qsq.question_order
                """, (session_id,))
                
                questions = conn.cursor.fetchall()
                return questions
                
        except Exception as e:
            return []

    def update_answer(self, session_id: str, question_id: int, answer_data: Dict[str, Any]) -> bool:
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
                           q.question_text as question_text,
                           q.points,
                           qo.option_id as correct_answer_id,
                           qo.option_text as correct_answer_text,
                           uao.option_id as user_answer_id,
                           uao.option_text as user_answer_text,
                           CASE 
                               WHEN qsq.user_answer_option_id = qo.option_id THEN 1 
                               ELSE 0 
                           END as is_correct,
                           CASE 
                               WHEN qsq.user_answer_option_id = qo.option_id THEN q.points 
                               ELSE 0 
                           END as points_earned
                    FROM quiz_session_questions qsq
                    JOIN questions q ON qsq.question_id = q.question_id
                    LEFT JOIN question_options qo ON qo.question_id = q.question_id AND qo.is_correct = 1
                    LEFT JOIN question_options uao ON qsq.user_answer_option_id = uao.option_id
                    WHERE qsq.session_id = %s
                    ORDER BY qsq.question_order
                """, (session['session_id'],))
                
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
    
    def _random_sample_questions(self, joins_sql: str, where_sql: str, params: tuple, count: int) -> List[Dict[str, Any]]:
        """ID tabanlı rastgele örnekleme uygular. RAND() ve OFFSET kullanmaz.
        - 1) Filtreli MIN/MAX question_id aralığını bulur
        - 2) Bu aralıkta rastgele id'lerden >= id ile ilk kaydı LIMIT 1 çekerek toplar
        - 3) Eksik kalırsa sıralı doldurma yapar
        """
        try:
            with self.db as conn:
                # 1) Sınırları al
                if self._perf:
                    t_bounds = time.perf_counter()
                conn.cursor.execute(f"""
                    SELECT MIN(q.question_id) AS min_id, MAX(q.question_id) AS max_id
                    FROM questions q
                    {joins_sql}
                    WHERE {where_sql}
                """, params)
                row = conn.cursor.fetchone()
                if not row or row.get('min_id') is None or row.get('max_id') is None:
                    return []
                min_id = int(row.get('min_id'))
                max_id = int(row.get('max_id'))
                if self._perf:
                    print(f"[PERF][Repo] _random_sample bounds: {(time.perf_counter()-t_bounds)*1000:.1f} ms (min={min_id}, max={max_id})")
                if min_id > max_id:
                    return []

                # 2) Rastgele örnekler
                sample_budget = min(5 * max(1, count), 1000)
                seen_ids = set()
                out: List[Dict[str, Any]] = []
                if self._perf:
                    t_sample = time.perf_counter()
                for _ in range(sample_budget):
                    if len(out) >= count:
                        break
                    r = random.randint(min_id, max_id)
                    conn.cursor.execute(f"""
                        SELECT q.*
                        FROM questions q
                        {joins_sql}
                        WHERE {where_sql} AND q.question_id >= %s
                        ORDER BY q.question_id
                        LIMIT 1
                    """, params + (r,))
                    one = conn.cursor.fetchone()
                    if one and one.get('question_id') not in seen_ids:
                        seen_ids.add(one['question_id'])
                        out.append(one)
                if self._perf:
                    print(f"[PERF][Repo] _random_sample loop: {(time.perf_counter()-t_sample)*1000:.1f} ms, collected={len(out)}")

                # 3) Eksik kalırsa sıralı doldur
                if len(out) < count:
                    need = count - len(out)
                    if self._perf:
                        t_fill = time.perf_counter()
                    conn.cursor.execute(f"""
                        SELECT q.*
                        FROM questions q
                        {joins_sql}
                        WHERE {where_sql}
                        ORDER BY q.question_id
                        LIMIT %s
                    """, params + (max(need * 3, need),))
                    rows = conn.cursor.fetchall()
                    for rrow in rows:
                        qid = rrow.get('question_id')
                        if qid not in seen_ids:
                            seen_ids.add(qid)
                            out.append(rrow)
                            if len(out) >= count:
                                break
                    if self._perf:
                        print(f"[PERF][Repo] _random_sample fill: {(time.perf_counter()-t_fill)*1000:.1f} ms, after_fill={len(out)}")
                try:
                    random.shuffle(out)
                except Exception:
                    pass
                return out[:count]
        except Exception:
            return []

    def get_random_questions(self, topic_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1. Belirli kriterlere göre ID tabanlı rastgele sorular getirir."""
        try:
            # Filtreleri hazırla
            diff_sql = "" if difficulty == 'random' else " AND q.difficulty_level = %s"
            where_sql = (
                "q.topic_id = %s AND q.is_active = 1" + diff_sql +
                " AND (SELECT COUNT(1) FROM question_options qo WHERE qo.question_id = q.question_id) >= 2"
            )
            params = (topic_id,) if difficulty == 'random' else (topic_id, difficulty)
            if self._perf:
                t0 = time.perf_counter()
            questions = self._random_sample_questions("", where_sql, params, count)
            if self._perf:
                print(f"[PERF][Repo] get_random_questions sample: {(time.perf_counter()-t0)*1000:.1f} ms, n={len(questions)}")
            return questions
        except Exception:
            return []

    def get_random_questions_by_subject(self, subject_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1b. Subject ID'ye göre ID tabanlı rastgele sorular getirir."""
        try:
            joins_sql = "JOIN topics t ON q.topic_id = t.topic_id JOIN units u ON t.unit_id = u.unit_id"
            diff_sql = "" if difficulty == 'random' else " AND q.difficulty_level = %s"
            where_sql = (
                "u.subject_id = %s AND q.is_active = 1" + diff_sql +
                " AND (SELECT COUNT(1) FROM question_options qo WHERE qo.question_id = q.question_id) >= 2"
            )
            params = (subject_id,) if difficulty == 'random' else (subject_id, difficulty)
            if self._perf:
                t0 = time.perf_counter()
            questions = self._random_sample_questions(joins_sql, where_sql, params, count)
            if self._perf:
                print(f"[PERF][Repo] get_random_questions_by_subject sample: {(time.perf_counter()-t0)*1000:.1f} ms, n={len(questions)}")
            return questions
        except Exception:
            return []

    def get_random_questions_by_unit(self, unit_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1c. Unit ID'ye göre ID tabanlı rastgele sorular getirir."""
        try:
            joins_sql = "JOIN topics t ON q.topic_id = t.topic_id"
            diff_sql = "" if difficulty == 'random' else " AND q.difficulty_level = %s"
            where_sql = (
                "t.unit_id = %s AND q.is_active = 1" + diff_sql +
                " AND (SELECT COUNT(1) FROM question_options qo WHERE qo.question_id = q.question_id) >= 2"
            )
            params = (unit_id,) if difficulty == 'random' else (unit_id, difficulty)
            if self._perf:
                t0 = time.perf_counter()
            questions = self._random_sample_questions(joins_sql, where_sql, params, count)
            if self._perf:
                print(f"[PERF][Repo] get_random_questions_by_unit sample: {(time.perf_counter()-t0)*1000:.1f} ms, n={len(questions)}")
            return questions
        except Exception:
            return []

    def get_random_questions_by_grade(self, grade_id: int, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1d. Grade ID'ye göre ID tabanlı rastgele sorular getirir."""
        try:
            joins_sql = (
                "JOIN topics t ON q.topic_id = t.topic_id "
                "JOIN units u ON t.unit_id = u.unit_id "
                "JOIN subjects s ON u.subject_id = s.subject_id"
            )
            diff_sql = "" if difficulty == 'random' else " AND q.difficulty_level = %s"
            where_sql = (
                "s.grade_id = %s AND q.is_active = 1" + diff_sql +
                " AND (SELECT COUNT(1) FROM question_options qo WHERE qo.question_id = q.question_id) >= 2"
            )
            params = (grade_id,) if difficulty == 'random' else (grade_id, difficulty)
            if self._perf:
                t0 = time.perf_counter()
            questions = self._random_sample_questions(joins_sql, where_sql, params, count)
            if self._perf:
                print(f"[PERF][Repo] get_random_questions_by_grade sample: {(time.perf_counter()-t0)*1000:.1f} ms, n={len(questions)}")
            return questions
        except Exception:
            return []

    def get_random_questions_global(self, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """4.4.1e. Herhangi bir kapsam olmadan ID tabanlı rastgele sorular getirir."""
        try:
            diff_sql = "" if difficulty == 'random' else " AND q.difficulty_level = %s"
            where_sql = (
                "q.is_active = 1" + diff_sql +
                " AND (SELECT COUNT(1) FROM question_options qo WHERE qo.question_id = q.question_id) >= 2"
            )
            params = tuple() if difficulty == 'random' else (difficulty,)
            if self._perf:
                t0 = time.perf_counter()
            questions = self._random_sample_questions("", where_sql, params, count)
            if self._perf:
                print(f"[PERF][Repo] get_random_questions_global sample: {(time.perf_counter()-t0)*1000:.1f} ms, n={len(questions)}")
            return questions
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # 4.5. Yardımcı İşlemler
    # -------------------------------------------------------------------------
    
    def get_correct_answer(self, question_id: int) -> Optional[Dict[str, Any]]:
        """4.5.1. Sorunun doğru cevabını getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT option_id AS id, option_text AS name
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
                if self._perf:
                    t0 = time.perf_counter()
                conn.cursor.execute("""
                    SELECT 
                        option_id AS id,
                        option_text AS name,
                        option_text AS option_text,
                        is_correct,
                        description,
                        created_at,
                        updated_at
                    FROM question_options 
                    WHERE question_id = %s
                """, (question_id,))
                
                options = conn.cursor.fetchall()
                if self._perf:
                    print(f"[PERF][Repo] get_question_options query: {(time.perf_counter()-t0)*1000:.1f} ms")
                # Python tarafında rastgele sırala (SQL'de RAND() yerine)
                try:
                    random.shuffle(options)
                except Exception:
                    pass
                return options
                
        except Exception as e:
            return []

    def get_question_details(self, question_id: int) -> Optional[Dict[str, Any]]:
        """4.5.3. Soru detaylarını getirir."""
        try:
            with self.db as conn:
                conn.cursor.execute("""
                    SELECT 
                        q.question_id,
                        q.question_text,
                        q.difficulty_level,
                        q.question_type,
                        q.points as points,
                        q.description,
                        q.created_at,
                        q.updated_at,
                        t.topic_id as topic_id,
                        t.topic_name as topic_name,
                        s.subject_name as subject_name
                    FROM questions q
                    JOIN topics t ON q.topic_id = t.topic_id
                    JOIN units u ON t.unit_id = u.unit_id
                    JOIN subjects s ON u.subject_id = s.subject_id
                    WHERE q.question_id = %s
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
                    SELECT option_text FROM question_options 
                    WHERE option_id = %s
                """, (answer_option_id,))
                
                result = conn.cursor.fetchone()
                if result and isinstance(result, dict):
                    return result.get('option_text')
                return None
                
        except Exception as e:
            return None