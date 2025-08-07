# =============================================================================
# QUIZ SESSIONS TABLE SCHEMA
# =============================================================================
# Quiz oturumları tablosu için Python şeması
# =============================================================================

QUIZ_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    grade_id INT NOT NULL,
    subject_id INT NOT NULL,
    unit_id INT,
    topic_id INT NOT NULL,
    difficulty_level ENUM('random', 'easy', 'medium', 'hard') DEFAULT 'random',
    timer_enabled BOOLEAN DEFAULT true,
    timer_duration INT DEFAULT 30,
    remaining_time_seconds INT DEFAULT 0,
    quiz_mode ENUM('educational', 'exam') DEFAULT 'educational',
    question_count INT DEFAULT 10,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    total_score INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    completion_time_seconds INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_session_id (session_id),
    INDEX idx_sessions_status (status),
    INDEX idx_sessions_start_time (start_time),
    INDEX idx_sessions_grade_subject (grade_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

QUIZ_SESSIONS_SAMPLE_DATA = "" 