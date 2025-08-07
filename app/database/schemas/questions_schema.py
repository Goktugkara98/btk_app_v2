# =============================================================================
# QUESTIONS TABLE SCHEMA
# =============================================================================
# Sorular tablosu için Python şeması
# =============================================================================

QUESTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    name TEXT NOT NULL,
    name_id VARCHAR(100) NOT NULL,
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    question_type ENUM('multiple_choice', 'true_false', 'fill_blank', 'essay') DEFAULT 'multiple_choice',
    points INT DEFAULT 1,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    INDEX idx_questions_topic (topic_id),
    INDEX idx_questions_name_id (name_id),
    INDEX idx_questions_difficulty (difficulty_level),
    INDEX idx_questions_type (question_type),
    INDEX idx_questions_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

QUESTIONS_SAMPLE_DATA = """
INSERT INTO questions (name, name_id, topic_id, difficulty_level, question_type, points) VALUES
-- Matematik Soruları (Sayılar konusu - topic_id: 1)
('5 + 3 = ?', 'math_addition_1', 1, 'easy', 'multiple_choice', 1),
('12 x 4 = ?', 'math_multiplication_1', 1, 'medium', 'multiple_choice', 2),
('25 ÷ 5 = ?', 'math_division_1', 1, 'easy', 'multiple_choice', 1),
('100 - 37 = ?', 'math_subtraction_1', 1, 'medium', 'multiple_choice', 2),
('8² = ?', 'math_power_1', 1, 'hard', 'multiple_choice', 3)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    difficulty_level = VALUES(difficulty_level),
    points = VALUES(points);
""" 