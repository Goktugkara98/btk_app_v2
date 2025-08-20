# BTK App - SQLAlchemy Migration Guide

## 🚀 Overview

Bu dokümantasyon, BTK App veritabanının MySQL Connector'dan SQLAlchemy ORM'e geçiş sürecini detaylandırır. Bu geçiş, kod organizasyonunu iyileştirir, veritabanı işlemlerini basitleştirir ve modern Python veritabanı pratiklerini uygular.

## 📋 İçindekiler

1. [Migration Özeti](#migration-özeti)
2. [Yeni Yapı](#yeni-yapı)
3. [Kurulum](#kurulum)
4. [Kullanım](#kullanım)
5. [API Endpoints](#api-endpoints)
6. [Model Yapısı](#model-yapısı)
7. [Repository Pattern](#repository-pattern)
8. [Migration Sistemi](#migration-sistemi)
9. [Örnekler](#örnekler)
10. [Geçiş Rehberi](#geçiş-rehberi)

## 🔄 Migration Özeti

### Önceki Durum
- Raw MySQL Connector kullanımı
- Manuel SQL sorguları
- Basit connection wrapper
- Temel CRUD işlemleri

### Yeni Durum
- SQLAlchemy ORM entegrasyonu
- Flask-SQLAlchemy entegrasyonu
- Modern repository pattern
- Otomatik migration sistemi
- Relationship yönetimi
- Type safety ve validation

## 🏗️ Yeni Yapı

```
app/database/
├── __init__.py              # Package initialization
├── database.py              # SQLAlchemy configuration
├── db_connection.py         # Updated connection wrapper
├── migrations_v3.py         # New migration system
├── models/                  # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── grade.py
│   ├── subject.py
│   ├── unit.py
│   ├── topic.py
│   ├── question.py
│   ├── quiz.py
│   └── chat.py
└── repositories/            # Repository pattern
    ├── base_repository_v2.py
    └── user_repository_v2.py
```

## ⚙️ Kurulum

### 1. Gereksinimler

```bash
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=btk_app
MYSQL_PORT=3306
FLASK_ENV=development
```

### 3. Veritabanı Başlatma

```python
from app.database.database import init_db
from app.database.migrations_v3 import run_migrations

# Flask app ile
init_db(app)
run_migrations(app)
```

## 🎯 Kullanım

### Temel Model Kullanımı

```python
from app.database.models import User, Grade, Subject

# Kullanıcı oluşturma
user = User(
    username="john_doe",
    email="john@example.com",
    password_hash="hashed_password",
    first_name="John",
    last_name="Doe"
)

# Veritabanına kaydetme
db.session.add(user)
db.session.commit()
```

### Repository Pattern

```python
from app.database.repositories.user_repository_v2 import UserRepository

user_repo = UserRepository()

# Kullanıcı oluşturma
user = user_repo.create(
    username="jane_doe",
    email="jane@example.com",
    password_hash="hashed_password"
)

# Kullanıcı arama
user = user_repo.get_by_username("jane_doe")
users = user_repo.search_users("doe")
```

## 🌐 API Endpoints

### Ana Endpoints

- `GET /` - Ana sayfa
- `GET /migrate` - Veritabanı migration'ı çalıştır
- `GET /tables` - Tablo bilgilerini görüntüle
- `GET /users` - Tüm kullanıcıları listele
- `GET /create-user` - Örnek kullanıcı oluştur
- `GET /curriculum` - Müfredat yapısını görüntüle
- `GET /questions/<topic_id>` - Konuya göre soruları getir

### Migration Endpoint

```bash
curl http://localhost:5000/migrate
```

Response:
```json
{
  "status": "success",
  "message": "Database migration completed successfully!"
}
```

## 🗃️ Model Yapısı

### User Model

```python
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    # ... diğer alanlar
    
    # Relationships
    quiz_sessions = relationship('QuizSession', back_populates='user')
    chat_sessions = relationship('ChatSession', back_populates='user')
```

### Curriculum Models

```python
# Grade -> Subject -> Unit -> Topic -> Question hierarchy
Grade (Sınıf)
├── Subject (Ders)
│   ├── Unit (Ünite)
│   │   ├── Topic (Konu)
│   │   │   └── Question (Soru)
│   │   │       └── QuestionOption (Seçenek)
```

## 🔧 Repository Pattern

### Base Repository

```python
class BaseRepository(Generic[T]):
    def create(self, **kwargs) -> Optional[T]
    def get_by_id(self, id: int) -> Optional[T]
    def get_all(self, limit: Optional[int] = None) -> List[T]
    def update(self, id: int, **kwargs) -> Optional[T]
    def delete(self, id: int) -> bool
    def search(self, search_term: str, search_fields: List[str]) -> List[T]
    def get_paginated(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]
```

### User Repository

```python
class UserRepository(BaseRepository[User]):
    def get_by_username(self, username: str) -> Optional[User]
    def get_by_email(self, email: str) -> Optional[User]
    def get_active_users(self) -> List[User]
    def search_users(self, search_term: str) -> List[User]
    def update_user_profile(self, user_id: int, profile_data: Dict) -> Optional[User]
```

## 🚀 Migration Sistemi

### SQLAlchemyMigrationManager

```python
migrator = SQLAlchemyMigrationManager(app)

# Tüm tabloları oluştur
migrator.create_all_tables()

# Veri doldur
migrator.seed_initial_data()

# Tam migration
migrator.run_full_migration()
```

### Otomatik Seeding

- Grade verileri (8-12. sınıflar)
- Subject verileri (Türkçe, Matematik, vb.)
- Unit verileri (Fiilimsiler, Cümle Türleri, vb.)
- Topic verileri
- Örnek sorular

## 💡 Örnekler

### Kullanıcı Yönetimi

```python
# Kullanıcı oluşturma
user_repo = UserRepository()
new_user = user_repo.create(
    username="student1",
    email="student1@school.com",
    password_hash="hashed_password",
    first_name="Ahmet",
    last_name="Yılmaz"
)

# Kullanıcı arama
user = user_repo.get_by_username("student1")
active_users = user_repo.get_active_users()

# Profil güncelleme
user_repo.update_user_profile(user.user_id, {
    'first_name': 'Ahmet Mehmet',
    'city': 'İstanbul'
})
```

### Müfredat Sorguları

```python
# 8. sınıf Türkçe dersindeki konuları getir
grade_8 = db.session.query(Grade).filter_by(grade_number=8).first()
turkish = db.session.query(Subject).filter_by(
    grade_id=grade_8.grade_id,
    subject_name="Türkçe"
).first()

topics = db.session.query(Topic).join(Unit).filter(
    Unit.subject_id == turkish.subject_id
).all()
```

### Quiz Session Yönetimi

```python
# Quiz session oluşturma
quiz_session = QuizSession(
    user_id=user.user_id,
    session_name="Fiilimsiler Testi",
    quiz_mode="practice",
    total_questions=10
)

db.session.add(quiz_session)
db.session.commit()

# Soru ekleme
session_question = QuizSessionQuestion(
    session_id=quiz_session.session_id,
    question_id=question.question_id,
    question_order=1
)

db.session.add(session_question)
db.session.commit()
```

## 🔄 Geçiş Rehberi

### 1. Eski Kod Güncelleme

```python
# ESKİ (MySQL Connector)
with DatabaseConnection() as conn:
    cursor = conn.cursor
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

# YENİ (SQLAlchemy)
user = db.session.query(User).filter_by(username=username).first()
```

### 2. Repository Kullanımı

```python
# ESKİ
def get_user_by_id(user_id):
    with DatabaseConnection() as conn:
        cursor = conn.cursor
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

# YENİ
user_repo = UserRepository()
user = user_repo.get_by_id(user_id)
```

### 3. Relationship Kullanımı

```python
# ESKİ - Manuel JOIN
def get_user_quiz_sessions(user_id):
    with DatabaseConnection() as conn:
        cursor = conn.cursor
        cursor.execute("""
            SELECT qs.* FROM quiz_sessions qs
            JOIN users u ON qs.user_id = u.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        return cursor.fetchall()

# YENİ - SQLAlchemy Relationships
user = db.session.query(User).filter_by(user_id=user_id).first()
quiz_sessions = user.quiz_sessions
```

## 🧪 Test Etme

### 1. Uygulamayı Başlat

```bash
python main_sqlalchemy.py
```

### 2. Migration Çalıştır

```
http://localhost:5000/migrate
```

### 3. Tabloları Kontrol Et

```
http://localhost:5000/tables
```

### 4. Örnek Kullanıcı Oluştur

```
http://localhost:5000/create-user
```

## 🔍 Hata Ayıklama

### Yaygın Hatalar

1. **Import Hataları**: Model import'larını kontrol et
2. **Session Hataları**: `with app.app_context():` kullan
3. **Relationship Hataları**: Foreign key'leri doğru tanımla
4. **Migration Hataları**: Veritabanı bağlantısını kontrol et

### Debug Modu

```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'echo': True  # SQL sorgularını konsola yazdır
}
```

## 📚 Ek Kaynaklar

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html)

## 🎉 Sonuç

Bu migration ile:

✅ **Modern ORM**: SQLAlchemy ile type-safe veritabanı işlemleri  
✅ **Repository Pattern**: Temiz ve test edilebilir kod yapısı  
✅ **Relationship Management**: Otomatik JOIN ve foreign key yönetimi  
✅ **Migration System**: Otomatik tablo oluşturma ve veri doldurma  
✅ **Code Organization**: Daha iyi kod organizasyonu ve maintainability  
✅ **Performance**: Connection pooling ve query optimization  
✅ **Type Safety**: Python type hints ve validation  

Veritabanınız artık modern Python veritabanı standartlarına uygun ve çok daha maintainable!
