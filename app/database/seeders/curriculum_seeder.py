from typing import Optional, Dict
from app.database.db_connection import DatabaseConnection
from app.database.curriculum_data_loader import JSONDataLoader


class CurriculumSeeder:
    """Seed grades/subjects/units/topics from JSON files (idempotent)."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.loader = JSONDataLoader()

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
            self.loader.load_all_grade_files()
            self.loader.extract_subjects()
            self.loader.extract_units()
            self.loader.extract_topics()

            with self.db as conn:
                # Grades
                grades_sql = self.loader.generate_grades_sql()
                if grades_sql:
                    conn.cursor.execute(grades_sql)
                    conn.connection.commit()

                # Subjects
                grade_map: Dict[int, int] = self.loader.get_grade_id_map(conn)
                subjects_sql = self.loader.generate_subjects_sql(grade_map)
                if subjects_sql:
                    conn.cursor.execute(subjects_sql)
                    conn.connection.commit()

                # Units
                subject_map = self.loader.get_subject_id_map(conn)
                units_sql = self.loader.generate_units_sql(subject_map)
                if units_sql:
                    conn.cursor.execute(units_sql)
                    conn.connection.commit()

                # Topics
                unit_map = self.loader.get_unit_id_map(conn)
                topics_sql = self.loader.generate_topics_sql(unit_map)
                if topics_sql:
                    conn.cursor.execute(topics_sql)
                    conn.connection.commit()
            return True
        except Exception:
            # Silently continue if JSON missing/corrupt to avoid breaking app startup
            return False
