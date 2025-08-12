# =============================================================================
# QUESTIONS TABLE SCHEMA
# =============================================================================
# Sorular tablosu için Python şeması
# =============================================================================

QUESTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

QUESTIONS_SAMPLE_DATA = """
INSERT INTO questions (question_text, topic_id, difficulty_level, question_type, points) VALUES
-- Matematik Soruları (Sayılar konusu - topic_id: 1)
('5 + 3 = ?', 1, 'easy', 'multiple_choice', 1),
('12 x 4 = ?', 1, 'medium', 'multiple_choice', 2),
('25 ÷ 5 = ?', 1, 'easy', 'multiple_choice', 1),
('100 - 37 = ?', 1, 'medium', 'multiple_choice', 2),
('8² = ?', 1, 'hard', 'multiple_choice', 3)
ON DUPLICATE KEY UPDATE 
    question_text = VALUES(question_text),
    difficulty_level = VALUES(difficulty_level),
    points = VALUES(points);
"""