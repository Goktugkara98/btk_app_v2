from typing import Optional, Dict, Tuple, Any
from pathlib import Path
import json
from app.database.db_connection import DatabaseConnection


class QuestionsSeeder:
    """Seed questions and options from JSON files (idempotent behavior at file level)."""

    def __init__(self, data_dir: str = "app/data/quiz_banks", db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.data_dir = Path(data_dir)

    # Internal helpers (inlined from former QuestionLoader)
    def _load_question_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _get_topic_id(self, grade: int, subject: str, unit: str, topic: str) -> Optional[int]:
        try:
            query = (
                """
                SELECT t.topic_id 
                FROM topics t
                JOIN units u ON t.unit_id = u.unit_id
                JOIN subjects s ON u.subject_id = s.subject_id
                JOIN grades g ON s.grade_id = g.grade_id
                WHERE g.grade_name = %s 
                  AND s.subject_name = %s 
                  AND u.unit_name = %s 
                  AND t.topic_name = %s
                """
            )
            grade_name = f"{grade}. Sınıf"
            with self.db as conn:
                conn.cursor.execute(query, (grade_name, subject, unit, topic))
                result = conn.cursor.fetchone()
                return result['topic_id'] if result else None
        except Exception:
            return None

    def _insert_question(self, question_data: Dict[str, Any], topic_id: int) -> Optional[int]:
        try:
            with self.db as conn:
                q_sql = (
                    """
                    INSERT INTO questions (question_text, topic_id, difficulty_level, question_type, points, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                )
                q_text = question_data['questionText']
                q_desc = question_data.get('explanation', '')
                q_vals = (q_text, topic_id, question_data['difficulty'], question_data['questionType'], 1, q_desc)
                conn.cursor.execute(q_sql, q_vals)
                question_id = conn.cursor.lastrowid

                for option in question_data['options']:
                    o_sql = (
                        """
                        INSERT INTO question_options (question_id, option_text, is_correct, description)
                        VALUES (%s, %s, %s, %s)
                        """
                    )
                    o_vals = (
                        question_id,
                        option['text'],
                        option['isCorrect'],
                        option.get('explanation', ''),
                    )
                    conn.cursor.execute(o_sql, o_vals)

                return question_id
        except Exception:
            return None

    def _process_question_file(self, file_path: str) -> Tuple[int, int]:
        data = self._load_question_file(file_path)
        if not data:
            return 0, 0

        metadata = data.get('metadata', {})
        questions = data.get('questions', [])
        grade = metadata.get('grade')
        subject = metadata.get('subject')
        unit = metadata.get('unit')
        topic = metadata.get('topic')
        if not all([grade, subject, unit, topic]):
            return 0, len(questions)

        topic_id = self._get_topic_id(grade, subject, unit, topic)
        if not topic_id:
            return 0, len(questions)

        success = 0
        for q in questions:
            if self._insert_question(q, topic_id):
                success += 1
        return success, len(questions)

    def _process_dir(self, dir_path: Path) -> Dict[str, Tuple[int, int]]:
        if not dir_path.exists():
            return {}
        results: Dict[str, Tuple[int, int]] = {}
        json_files = list(dir_path.rglob("*.json"))
        if not json_files:
            return {}
        for fp in json_files:
            results[fp.name] = self._process_question_file(str(fp))
        return results

    # Public API
    def seed_all(self) -> Dict[str, Tuple[int, int]]:
        return self._process_dir(self.data_dir)

    def seed_from_dir(self, directory: str) -> Dict[str, Tuple[int, int]]:
        return self._process_dir(Path(directory))

    def seed_file(self, file_path: str) -> Tuple[int, int]:
        return self._process_question_file(file_path)

    def close(self) -> None:
        if self.own_connection:
            self.db.close()
