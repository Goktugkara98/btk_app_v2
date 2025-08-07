# =============================================================================
# CHAT MESSAGES SCHEMA
# =============================================================================
# Bu modül, AI chat mesajlarını saklamak için veritabanı şemasını tanımlar.
# Tüm user-AI etkileşimleri kaydedilir.
# =============================================================================

def get_chat_messages_schema():
    """Chat messages tablosu için SQL şeması döndürür."""
    return """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chat_session_id VARCHAR(255) NOT NULL COMMENT 'Chat session reference',
        
        -- Mesaj bilgileri
        message_type ENUM('user', 'ai', 'system') NOT NULL,
        content TEXT NOT NULL COMMENT 'Message content',
        
        -- AI specific bilgileri
        action_type VARCHAR(50) COMMENT 'Type of action: general, explain, hint',
        ai_model VARCHAR(50) COMMENT 'AI model used for response',
        prompt_used TEXT COMMENT 'Full prompt sent to AI',
        
        -- Performance metrics
        response_time_ms INT COMMENT 'AI response time in milliseconds',
        token_count INT COMMENT 'Token count for AI requests',
        
        -- Metadata
        metadata JSON COMMENT 'Additional message metadata',
        
        -- Zaman damgaları
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Foreign key constraints
        FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
        
        -- Indexes for performance
        INDEX idx_chat_session (chat_session_id),
        INDEX idx_message_type (message_type),
        INDEX idx_action_type (action_type),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
