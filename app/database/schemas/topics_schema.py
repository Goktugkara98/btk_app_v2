# =============================================================================
# TOPICS TABLE SCHEMA
# =============================================================================
# Konular tablosu için Python şeması
# =============================================================================

TOPICS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_id VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
    INDEX idx_topics_name (name),
    INDEX idx_topics_name_id (name_id),
    INDEX idx_topics_unit (unit_id),
    INDEX idx_topics_active (is_active),
    UNIQUE KEY unique_topic_unit (name_id, unit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# JSON dosyalarından dinamik olarak doldurulacak
TOPICS_SAMPLE_DATA = "" 