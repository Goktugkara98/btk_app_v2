# =============================================================================
# UNITS TABLE SCHEMA
# =============================================================================
# Üniteler tablosu için Python şeması
# =============================================================================

UNITS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    unit_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    INDEX idx_units_name (unit_name),
    INDEX idx_units_subject (subject_id),
    INDEX idx_units_active (is_active),
    UNIQUE KEY unique_unit_per_subject (subject_id, unit_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# JSON dosyalarından dinamik olarak doldurulacak
UNITS_SAMPLE_DATA = "" 