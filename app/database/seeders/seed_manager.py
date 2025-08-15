from typing import Optional, Dict, Tuple
from app.database.db_connection import DatabaseConnection
from .curriculum_seeder import CurriculumSeeder
from .questions_seeder import QuestionsSeeder
from .users_seeder import UsersSeeder


class SeedManager:
    """Aggregate seeder operations behind a simple API."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.curriculum = CurriculumSeeder(self.db)
        self.questions = QuestionsSeeder(db_connection=self.db)
        self.users = UsersSeeder(self.db)

    # Curriculum
    def seed_grades_if_empty(self) -> bool:
        return self.curriculum.seed_grades_if_empty()

    def seed_curriculum(self) -> bool:
        return self.curriculum.seed_curriculum()

    # Questions
    def seed_all_questions(self) -> Dict[str, Tuple[int, int]]:
        return self.questions.seed_all()

    def seed_questions_from_dir(self, directory: str) -> Dict[str, Tuple[int, int]]:
        return self.questions.seed_from_dir(directory)

    def seed_questions_file(self, file_path: str) -> Tuple[int, int]:
        return self.questions.seed_file(file_path)

    # Users (dev only)
    def seed_default_users(self) -> bool:
        return self.users.seed_default_users()

    def close(self) -> None:
        if self.own_connection:
            self.db.close()
