# =============================================================================
# QUIZ SESSIONS TABLE SCHEMA
# =============================================================================
# Quiz oturumları tablosu için Python şeması
# =============================================================================

QUIZ_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS quiz_sessions (
    session_id VARCHAR(64) NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    grade_id INT NULL,
    subject_id INT NULL,
    unit_id INT NULL,
    topic_id INT NULL,
    selection_scope ENUM('topic', 'unit', 'subject', 'grade', 'global') DEFAULT 'topic',
    difficulty_level ENUM('random', 'easy', 'medium', 'hard') DEFAULT 'random',
    quiz_mode ENUM('educational', 'exam') DEFAULT 'educational',
    question_count INT DEFAULT 10,
    timer_enabled BOOLEAN DEFAULT true,
    timer_duration_seconds INT DEFAULT 1800,
    remaining_time_seconds INT DEFAULT 0,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    total_score INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    completion_time_seconds INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (grade_id) REFERENCES grades(grade_id) ON DELETE SET NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE SET NULL,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE SET NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE SET NULL,
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_scope (selection_scope),
    INDEX idx_sessions_status (status),
    INDEX idx_sessions_start_time (start_time),
    INDEX idx_sessions_grade_subject (grade_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""