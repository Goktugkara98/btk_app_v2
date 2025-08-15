# =============================================================================
# QUESTION OPTIONS TABLE SCHEMA
# =============================================================================
# Soru seçenekleri tablosu için Python şeması
# =============================================================================

QUESTION_OPTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS question_options (
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_options_question (question_id),
    INDEX idx_options_correct (is_correct),
    INDEX idx_options_qid_correct (question_id, is_correct)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
