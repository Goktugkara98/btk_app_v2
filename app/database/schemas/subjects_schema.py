# =============================================================================
# SUBJECTS TABLE SCHEMA
# =============================================================================
# Dersler tablosu için Python şeması
# =============================================================================

SUBJECTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES grades(grade_id) ON DELETE CASCADE,
    INDEX idx_subjects_name (subject_name),
    INDEX idx_subjects_grade (grade_id),
    INDEX idx_subjects_active (is_active),
    UNIQUE KEY unique_subject_per_grade (grade_id, subject_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# JSON dosyalarından dinamik olarak doldurulacak
SUBJECTS_SAMPLE_DATA = "" 