from typing import Optional, Dict, Tuple
from pathlib import Path
from app.database.db_connection import DatabaseConnection
from app.database.quiz_data_loader import QuestionLoader


class QuestionsSeeder:
    """Seed questions and options from JSON files (idempotent behavior at file level)."""

    def __init__(self, data_dir: str = "app/data/quiz_banks", db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None
        self.data_dir = Path(data_dir)
        self.loader = QuestionLoader(data_dir=str(self.data_dir), db_connection=self.db)

    def seed_all(self) -> Dict[str, Tuple[int, int]]:
        return self.loader.process_all_question_files()

    def seed_from_dir(self, directory: str) -> Dict[str, Tuple[int, int]]:
        self.loader.data_dir = Path(directory)
        return self.loader.process_all_question_files()

    def seed_file(self, file_path: str) -> Tuple[int, int]:
        return self.loader.process_question_file(file_path)

    def close(self) -> None:
        if self.own_connection:
            self.db.close()
