# =============================================================================
# GRADES TABLE SCHEMA
# =============================================================================
# Sınıflar tablosu için Python şeması
# =============================================================================

GRADES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    name_id VARCHAR(30) NOT NULL,
    level INT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_grade_level (level),
    UNIQUE KEY unique_grade_name_id (name_id),
    INDEX idx_grades_level (level),
    INDEX idx_grades_name_id (name_id),
    INDEX idx_grades_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# JSON dosyalarından dinamik olarak doldurulacak
GRADES_SAMPLE_DATA = "" 