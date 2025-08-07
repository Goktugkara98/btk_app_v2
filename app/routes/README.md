# 🛣️ Routes Modülü

Bu klasör, Daima Uygulaması'nın Flask rotalarını (endpoints) modüler bir yapıda içerir. API ve sayfa rotaları ayrı ayrı organize edilmiştir.

## 📁 Klasör Yapısı

```
app/routes/
├── README.md                    # Bu dosya
├── __init__.py                  # Ana routes modülü
├── api/                         # API rotaları
│   ├── __init__.py             # API modülü başlatıcı
│   ├── api_routes.py           # Ana API blueprint
│   ├── user_routes.py          # Kullanıcı API rotaları
│   ├── system_routes.py        # Sistem API rotaları
│   └── quiz_routes.py          # Quiz API rotaları
└── pages/                       # Sayfa rotaları
    ├── __init__.py             # Pages modülü başlatıcı
    ├── routes.py               # Ana sayfa blueprint
    ├── main_routes.py          # Ana sayfa rotaları
    ├── auth_routes.py          # Kimlik doğrulama rotaları
    ├── quiz_routes.py          # Quiz sayfa rotaları
    └── user_routes.py          # Kullanıcı sayfa rotaları
```

## 🏗️ Mimari Yapı

### 🔗 Blueprint Hiyerarşisi

```
Flask App
├── api_bp (Blueprint: 'api')
│   ├── user_bp (Blueprint: 'users')
│   ├── system_bp (Blueprint: 'system')
│   └── quiz_bp (Blueprint: 'quiz')
└── pages_bp (Blueprint: 'pages')
    ├── main_bp (Blueprint: 'main')
    ├── auth_bp (Blueprint: 'auth')
    ├── quiz_bp (Blueprint: 'quiz')
    └── user_bp (Blueprint: 'user')
```

### 📍 URL Yapısı

#### **API Rotaları** (`/api/*`)
- `/api/users/*` - Kullanıcı işlemleri
- `/api/system/*` - Sistem durumu
- `/api/quiz/*` - Quiz işlemleri

#### **Sayfa Rotaları** (`/*`)
- `/` - Ana sayfa
- `/login`, `/register` - Kimlik doğrulama
- `/quiz/*` - Quiz sayfaları
- `/profile` - Kullanıcı profili

## 🔧 API Rotaları

### **api_routes.py** - Ana API Blueprint
API modüllerini birleştiren ana blueprint.

**Özellikler:**
- Modüler yapı
- Hata yönetimi
- Blueprint kayıt sistemi

### **user_routes.py** - Kullanıcı API Rotaları
Kullanıcı ile ilgili API endpoint'leri.

**Endpoint'ler:**
- `POST /api/register` - Kullanıcı kaydı
- `POST /api/login` - Kullanıcı girişi
- `GET /api/users/profile` - Profil bilgileri
- `PUT /api/users/profile` - Profil güncelleme
- `DELETE /api/users/account` - Hesap silme

**Özellikler:**
- JWT token yönetimi
- Şifre hashleme
- Input validasyonu
- Hata yönetimi

### **system_routes.py** - Sistem API Rotaları
Sistem durumu ve sağlık kontrolü endpoint'leri.

**Endpoint'ler:**
- `GET /api/health` - Sistem sağlığı
- `GET /api/status` - Sistem durumu
- `GET /api/version` - Uygulama versiyonu
- `GET /api/info` - Sistem bilgileri

**Özellikler:**
- Sistem metrikleri
- Performans izleme
- Hata raporlama

### **quiz_routes.py** - Quiz API Rotaları
Quiz ile ilgili API endpoint'leri.

**Endpoint'ler:**
- `GET /api/quiz/topics` - Konu listesi
- `POST /api/quiz/start` - Quiz başlatma
- `GET /api/quiz/questions` - Soru listesi
- `POST /api/quiz/submit` - Quiz gönderme
- `GET /api/quiz/results` - Sonuçlar

**Özellikler:**
- Quiz durumu yönetimi
- Soru filtreleme
- Sonuç hesaplama
- İlerleme takibi

## 🌐 Sayfa Rotaları

### **routes.py** - Ana Sayfa Blueprint
Sayfa modüllerini birleştiren ana blueprint.

**Özellikler:**
- Template rendering
- Session yönetimi
- Hata sayfaları

### **main_routes.py** - Ana Sayfa Rotaları
Ana sayfa ve genel sayfa rotaları.

**Rotalar:**
- `GET /` - Ana sayfa
- `GET /about` - Hakkında sayfası
- `GET /contact` - İletişim sayfası
- `GET /help` - Yardım sayfası

**Özellikler:**
- Responsive tasarım
- SEO optimizasyonu
- İçerik yönetimi

### **auth_routes.py** - Kimlik Doğrulama Rotaları
Giriş, kayıt ve oturum yönetimi.

**Rotalar:**
- `GET /login` - Giriş sayfası
- `POST /login` - Giriş işlemi
- `GET /register` - Kayıt sayfası
- `POST /register` - Kayıt işlemi
- `GET /logout` - Çıkış işlemi

**Özellikler:**
- Form validasyonu
- CSRF koruması
- Session yönetimi
- Hata mesajları

### **quiz_routes.py** - Quiz Sayfa Rotaları
Quiz ile ilgili sayfa rotaları.

**Rotalar:**
- `GET /quiz` - Quiz ana sayfası
- `GET /quiz/start` - Quiz başlatma sayfası
- `GET /quiz/questions` - Soru sayfası
- `GET /quiz/results` - Sonuç sayfası
- `GET /quiz/history` - Quiz geçmişi

**Özellikler:**
- Dinamik içerik
- JavaScript entegrasyonu
- İlerleme göstergesi
- Zamanlayıcı

### **user_routes.py** - Kullanıcı Sayfa Rotaları
Kullanıcı profili ve ayarlar.

**Rotalar:**
- `GET /profile` - Profil sayfası
- `GET /profile/edit` - Profil düzenleme
- `GET /profile/settings` - Ayarlar sayfası
- `GET /profile/history` - Kullanıcı geçmişi

**Özellikler:**
- Profil yönetimi
- Avatar yükleme
- Ayarlar paneli
- İstatistikler

## 🚀 Kullanım

### 1. Blueprint Kayıt
```python
from app.routes import api_bp, pages_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(pages_bp)
```

### 2. Modül Import
```python
# API rotaları
from app.routes.api import user_bp, system_bp, quiz_bp

# Sayfa rotaları
from app.routes.pages import main_bp, auth_bp, quiz_bp, user_bp
```

### 3. Route Tanımlama
```python
from flask import Blueprint

# Blueprint oluştur
user_bp = Blueprint('users', __name__)

# Route tanımla
@user_bp.route('/profile', methods=['GET'])
def get_profile():
    return {'message': 'Profile data'}
```

## 🔒 Güvenlik

### **Kimlik Doğrulama**
- JWT token tabanlı
- Session yönetimi
- CSRF koruması

### **Yetkilendirme**
- Role-based access control
- Endpoint koruması
- Admin paneli

### **Input Validasyonu**
- Form validasyonu
- SQL injection koruması
- XSS koruması

## 📊 Hata Yönetimi

### **HTTP Status Kodları**
- `200` - Başarılı
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

### **Hata Formatı**
```json
{
  "error": "Hata mesajı",
  "code": "ERROR_CODE",
  "details": "Detaylı açıklama"
}
```

## 🧪 Test

### **Unit Test**
```python
def test_user_registration():
    response = client.post('/api/register', json={
        'username': 'test',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
```

### **Integration Test**
```python
def test_quiz_flow():
    # Quiz başlat
    response = client.post('/api/quiz/start')
    assert response.status_code == 200
    
    # Soruları al
    response = client.get('/api/quiz/questions')
    assert response.status_code == 200
```

## 📝 Örnekler

### **API Response Örneği**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "message": "User created successfully"
}
```

### **Template Rendering**
```python
@main_bp.route('/')
def index():
    return render_template('index.html', 
                         title='Ana Sayfa',
                         user=current_user)
```

## ⚠️ Önemli Notlar

1. **Blueprint Kullanımı**: Tüm rotalar blueprint'ler içinde tanımlanmalı
2. **URL Prefix**: API rotaları `/api` prefix'i kullanır
3. **Error Handling**: Tüm rotalar hata yönetimi içermeli
4. **Validation**: Input validasyonu zorunlu
5. **Documentation**: Her endpoint dokümante edilmeli

## 🐛 Sorun Giderme

### **Blueprint Kayıt Hatası**
```python
# Blueprint'i kontrol et
print(app.blueprints)

# URL kurallarını kontrol et
print(app.url_map)
```

### **Route Bulunamadı**
```python
# Blueprint'in kayıtlı olduğunu kontrol et
if 'api' in app.blueprints:
    print("API blueprint kayıtlı")
```

### **Import Hatası**
```python
# Modül yolunu kontrol et
import sys
sys.path.append('/path/to/app')
```

## 📚 İlgili Dosyalar

- **main.py**: Flask uygulaması ve blueprint kayıt
- **app/services/**: İş mantığı servisleri
- **app/templates/**: HTML template'leri
- **app/static/**: CSS, JS, resim dosyaları

---

**Son Güncelleme**: 2025-01-27  
**Versiyon**: 2.0  
**Yazar**: Göktuğ KARA 