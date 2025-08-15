# =============================================================================
# TOPICS TABLE SCHEMA
# =============================================================================
# Konular tablosu için Python şeması
# =============================================================================

TOPICS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id INT NOT NULL,
    topic_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    INDEX idx_topics_name (topic_name),
    INDEX idx_topics_unit (unit_id),
    INDEX idx_topics_active (is_active),
    UNIQUE KEY unique_topic_per_unit (unit_id, topic_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""