# =============================================================================
# QUESTIONS TABLE SCHEMA
# =============================================================================
# Sorular tablosu için Python şeması
# =============================================================================

QUESTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    question_text TEXT NOT NULL,
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    question_type ENUM('multiple_choice', 'true_false', 'fill_blank', 'essay') DEFAULT 'multiple_choice',
    points INT DEFAULT 1,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    INDEX idx_questions_topic (topic_id),
    INDEX idx_questions_difficulty (difficulty_level),
    INDEX idx_questions_type (question_type),
    INDEX idx_questions_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

