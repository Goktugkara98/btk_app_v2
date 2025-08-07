# 📊 Veritabanı Modülü

Bu klasör, Daima Uygulaması'nın veritabanı yönetimi ve veri işleme işlevlerini içerir.

## 📁 Klasör Yapısı

```
app/database/
├── README.md                    # Bu dosya
├── db_connection.py             # Veritabanı bağlantı yönetimi
├── db_migrations.py             # Veritabanı migration sistemi
├── curriculum_data_loader.py    # Müfredat verilerini yükleme
├── quiz_data_loader.py          # Quiz verilerini yükleme
├── quiz_data_cli.py             # Quiz veri yükleme CLI scripti
├── user_repository.py           # Kullanıcı veri erişimi
└── schemas/                     # Veritabanı tablo şemaları
    ├── __init__.py
    ├── grades_schema.py         # Sınıflar tablosu
    ├── subjects_schema.py       # Dersler tablosu
    ├── units_schema.py          # Üniteler tablosu
    ├── topics_schema.py         # Konular tablosu
    ├── questions_schema.py      # Sorular tablosu
    ├── question_options_schema.py # Şıklar tablosu
    └── users_schema.py          # Kullanıcılar tablosu
```

## 🗄️ Veritabanı Yapısı

### 📋 Standart Tablo Yapısı

Her tabloda tutarlı bir sütun düzeni kullanılır:

1. **id** (Primary Key)
2. **[parent_id]** (Üst sınıf ID'si)
3. **name** (Türkçe isim - geliştirici ve frontend için)
4. **name_id** (İngilizce kod - veri işlemleri için)
5. **description** (Açıklama)
6. **[extra sütunlar]** (Tabloya özel sütunlar)
7. **is_active** (Aktiflik durumu)
8. **created_at** (Oluşturma tarihi)
9. **updated_at** (Güncelleme tarihi)

### 📊 Tablo Detayları

#### **GRADES (Sınıflar)**
```sql
id, name, name_id, level, description, is_active, created_at, updated_at
```
- **Amaç**: Sınıf seviyelerini (8, 9, 10, 11, 12) tanımlar
- **Örnek**: "8. Sınıf", "grade_8", 8

#### **SUBJECTS (Dersler)**
```sql
id, grade_id, name, name_id, description, is_active, created_at, updated_at
```
- **Amaç**: Her sınıf seviyesindeki dersleri tanımlar
- **Örnek**: "Türkçe", "turkish", "Türkçe dersi"

#### **UNITS (Üniteler)**
```sql
id, subject_id, name, name_id, description, is_active, created_at, updated_at
```
- **Amaç**: Her dersin ünitelerini tanımlar
- **Örnek**: "Fiilimsiler", "verbals", "Fiilimsiler ünitesi"

#### **TOPICS (Konular)**
```sql
id, unit_id, name, name_id, description, is_active, created_at, updated_at
```
- **Amaç**: Her ünitenin konularını tanımlar
- **Örnek**: "Sıfat-fiil", "participle", "Fiilimsiler - Sıfat-fiil"

#### **QUESTIONS (Sorular)**
```sql
id, topic_id, name, name_id, difficulty_level, question_type, points, description, is_active, created_at, updated_at
```
- **Amaç**: Konulara ait soruları saklar
- **Özel Alanlar**:
  - `difficulty_level`: 'easy', 'medium', 'hard'
  - `question_type`: 'multiple_choice', 'true_false', 'fill_blank', 'essay'
  - `points`: Soru puanı
  - `description`: Soru açıklaması

#### **QUESTION_OPTIONS (Şıklar)**
```sql
id, question_id, name, name_id, is_correct, option_order, description, is_active, created_at, updated_at
```
- **Amaç**: Soruların şıklarını saklar
- **Özel Alanlar**:
  - `is_correct`: Doğru şık mı?
  - `option_order`: Şık sırası (A=1, B=2, C=3, D=4)
  - `description`: Şık açıklaması

#### **USERS (Kullanıcılar)**
```sql
id, grade_level_id, name, name_id, email, password_hash, first_name, last_name, phone, birth_date, gender, school, bio, avatar_path, is_active, is_admin, created_at, updated_at
```
- **Amaç**: Sistem kullanıcılarını saklar
- **Özel Alanlar**:
  - `password_hash`: Şifrelenmiş parola
  - `is_admin`: Yönetici yetkisi
  - `avatar_path`: Profil resmi yolu

## 🔧 Modüller

### **db_connection.py**
Veritabanı bağlantı yönetimi için wrapper sınıf.

**Özellikler:**
- Otomatik bağlantı yenileme
- Context manager desteği (`with` bloğu)
- Hata yönetimi ve loglama
- Transaction yönetimi

**Kullanım:**
```python
from app.database.db_connection import DatabaseConnection

db = DatabaseConnection()
with db as conn:
    conn.cursor.execute("SELECT * FROM users")
    users = conn.cursor.fetchall()
```

### **db_migrations.py**
Veritabanı tablolarını oluşturan ve yöneten sistem.

**Özellikler:**
- Otomatik tablo oluşturma
- JSON verilerini yükleme
- Tablo varlık kontrolü
- Migration geçmişi

**Kullanım:**
```python
from app.database.db_migrations import DatabaseMigrations

migrations = DatabaseMigrations(db_connection)
migrations.run_migrations()  # Tabloları oluştur
```

### **quiz_data_loader.py**
JSON dosyalarından quiz verilerini veritabanına yükler.

**Özellikler:**
- JSON dosya okuma
- Metadata kontrolü
- Topic ID eşleştirme
- Soru ve şık açıklamalarını kaydetme

**Kullanım:**
```python
from app.database.quiz_data_loader import QuestionLoader

loader = QuestionLoader()
results = loader.process_all_question_files()
```

### **curriculum_data_loader.py**
Grade, subject, unit, topic verilerini JSON'dan yükler.

**Özellikler:**
- Grade dosyalarını okuma
- Hiyerarşik veri çıkarma
- SQL insert ifadeleri oluşturma
- ID eşleştirme

### **quiz_data_cli.py**
Quiz veri yükleme için CLI scripti.

**Kullanım:**
```bash
# Tüm quiz dosyalarını yükle
python app/database/quiz_data_cli.py

# Belirli bir dosyayı yükle
python app/database/quiz_data_cli.py --file path/to/file.json

# Belirli bir dizindeki dosyaları yükle
python app/database/quiz_data_cli.py --dir path/to/directory
```

### **user_repository.py**
Kullanıcı verilerine erişim için repository pattern.

**Özellikler:**
- CRUD işlemleri
- Kullanıcı doğrulama
- Şifre hashleme
- Arama ve filtreleme

## 📝 Şema Dosyaları

Her tablo için ayrı şema dosyası bulunur:

- **grades_schema.py**: Sınıflar tablosu tanımı
- **subjects_schema.py**: Dersler tablosu tanımı
- **units_schema.py**: Üniteler tablosu tanımı
- **topics_schema.py**: Konular tablosu tanımı
- **questions_schema.py**: Sorular tablosu tanımı
- **question_options_schema.py**: Şıklar tablosu tanımı
- **users_schema.py**: Kullanıcılar tablosu tanımı

Her şema dosyası şunları içerir:
- `CREATE TABLE` SQL ifadesi
- İndeksler ve foreign key'ler
- Örnek veriler (opsiyonel)

## 🚀 Kurulum ve Kullanım

### 1. Veritabanı Bağlantısı
```python
from app.database.db_connection import DatabaseConnection

db = DatabaseConnection()
```

### 2. Tabloları Oluştur
```python
from app.database.db_migrations import DatabaseMigrations

migrations = DatabaseMigrations(db)
migrations.run_migrations()
```

### 3. Quiz Verilerini Yükle
```python
from app.database.quiz_data_loader import QuestionLoader

loader = QuestionLoader()
results = loader.process_all_question_files()
```

### 4. CLI ile Yükleme
```bash
python app/database/quiz_data_cli.py
```

## 🔍 Veri Kontrolü

### Tablo Sayılarını Kontrol Et
```python
from app.database.db_connection import DatabaseConnection

db = DatabaseConnection()
with db as conn:
    conn.cursor.execute("SELECT COUNT(*) as count FROM questions")
    result = conn.cursor.fetchone()
    print(f"Toplam soru sayısı: {result['count']}")
```

### Soru Detaylarını Kontrol Et
```python
with db as conn:
    conn.cursor.execute("""
        SELECT q.name, q.description, t.name as topic_name
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        LIMIT 5
    """)
    questions = conn.cursor.fetchall()
    for q in questions:
        print(f"Soru: {q['name']}")
        print(f"Açıklama: {q['description']}")
        print(f"Konu: {q['topic_name']}")
```

## ⚠️ Önemli Notlar

1. **Bağlantı Yönetimi**: Her zaman `with` bloğu kullanın
2. **Transaction**: Otomatik commit/rollback yapılır
3. **Hata Yönetimi**: Tüm modüller exception handling içerir
4. **Veri Bütünlüğü**: Foreign key constraint'ler aktif
5. **Performans**: İndeksler optimize edilmiş

## 🐛 Sorun Giderme

### Bağlantı Hatası
```python
# Bağlantıyı yeniden kur
db = DatabaseConnection()
db._ensure_connection()
```

### Tablo Bulunamadı
```python
# Migration'ları çalıştır
migrations = DatabaseMigrations(db)
migrations.force_recreate()
```

### Question Yükleme Hatası
```bash
# Verbose mod ile çalıştır
python app/database/load_questions.py --verbose
```

## 📚 İlgili Dosyalar

- **main.py**: Uygulama başlatma ve veritabanı init
- **config.py**: Veritabanı konfigürasyonu
- **app/data/quiz_banks/**: Quiz JSON dosyaları
- **app/data/curriculum_structure/**: Müfredat JSON dosyaları

---

**Son Güncelleme**: 2025-01-27  
**Versiyon**: 2.0  
**Yazar**: Göktuğ KARA