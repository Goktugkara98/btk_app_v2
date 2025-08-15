from typing import Optional, Dict, Tuple, List
from pathlib import Path
import json
from app.database.db_connection import DatabaseConnection


class CurriculumSeeder:
    """Seed grades/subjects/units/topics from JSON files (idempotent)."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None, data_dir: str = "app/data/curriculum_structure") -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.data_dir = Path(data_dir)
        # in-memory extracted data
        self._grades_data: Dict[int, dict] = {}
        self._subjects_data: List[Tuple[int, str, str, str]] = []
        self._units_data: List[Tuple[int, str, str, str, str]] = []
        self._topics_data: List[Tuple[int, str, str, str, str, str]] = []

    def seed_grades_if_empty(self) -> bool:
        try:
            with self.db as conn:
                conn.cursor.execute("SELECT COUNT(*) AS cnt FROM grades")
                row = conn.cursor.fetchone() or {}
                if (row.get('cnt') or 0) > 0:
                    return True

                values = [
                    f"({i}, '{i}. Sınıf', '{i}. Sınıf seviyesi', 1)"
                    for i in range(1, 13)
                ]
                sql = (
                    "INSERT INTO grades (grade_id, grade_name, description, is_active) VALUES "
                    + ", ".join(values)
                    + " ON DUPLICATE KEY UPDATE grade_name=VALUES(grade_name)"
                )
                conn.cursor.execute(sql)
                conn.connection.commit()
            return True
        except Exception:
            return False

    def seed_curriculum(self) -> bool:
        try:
            # Load JSONs and precompute extracts
            self._load_all_grade_files()
            self._extract_subjects()
            self._extract_units()
            self._extract_topics()

            with self.db as conn:
                # Grades
                grades_sql = self._generate_grades_sql()
                if grades_sql:
                    conn.cursor.execute(grades_sql)
                    conn.connection.commit()

                # Subjects
                grade_map: Dict[int, int] = self._get_grade_id_map(conn)
                subjects_sql = self._generate_subjects_sql(grade_map)
                if subjects_sql:
                    conn.cursor.execute(subjects_sql)
                    conn.connection.commit()

                # Units
                subject_map = self._get_subject_id_map(conn)
                units_sql = self._generate_units_sql(subject_map)
                if units_sql:
                    conn.cursor.execute(units_sql)
                    conn.connection.commit()

                # Topics
                unit_map = self._get_unit_id_map(conn)
                topics_sql = self._generate_topics_sql(unit_map)
                if topics_sql:
                    conn.cursor.execute(topics_sql)
                    conn.connection.commit()
            return True
        except Exception:
            # Silently continue if JSON missing/corrupt to avoid breaking app startup
            return False

    # ---- Internal helpers (inlined from former JSONDataLoader) ----
    def _load_all_grade_files(self) -> Dict[int, dict]:
        if not self.data_dir.exists():
            return {}
        grade_files = list(self.data_dir.glob("grade_*.json"))
        if not grade_files:
            return {}
        for file_path in grade_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data and isinstance(data, list) and len(data) > 0:
                    grade_info = data[0]
                    grade_level = grade_info.get('gradeLevel')
                    if grade_level:
                        self._grades_data[grade_level] = grade_info
            except Exception:
                continue
        return self._grades_data

    def _extract_subjects(self) -> List[Tuple[int, str, str, str]]:
        subjects: List[Tuple[int, str, str, str]] = []
        for grade_level, grade_data in self._grades_data.items():
            for course in grade_data.get('subjects', []):
                course_id = course.get('subjectId')
                course_name = course.get('subjectName')
                if course_id and course_name:
                    subjects.append((grade_level, course_id, course_name, f'{course_name} dersi'))
        self._subjects_data = subjects
        return subjects

    def _extract_units(self) -> List[Tuple[int, str, str, str, str]]:
        units: List[Tuple[int, str, str, str, str]] = []
        for grade_level, grade_data in self._grades_data.items():
            for course in grade_data.get('subjects', []):
                course_id = course.get('subjectId')
                for unit in course.get('units', []):
                    unit_id = unit.get('unitId')
                    unit_name = unit.get('unitName')
                    if unit_id and unit_name:
                        units.append((grade_level, course_id, unit_id, unit_name, f'{unit_name} ünitesi'))
        self._units_data = units
        return units

    def _extract_topics(self) -> List[Tuple[int, str, str, str, str, str]]:
        topics: List[Tuple[int, str, str, str, str, str]] = []
        for grade_level, grade_data in self._grades_data.items():
            for course in grade_data.get('subjects', []):
                course_id = course.get('subjectId')
                for unit in course.get('units', []):
                    unit_id = unit.get('unitId')
                    unit_name = unit.get('unitName')
                    for topic in unit.get('topics', []):
                        if isinstance(topic, dict):
                            topic_id = topic.get('topicId')
                            topic_name = topic.get('topicName')
                            if topic_id and topic_name:
                                topics.append((grade_level, course_id, unit_id, topic_id, topic_name, f'{unit_name} - {topic_name}'))
                        elif isinstance(topic, str) and topic:
                            topics.append((grade_level, course_id, unit_id, topic.lower().replace(' ', '_'), topic, f'{unit_name} - {topic}'))
        self._topics_data = topics
        return topics

    def _generate_grades_sql(self) -> str:
        if not self._grades_data:
            return ""
        values: List[str] = []
        for grade_level, grade_data in self._grades_data.items():
            grade_name = grade_data.get('gradeName', f'{grade_level}. Sınıf')
            description = f'{grade_name} seviyesi'
            # escape quotes
            grade_name_esc = grade_name.replace("'", "''")
            description_esc = description.replace("'", "''")
            values.append(f"('{grade_name_esc}', '{description_esc}')")
        if not values:
            return ""
        return (
            """
INSERT INTO grades (grade_name, description) VALUES
{values}
ON DUPLICATE KEY UPDATE 
    grade_name = VALUES(grade_name),
    description = VALUES(description);
            """
        ).replace("{values}", ", ".join(values))

    def _generate_subjects_sql(self, grade_id_map: Dict[int, int]) -> str:
        if not self._subjects_data:
            return ""
        values: List[str] = []
        for grade_level, subject_code, subject_name, description in self._subjects_data:
            grade_id = grade_id_map.get(grade_level)
            if grade_id:
                subject_name_esc = subject_name.replace("'", "''")
                description_esc = description.replace("'", "''")
                values.append(f"({grade_id}, '{subject_name_esc}', '{description_esc}')")
        if not values:
            return ""
        return (
            """
INSERT INTO subjects (grade_id, subject_name, description) VALUES
{values}
ON DUPLICATE KEY UPDATE 
    subject_name = VALUES(subject_name),
    description = VALUES(description);
            """
        ).replace("{values}", ", ".join(values))

    def _generate_units_sql(self, subject_id_map: Dict[Tuple[int, str], int]) -> str:
        if not self._units_data:
            return ""
        values: List[str] = []
        for grade_level, subject_code, unit_id, unit_name, description in self._units_data:
            subject_id = subject_id_map.get((grade_level, subject_code))
            if subject_id:
                unit_name_esc = unit_name.replace("'", "''")
                description_esc = description.replace("'", "''")
                values.append(f"({subject_id}, '{unit_name_esc}', '{description_esc}')")
        if not values:
            return ""
        return (
            """
INSERT INTO units (subject_id, unit_name, description) VALUES
{values}
ON DUPLICATE KEY UPDATE 
    unit_name = VALUES(unit_name),
    description = VALUES(description);
            """
        ).replace("{values}", ", ".join(values))

    def _generate_topics_sql(self, unit_id_map: Dict[Tuple[int, str, str], int]) -> str:
        if not self._topics_data:
            return ""
        values: List[str] = []
        for grade_level, subject_code, unit_id, topic_id, topic_name, description in self._topics_data:
            db_unit_id = unit_id_map.get((grade_level, subject_code, unit_id))
            if db_unit_id:
                topic_name_esc = topic_name.replace("'", "''")
                description_esc = description.replace("'", "''")
                values.append(f"({db_unit_id}, '{topic_name_esc}', '{description_esc}')")
        if not values:
            return ""
        return (
            """
INSERT INTO topics (unit_id, topic_name, description) VALUES
{values}
ON DUPLICATE KEY UPDATE 
    topic_name = VALUES(topic_name),
    description = VALUES(description);
            """
        ).replace("{values}", ", ".join(values))

    # ID maps using existing connection
    def _get_grade_id_map(self, conn) -> Dict[int, int]:
        grade_id_map: Dict[int, int] = {}
        try:
            for grade_level in self._grades_data.keys():
                grade_name = self._grades_data.get(grade_level, {}).get('gradeName', f'{grade_level}. Sınıf')
                conn.cursor.execute(
                    "SELECT grade_id FROM grades WHERE grade_name = %s",
                    (grade_name,)
                )
                result = conn.cursor.fetchone()
                if result:
                    grade_id_map[grade_level] = result['grade_id']
        except Exception:
            return {}
        return grade_id_map

    def _get_subject_id_map(self, conn) -> Dict[Tuple[int, str], int]:
        subject_id_map: Dict[Tuple[int, str], int] = {}
        try:
            for grade_level, subject_code, subject_name, _ in self._subjects_data:
                grade_name = self._grades_data.get(grade_level, {}).get('gradeName', f'{grade_level}. Sınıf')
                conn.cursor.execute(
                    "SELECT s.subject_id FROM subjects s JOIN grades g ON s.grade_id = g.grade_id WHERE s.subject_name = %s AND g.grade_name = %s",
                    (subject_name, grade_name)
                )
                result = conn.cursor.fetchone()
                if result:
                    subject_id_map[(grade_level, subject_code)] = result['subject_id']
        except Exception:
            return {}
        return subject_id_map

    def _get_unit_id_map(self, conn) -> Dict[Tuple[int, str, str], int]:
        unit_id_map: Dict[Tuple[int, str, str], int] = {}
        try:
            for grade_level, subject_code, unit_id, unit_name, _ in self._units_data:
                # find subject_name for this subject_code at grade_level
                subject_name = None
                for gl, sc, sn, _desc in self._subjects_data:
                    if gl == grade_level and sc == subject_code:
                        subject_name = sn
                        break
                if not subject_name:
                    continue
                conn.cursor.execute(
                    (
                        """
                        SELECT u.unit_id
                        FROM units u
                        JOIN subjects s ON u.subject_id = s.subject_id
                        JOIN grades g ON s.grade_id = g.grade_id
                        WHERE u.unit_name = %s AND s.subject_name = %s AND g.grade_name = %s
                        """
                    ),
                    (unit_name, subject_name, self._grades_data.get(grade_level, {}).get('gradeName', f'{grade_level}. Sınıf'))
                )
                result = conn.cursor.fetchone()
                if result:
                    unit_id_map[(grade_level, subject_code, unit_id)] = result['unit_id']
        except Exception:
            return {}
        return unit_id_map
