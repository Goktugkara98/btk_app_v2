# =============================================================================
# QUESTION OPTIONS TABLE SCHEMA
# =============================================================================
# Soru seçenekleri tablosu için Python şeması
# =============================================================================

QUESTION_OPTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    name TEXT NOT NULL,
    name_id VARCHAR(100) NOT NULL,
    is_correct BOOLEAN DEFAULT false,
    option_order INT DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_options_question (question_id),
    INDEX idx_options_name_id (name_id),
    INDEX idx_options_correct (is_correct),
    INDEX idx_options_order (option_order),
    INDEX idx_options_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

QUESTION_OPTIONS_SAMPLE_DATA = """
INSERT INTO question_options (question_id, name, name_id, is_correct, option_order) VALUES
-- 5 + 3 = ? (question_id: 1)
(1, '7', 'option_7', false, 1),
(1, '8', 'option_8', true, 2),
(1, '9', 'option_9', false, 3),
(1, '10', 'option_10', false, 4),

-- 12 x 4 = ? (question_id: 2)
(2, '44', 'option_44', false, 1),
(2, '46', 'option_46', false, 2),
(2, '48', 'option_48', true, 3),
(2, '50', 'option_50', false, 4)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    is_correct = VALUES(is_correct),
    option_order = VALUES(option_order);
""" 