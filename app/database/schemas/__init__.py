# =============================================================================
# DATABASE SCHEMAS INIT
# =============================================================================
# Tüm veritabanı şemalarını import eder
# =============================================================================

# Grades (Sınıflar) şeması
from .grades_schema import GRADES_TABLE_SQL, GRADES_SAMPLE_DATA

# Subjects (Dersler) şeması
from .subjects_schema import SUBJECTS_TABLE_SQL, SUBJECTS_SAMPLE_DATA

# Units (Üniteler) şeması
from .units_schema import UNITS_TABLE_SQL, UNITS_SAMPLE_DATA

# Topics (Konular) şeması
from .topics_schema import TOPICS_TABLE_SQL, TOPICS_SAMPLE_DATA

# Questions (Sorular) şeması
from .questions_schema import QUESTIONS_TABLE_SQL, QUESTIONS_SAMPLE_DATA

# Question Options (Soru Seçenekleri) şeması
from .question_options_schema import QUESTION_OPTIONS_TABLE_SQL, QUESTION_OPTIONS_SAMPLE_DATA

# Users (Kullanıcılar) şeması
from .users_schema import USERS_TABLE_SQL, USERS_SAMPLE_DATA

# Quiz Sessions (Quiz Oturumları) şeması
from .quiz_sessions_schema import QUIZ_SESSIONS_TABLE_SQL, QUIZ_SESSIONS_SAMPLE_DATA

# Quiz Session Questions (Quiz Oturumu Soruları) şeması
from .quiz_session_questions_schema import QUIZ_SESSION_QUESTIONS_TABLE_SQL, QUIZ_SESSION_QUESTIONS_SAMPLE_DATA

# Tüm şemaları export et
__all__ = [
    'GRADES_TABLE_SQL', 'GRADES_SAMPLE_DATA',
    'SUBJECTS_TABLE_SQL', 'SUBJECTS_SAMPLE_DATA',
    'UNITS_TABLE_SQL', 'UNITS_SAMPLE_DATA',
    'TOPICS_TABLE_SQL', 'TOPICS_SAMPLE_DATA',
    'QUESTIONS_TABLE_SQL', 'QUESTIONS_SAMPLE_DATA',
    'QUESTION_OPTIONS_TABLE_SQL', 'QUESTION_OPTIONS_SAMPLE_DATA',
    'USERS_TABLE_SQL', 'USERS_SAMPLE_DATA',
    'QUIZ_SESSIONS_TABLE_SQL', 'QUIZ_SESSIONS_SAMPLE_DATA',
    'QUIZ_SESSION_QUESTIONS_TABLE_SQL', 'QUIZ_SESSION_QUESTIONS_SAMPLE_DATA'
] 