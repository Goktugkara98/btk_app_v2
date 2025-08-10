# =============================================================================
# USERS TABLE SCHEMA
# =============================================================================
# Kullanıcılar tablosu için Python şeması
# =============================================================================

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    birth_date DATE,
    gender ENUM('male', 'female', 'other'),
    country VARCHAR(100),
    city VARCHAR(100),
    school VARCHAR(100),
    phone VARCHAR(20),
    bio TEXT,
    avatar_path VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

USERS_SAMPLE_DATA = """
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, birth_date, gender, country, city, school, bio, is_admin) VALUES
('admin', 'admin@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Admin', 'User', '+90 555 123 4567', '1990-01-01', 'male', 'Turkey', 'Ankara', 'BTK Akademi', 'Sistem yöneticisi', true),
('demo_user', 'demo@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Demo', 'User', '+90 555 987 6543', '2000-05-15', 'female', 'Turkey', 'Istanbul', 'Demo Okulu', 'Demo kullanıcı hesabı', false),
('test_user', 'test@btk.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Test', 'User', '+90 555 111 2222', '1995-12-20', 'other', 'Turkey', 'Izmir', 'Test Okulu', 'Test kullanıcı hesabı', false)
ON DUPLICATE KEY UPDATE 
    username = VALUES(username),
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    phone = VALUES(phone),
    birth_date = VALUES(birth_date),
    gender = VALUES(gender),
    country = VALUES(country),
    city = VALUES(city),
    school = VALUES(school),
    bio = VALUES(bio);
"""