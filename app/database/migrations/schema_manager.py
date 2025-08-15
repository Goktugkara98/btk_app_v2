from typing import Optional
from app.database.db_connection import DatabaseConnection
from app.database.schemas import (
    GRADES_TABLE_SQL,
    SUBJECTS_TABLE_SQL,
    UNITS_TABLE_SQL,
    TOPICS_TABLE_SQL,
    QUESTIONS_TABLE_SQL,
    QUESTION_OPTIONS_TABLE_SQL,
    USERS_TABLE_SQL,
    QUIZ_SESSIONS_TABLE_SQL,
    QUIZ_SESSION_QUESTIONS_TABLE_SQL,
)
from app.database.schemas.chat_sessions_schema import get_chat_sessions_schema
from app.database.schemas.chat_messages_schema import get_chat_messages_schema


class SchemaManager:
    """Create/drop database tables in the correct FK order (idempotent)."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

        self.table_schemas = {
            'grades': GRADES_TABLE_SQL,
            'subjects': SUBJECTS_TABLE_SQL,
            'units': UNITS_TABLE_SQL,
            'topics': TOPICS_TABLE_SQL,
            'questions': QUESTIONS_TABLE_SQL,
            'question_options': QUESTION_OPTIONS_TABLE_SQL,
            'users': USERS_TABLE_SQL,
            'quiz_sessions': QUIZ_SESSIONS_TABLE_SQL,
            'quiz_session_questions': QUIZ_SESSION_QUESTIONS_TABLE_SQL,
            'chat_sessions': get_chat_sessions_schema(),
            'chat_messages': get_chat_messages_schema(),
        }
        self.table_order = [
            'grades', 'subjects', 'units', 'topics',
            'questions', 'question_options', 'users',
            'quiz_sessions', 'quiz_session_questions',
            'chat_sessions', 'chat_messages'
        ]

    def ensure_tables(self) -> bool:
        try:
            with self.db as conn:
                for table in self.table_order:
                    sql = self.table_schemas[table]
                    conn.cursor.execute(sql)
                    conn.connection.commit()
            return True
        except Exception:
            return False

    def drop_all_tables(self) -> bool:
        try:
            with self.db as conn:
                for table in reversed(self.table_order):
                    conn.cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    conn.connection.commit()
            return True
        except Exception:
            return False

    def force_recreate(self) -> bool:
        return self.drop_all_tables() and self.ensure_tables()
