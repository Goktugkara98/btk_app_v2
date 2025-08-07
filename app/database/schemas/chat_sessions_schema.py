# =============================================================================
# CHAT SESSIONS SCHEMA
# =============================================================================
# Bu modül, AI chat session'larını saklamak için veritabanı şemasını tanımlar.
# Her soru için ayrı chat session oluşturulur.
# =============================================================================

def get_chat_sessions_schema():
    """Chat sessions tablosu için SQL şeması döndürür."""
    return """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(255) UNIQUE NOT NULL COMMENT 'Unique chat session identifier',
        quiz_session_id VARCHAR(255) NOT NULL COMMENT 'Quiz session reference',
        question_id INT NOT NULL COMMENT 'Specific question this chat is about',
        user_id INT COMMENT 'User who owns this chat session',
        
        -- Context bilgileri
        subject_name VARCHAR(100) COMMENT 'Subject context',
        topic_name VARCHAR(100) COMMENT 'Topic context', 
        difficulty_level VARCHAR(20) COMMENT 'Question difficulty level',
        
        -- Session durumu
        status ENUM('active', 'completed', 'archived') DEFAULT 'active',
        message_count INT DEFAULT 0 COMMENT 'Total messages in this session',
        
        -- Zaman damgaları
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Foreign key constraints (temporarily disabled for development)
        -- FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
        
        -- Indexes for performance
        INDEX idx_quiz_session (quiz_session_id),
        INDEX idx_question (question_id),
        INDEX idx_user (user_id),
        INDEX idx_status (status),
        INDEX idx_last_activity (last_activity)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
