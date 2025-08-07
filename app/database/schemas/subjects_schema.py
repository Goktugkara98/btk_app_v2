# =============================================================================
# SUBJECTS TABLE SCHEMA
# =============================================================================
# Dersler tablosu için Python şeması
# =============================================================================

SUBJECTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_id VARCHAR(30) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    INDEX idx_subjects_name (name),
    INDEX idx_subjects_name_id (name_id),
    INDEX idx_subjects_grade (grade_id),
    INDEX idx_subjects_active (is_active),
    UNIQUE KEY unique_subject_grade (name_id, grade_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# JSON dosyalarından dinamik olarak doldurulacak
SUBJECTS_SAMPLE_DATA = "" 