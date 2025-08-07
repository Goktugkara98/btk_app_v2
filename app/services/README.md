# 🔧 Services Modülü

Bu klasör, Daima Uygulaması'nın iş mantığı (business logic) servislerini modüler bir yapıda içerir. Veritabanı işlemleri ve karmaşık iş mantığı bu katmanda yer alır.

## 📁 Klasör Yapısı

```
app/services/
├── README.md                    # Bu dosya
├── __init__.py                  # Ana services modülü
├── services.py                  # Servis fabrikası
├── user_service.py              # Kullanıcı iş mantığı
├── quiz_service.py              # Quiz iş mantığı
└── system_service.py            # Sistem iş mantığı
```

## 🏗️ Mimari Yapı

### 🔄 Katman Mimarisi

```
Routes (Controllers)
    ↓
Services (Business Logic)
    ↓
Database (Data Access)
```

### 🏭 Service Factory Pattern

```
ServiceFactory
├── UserService
├── QuizService
└── SystemService
```

## 🔧 Servisler

### **services.py** - Servis Fabrikası
Tüm servislerin merkezi yönetim noktası.

**Özellikler:**
- Singleton pattern
- Lazy loading
- Dependency injection
- Error handling

**Kullanım:**
```python
from app.services import service_factory

# Servis al
user_service = service_factory.get_user_service()
quiz_service = service_factory.get_quiz_service()
```

### **user_service.py** - Kullanıcı Servisi
Kullanıcı ile ilgili tüm iş mantığı.

**Sınıf: UserService**

**Metodlar:**
- `register_user()` - Kullanıcı kaydı
- `authenticate_user()` - Kullanıcı doğrulama
- `get_user_profile()` - Profil bilgileri
- `update_user_profile()` - Profil güncelleme
- `delete_user_account()` - Hesap silme
- `change_password()` - Şifre değiştirme
- `reset_password()` - Şifre sıfırlama
- `get_user_statistics()` - Kullanıcı istatistikleri

**Özellikler:**
- Şifre hashleme (bcrypt)
- JWT token yönetimi
- Input validasyonu
- Email doğrulama
- Avatar yönetimi

**Örnek Kullanım:**
```python
from app.services import get_user_service

user_service = get_user_service()

# Kullanıcı kaydı
user = user_service.register_user(
    username="john_doe",
    email="john@example.com",
    password="secure_password"
)

# Kullanıcı doğrulama
token = user_service.authenticate_user(
    email="john@example.com",
    password="secure_password"
)
```

### **quiz_service.py** - Quiz Servisi
Quiz ile ilgili tüm iş mantığı.

**Sınıf: QuizService**

**Metodlar:**
- `get_available_topics()` - Mevcut konular
- `start_quiz()` - Quiz başlatma
- `get_questions()` - Soru listesi
- `submit_answer()` - Cevap gönderme
- `finish_quiz()` - Quiz bitirme
- `get_quiz_results()` - Quiz sonuçları
- `get_quiz_history()` - Quiz geçmişi
- `calculate_score()` - Puan hesaplama

**Özellikler:**
- Quiz durumu yönetimi
- Soru filtreleme
- Zamanlayıcı
- İlerleme takibi
- Sonuç analizi

**Örnek Kullanım:**
```python
from app.services import get_quiz_service

quiz_service = get_quiz_service()

# Quiz başlat
quiz_session = quiz_service.start_quiz(
    user_id=1,
    topic_id=5,
    question_count=10
)

# Soruları al
questions = quiz_service.get_questions(quiz_session.id)

# Cevap gönder
quiz_service.submit_answer(
    quiz_session_id=quiz_session.id,
    question_id=1,
    answer="A"
)

# Quiz bitir
results = quiz_service.finish_quiz(quiz_session.id)
```

### **system_service.py** - Sistem Servisi
Sistem durumu ve sağlık kontrolü.

**Sınıf: SystemService**

**Metodlar:**
- `get_system_health()` - Sistem sağlığı
- `get_system_status()` - Sistem durumu
- `get_performance_metrics()` - Performans metrikleri
- `get_error_logs()` - Hata logları
- `get_system_info()` - Sistem bilgileri
- `check_database_connection()` - Veritabanı bağlantısı
- `get_memory_usage()` - Bellek kullanımı
- `get_cpu_usage()` - CPU kullanımı

**Özellikler:**
- Sistem monitörü
- Performans izleme
- Hata raporlama
- Log yönetimi
- Metrik toplama

**Örnek Kullanım:**
```python
from app.services import get_system_service

system_service = get_system_service()

# Sistem sağlığını kontrol et
health = system_service.get_system_health()

# Performans metriklerini al
metrics = system_service.get_performance_metrics()

# Hata loglarını kontrol et
logs = system_service.get_error_logs()
```

## 🚀 Kullanım

### 1. Servis Fabrikası ile Erişim
```python
from app.services import service_factory

# Tüm servisleri al
services = service_factory.get_all_services()

# Belirli servisi al
user_service = service_factory.get_service('user')
```

### 2. Direkt Fonksiyon ile Erişim
```python
from app.services import get_user_service, get_quiz_service

user_service = get_user_service()
quiz_service = get_quiz_service()
```

### 3. Servis Sınıflarını Direkt Import
```python
from app.services import UserService, QuizService

user_service = UserService()
quiz_service = QuizService()
```

## 🔒 Güvenlik

### **Veri Doğrulama**
- Input sanitization
- SQL injection koruması
- XSS koruması
- CSRF koruması

### **Kimlik Doğrulama**
- JWT token validasyonu
- Session yönetimi
- Role-based access control

### **Şifreleme**
- Bcrypt hashleme
- Salt kullanımı
- Güvenli token üretimi

## 📊 Hata Yönetimi

### **Exception Handling**
```python
try:
    result = user_service.register_user(data)
except ValidationError as e:
    return {"error": "Validation failed", "details": e.message}
except DatabaseError as e:
    return {"error": "Database error", "details": str(e)}
except Exception as e:
    return {"error": "Internal server error"}
```

### **Logging**
```python
import logging

logger = logging.getLogger(__name__)

def some_method():
    try:
        # İşlem
        logger.info("İşlem başarılı")
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise
```

## 🧪 Test

### **Unit Test Örneği**
```python
import unittest
from app.services import get_user_service

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = get_user_service()
    
    def test_user_registration(self):
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "password123"
        }
        
        result = self.user_service.register_user(user_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "test_user")
```

### **Integration Test Örneği**
```python
def test_quiz_flow():
    quiz_service = get_quiz_service()
    user_service = get_user_service()
    
    # Kullanıcı oluştur
    user = user_service.register_user(user_data)
    
    # Quiz başlat
    quiz = quiz_service.start_quiz(user.id, topic_id=1)
    
    # Soruları al
    questions = quiz_service.get_questions(quiz.id)
    
    # Cevap ver
    quiz_service.submit_answer(quiz.id, questions[0].id, "A")
    
    # Quiz bitir
    results = quiz_service.finish_quiz(quiz.id)
    
    assert results.score > 0
```

## 📝 Örnekler

### **Kullanıcı Kayıt İşlemi**
```python
def register_user_workflow(user_data):
    user_service = get_user_service()
    
    # Veri doğrulama
    if not user_service.validate_user_data(user_data):
        raise ValidationError("Invalid user data")
    
    # Email kontrolü
    if user_service.email_exists(user_data['email']):
        raise ConflictError("Email already exists")
    
    # Kullanıcı oluştur
    user = user_service.register_user(user_data)
    
    # Hoş geldin emaili gönder
    user_service.send_welcome_email(user.email)
    
    return user
```

### **Quiz Tamamlama İşlemi**
```python
def complete_quiz_workflow(quiz_session_id, answers):
    quiz_service = get_quiz_service()
    user_service = get_user_service()
    
    # Quiz'i bitir
    results = quiz_service.finish_quiz(quiz_session_id, answers)
    
    # Puanı hesapla
    score = quiz_service.calculate_score(results)
    
    # Kullanıcı istatistiklerini güncelle
    user_service.update_quiz_statistics(results.user_id, score)
    
    # Başarı rozeti kontrolü
    badges = user_service.check_achievement_badges(results.user_id)
    
    return {
        "score": score,
        "results": results,
        "badges": badges
    }
```

## ⚠️ Önemli Notlar

1. **Service Layer**: Tüm iş mantığı servislerde olmalı
2. **Dependency Injection**: Servisler arası bağımlılıklar minimize edilmeli
3. **Error Handling**: Tüm metodlar exception handling içermeli
4. **Validation**: Input validasyonu zorunlu
5. **Logging**: Önemli işlemler loglanmalı

## 🐛 Sorun Giderme

### **Servis Başlatma Hatası**
```python
# Servis durumunu kontrol et
if service_factory.is_service_available('user'):
    print("UserService mevcut")
else:
    print("UserService başlatılamadı")
```

### **Import Hatası**
```python
# Servis import'unu kontrol et
try:
    from app.services import UserService
    print("UserService import başarılı")
except ImportError as e:
    print(f"Import hatası: {e}")
```

### **Veritabanı Bağlantı Hatası**
```python
# Veritabanı bağlantısını kontrol et
system_service = get_system_service()
db_status = system_service.check_database_connection()
print(f"DB Durumu: {db_status}")
```

## 📚 İlgili Dosyalar

- **app/routes/**: Route handlers
- **app/database/**: Veritabanı işlemleri
- **app/models/**: Veri modelleri
- **app/utils/**: Yardımcı fonksiyonlar

---

**Son Güncelleme**: 2025-01-27  
**Versiyon**: 2.0  
**Yazar**: Göktuğ KARA