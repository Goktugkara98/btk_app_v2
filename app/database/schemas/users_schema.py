# =============================================================================
# USERS TABLE SCHEMA
# =============================================================================
# Kullanıcılar tablosu için Python şeması
# =============================================================================

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade_level_id INT,
    username VARCHAR(100) NOT NULL,
    name_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    birth_date DATE,
    gender ENUM('male', 'female', 'other'),
    school VARCHAR(100),
    bio TEXT,
    avatar_path VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_level_id) REFERENCES grades(id) ON DELETE SET NULL,
    INDEX idx_users_username (username),
    INDEX idx_users_name_id (name_id),
    INDEX idx_users_email (email),
    INDEX idx_users_active (is_active),
    INDEX idx_users_grade (grade_level_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

USERS_SAMPLE_DATA = """
INSERT INTO users (username, name_id, email, password_hash, first_name, last_name, phone, birth_date, gender, school, grade_level_id, bio, is_admin) VALUES
('admin', 'admin', 'admin@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Admin', 'User', '+90 555 123 4567', '1990-01-01', 'male', 'BTK Akademi', 1, 'Sistem yöneticisi', true),
('demo_user', 'demo_user', 'demo@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Demo', 'User', '+90 555 987 6543', '2000-05-15', 'female', 'Demo Okulu', 1, 'Demo kullanıcı hesabı', false),
('test_user', 'test_user', 'test@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Test', 'User', '+90 555 111 2222', '1995-12-20', 'other', 'Test Okulu', 1, 'Test kullanıcı hesabı', false)
ON DUPLICATE KEY UPDATE 
    username = VALUES(username),
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    phone = VALUES(phone),
    birth_date = VALUES(birth_date),
    gender = VALUES(gender),
    school = VALUES(school),
    grade_level_id = VALUES(grade_level_id),
    bio = VALUES(bio);
""" 