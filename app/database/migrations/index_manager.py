from typing import Optional
from app.database.db_connection import DatabaseConnection


class IndexManager:
    """Ensure critical performance indexes exist (idempotent)."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None) -> None:
        self.db = db_connection or DatabaseConnection()
        self.own_connection = db_connection is None

    def ensure_indexes(self) -> bool:
        try:
            with self.db as conn:
                # Get current DB name
                conn.cursor.execute("SELECT DATABASE() AS db")
                row = conn.cursor.fetchone() or {}
                db_name = row.get('db')
                if not db_name:
                    return False

                def ensure_index(table: str, index_name: str, cols_sql: str) -> None:
                    exists_sql = (
                        "SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS "
                        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND INDEX_NAME=%s LIMIT 1"
                    )
                    conn.cursor.execute(exists_sql, (db_name, table, index_name))
                    exists = conn.cursor.fetchone()
                    if not exists:
                        conn.cursor.execute(f"ALTER TABLE {table} ADD INDEX {index_name} {cols_sql}")
                        conn.connection.commit()

                # Ensure required indexes
                ensure_index('questions', 'idx_q_topic_active_diff_qid', '(topic_id, is_active, difficulty_level, question_id)')
                ensure_index('questions', 'idx_q_active_diff_qid', '(is_active, difficulty_level, question_id)')
                ensure_index('question_options', 'idx_options_qid_correct', '(question_id, is_correct)')
                return True
        except Exception:
            return False
