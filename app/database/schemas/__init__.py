# =============================================================================
# DATABASE SCHEMAS INIT
# =============================================================================
# Tüm veritabanı şemalarını import eder
# =============================================================================

# Grades (Sınıflar) şeması
from .grades_schema import GRADES_TABLE_SQL

# Subjects (Dersler) şeması
from .subjects_schema import SUBJECTS_TABLE_SQL

# Units (Üniteler) şeması
from .units_schema import UNITS_TABLE_SQL

# Topics (Konular) şeması
from .topics_schema import TOPICS_TABLE_SQL

# Questions (Sorular) şeması
from .questions_schema import QUESTIONS_TABLE_SQL

# Question Options (Soru Seçenekleri) şeması
from .question_options_schema import QUESTION_OPTIONS_TABLE_SQL

# Users (Kullanıcılar) şeması
from .users_schema import USERS_TABLE_SQL

# Quiz Sessions (Quiz Oturumları) şeması
from .quiz_sessions_schema import QUIZ_SESSIONS_TABLE_SQL

# Quiz Session Questions (Quiz Oturumu Soruları) şeması
from .quiz_session_questions_schema import QUIZ_SESSION_QUESTIONS_TABLE_SQL

# Tüm şemaları export et
__all__ = [
    'GRADES_TABLE_SQL',
    'SUBJECTS_TABLE_SQL',
    'UNITS_TABLE_SQL',
    'TOPICS_TABLE_SQL',
    'QUESTIONS_TABLE_SQL',
    'QUESTION_OPTIONS_TABLE_SQL',
    'USERS_TABLE_SQL',
    'QUIZ_SESSIONS_TABLE_SQL',
    'QUIZ_SESSION_QUESTIONS_TABLE_SQL'
]