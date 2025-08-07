# =============================================================================
# QUIZ SESSION QUESTIONS TABLE SCHEMA
# =============================================================================
# Quiz oturumu soruları tablosu için Python şeması
# =============================================================================

QUIZ_SESSION_QUESTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS quiz_session_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    question_id INT NOT NULL,
    question_order INT NOT NULL,
    user_answer_option_id INT NULL,
    is_correct BOOLEAN NULL,
    points_earned INT DEFAULT 0,
    time_spent_seconds INT DEFAULT 0,
    answered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_answer_option_id) REFERENCES question_options(id) ON DELETE SET NULL,
    INDEX idx_session_questions_session (session_id),
    INDEX idx_session_questions_question (question_id),
    INDEX idx_session_questions_order (question_order),
    INDEX idx_session_questions_correct (is_correct),
    UNIQUE KEY unique_session_question (session_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

QUIZ_SESSION_QUESTIONS_SAMPLE_DATA = "" 