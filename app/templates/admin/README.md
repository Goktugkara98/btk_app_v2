# Admin Panel - BTK App

## Genel Bakış

BTK App için modern, responsive ve kullanıcı dostu admin paneli. Bu panel, müfredat yönetimi, kullanıcı yönetimi ve sistem yönetimi işlemlerini kolaylaştırır.

## Özellikler

### 🎨 Modern Tasarım
- **Responsive Layout**: Tüm cihazlarda mükemmel görünüm
- **Dark Mode Support**: Sistem tercihine göre otomatik tema
- **Modern UI/UX**: Material Design prensipleri
- **Smooth Animations**: CSS3 animasyonları ve geçişler

### 🚀 Gelişmiş Fonksiyonlar
- **Dashboard**: Gerçek zamanlı istatistikler ve grafikler
- **Müfredat Yönetimi**: Sınıf, ders, ünite ve konu yönetimi
- **Kullanıcı Yönetimi**: Kullanıcı ekleme, düzenleme, silme
- **Veri Aktarımı**: JSON import/export işlemleri
- **Sistem Monitörü**: Sunucu sağlık durumu ve performans

### 🔒 Güvenlik
- **Admin Yetkilendirme**: Rol tabanlı erişim kontrolü
- **Session Yönetimi**: Güvenli oturum yönetimi
- **Logging**: Tüm admin işlemlerinin detaylı loglanması
- **Auto Logout**: 30 dakika hareketsizlik sonrası otomatik çıkış

### ⌨️ Klavye Kısayolları
- `Ctrl + K`: Sidebar aç/kapat
- `Ctrl + H`: Ana sayfaya git
- `Ctrl + N`: Yeni öğe oluştur
- `Ctrl + S`: Kaydet

## Kurulum

### Gereksinimler
- Python 3.8+
- Flask 2.0+
- Bootstrap 5.3+
- Font Awesome 6.4+

### Adımlar
1. **Dosyaları kopyala**: Admin template'lerini `app/templates/admin/` klasörüne kopyala
2. **CSS dosyalarını ekle**: `app/static/css/admin/` klasörüne CSS dosyalarını ekle
3. **JavaScript dosyalarını ekle**: `app/static/js/admin/` klasörüne JS dosyalarını ekle
4. **Routes'ları ekle**: Admin routes'larını `app/routes/` klasörüne ekle
5. **Services'leri ekle**: Admin service'lerini `app/services/` klasörüne ekle

## Dosya Yapısı

```
app/
├── templates/
│   └── admin/
│       ├── base_admin.html          # Ana admin template
│       ├── dashboard.html           # Dashboard sayfası
│       ├── grades.html             # Sınıf yönetimi
│       ├── subjects.html           # Ders yönetimi
│       ├── units.html              # Ünite yönetimi
│       ├── topics.html             # Konu yönetimi
│       ├── import_export.html      # Veri aktarımı
│       ├── users.html              # Kullanıcı yönetimi
│       ├── system.html             # Sistem yönetimi
│       ├── reports.html            # Raporlar
│       ├── settings.html           # Ayarlar
│       └── errors/                 # Hata sayfaları
│           ├── 404.html
│           ├── 403.html
│           └── 500.html
├── static/
│   ├── css/
│   │   └── admin/
│   │       └── admin.css           # Admin CSS stilleri
│   └── js/
│       └── admin/
│           ├── admin-base.js       # Ana admin JavaScript
│           ├── dashboard.js        # Dashboard JavaScript
│           ├── curriculum.js       # Müfredat JavaScript
│           └── users.js            # Kullanıcı JavaScript
├── routes/
│   ├── pages/
│   │   └── admin_routes.py        # Admin sayfa routes'ları
│   └── api/
│       └── admin_routes.py        # Admin API routes'ları
└── services/
    └── admin_service.py            # Admin iş mantığı
```

## Kullanım

### Dashboard
- Sistem genel durumu ve istatistikler
- Gerçek zamanlı grafikler ve veriler
- Hızlı işlem butonları
- Son aktiviteler listesi

### Müfredat Yönetimi
- **Sınıflar**: Sınıf ekleme, düzenleme, silme
- **Dersler**: Ders ekleme, sınıfa atama
- **Üniteler**: Ünite ekleme, derse atama
- **Konular**: Konu ekleme, üniteye atama

### Kullanıcı Yönetimi
- Kullanıcı listesi ve arama
- Kullanıcı durumu güncelleme
- Toplu işlemler
- Kullanıcı istatistikleri

### Veri Aktarımı
- JSON dosyasından veri yükleme
- Veritabanından JSON export
- Veri doğrulama ve hata kontrolü
- Toplu veri işlemleri

## API Endpoints

### Dashboard
- `GET /admin/dashboard` - Dashboard istatistikleri
- `GET /admin/dashboard/activity` - Aktivite grafiği verileri

### Müfredat
- `GET /admin/grades` - Sınıf listesi
- `POST /admin/grades` - Yeni sınıf oluştur
- `PUT /admin/grades/{id}` - Sınıf güncelle
- `DELETE /admin/grades/{id}` - Sınıf sil

### Kullanıcılar
- `GET /admin/users` - Kullanıcı listesi
- `PUT /admin/users/{id}/status` - Kullanıcı durumu güncelle
- `DELETE /admin/users/{id}` - Kullanıcı sil

### Sistem
- `GET /admin/system/health` - Sistem sağlık durumu
- `POST /admin/system/report` - Sistem raporu oluştur

## Özelleştirme

### CSS Değişkenleri
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --bg-primary: #ffffff;
    --bg-sidebar: #1e293b;
    --sidebar-width: 280px;
}
```

### JavaScript Konfigürasyonu
```javascript
// Admin panel konfigürasyonu
window.adminConfig = {
    autoLogout: 30 * 60 * 1000, // 30 dakika
    refreshInterval: 5 * 60 * 1000, // 5 dakika
    enableNotifications: true,
    enableSounds: true
};
```

### Template Özelleştirme
```html
{% extends "admin/base_admin.html" %}

{% block page_title %}Özel Sayfa{% endblock %}
{% block page_subtitle %}Sayfa açıklaması{% endblock %}

{% block content %}
<!-- Sayfa içeriği -->
{% endblock %}
```

## Güvenlik

### Yetkilendirme
- Admin decorator ile sayfa koruması
- Session tabanlı kimlik doğrulama
- Rol tabanlı erişim kontrolü

### Logging
- Tüm admin işlemleri loglanır
- IP adresi ve user agent kaydedilir
- Hata durumları detaylı loglanır

### Session Güvenliği
- Otomatik oturum sonlandırma
- Güvenli session yönetimi
- CSRF koruması

## Performans

### Optimizasyonlar
- CSS ve JavaScript minification
- Image optimization
- Lazy loading
- Caching strategies

### Monitoring
- Sayfa yükleme süreleri
- API response times
- Error rates
- User activity tracking

## Hata Yönetimi

### Hata Sayfaları
- 404: Sayfa bulunamadı
- 403: Erişim reddedildi
- 500: Sunucu hatası

### Hata Logging
- Detaylı hata mesajları
- Stack trace logging
- User context bilgileri

## Test

### Unit Tests
```bash
python -m pytest tests/test_admin.py
```

### Integration Tests
```bash
python -m pytest tests/test_admin_integration.py
```

### Browser Tests
```bash
python -m pytest tests/test_admin_browser.py
```

## Deployment

### Production
- Debug mode kapalı
- Logging seviyesi INFO
- HTTPS zorunlu
- Rate limiting aktif

### Environment Variables
```bash
ADMIN_DEBUG=false
ADMIN_LOG_LEVEL=INFO
ADMIN_SESSION_TIMEOUT=1800
ADMIN_MAX_LOGIN_ATTEMPTS=5
```

## Destek

### Dokümantasyon
- API dokümantasyonu
- Kullanıcı kılavuzu
- Geliştirici dokümantasyonu

### İletişim
- GitHub Issues
- Email support
- Live chat (opsiyonel)

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Changelog

### v2.0.0 (2024-01-XX)
- Modern tasarım ve UI/UX iyileştirmeleri
- Responsive layout desteği
- Gelişmiş JavaScript fonksiyonları
- Yeni admin service yapısı
- Kapsamlı logging ve monitoring

### v1.0.0 (2023-XX-XX)
- İlk sürüm
- Temel admin paneli
- Müfredat yönetimi
- Kullanıcı yönetimi

## Roadmap

### v2.1.0 (Gelecek)
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Mobile app integration

### v2.2.0 (Gelecek)
- [ ] AI-powered insights
- [ ] Advanced reporting
- [ ] Workflow automation
- [ ] API rate limiting

---

**Not**: Bu admin paneli sürekli geliştirilmektedir. Güncel bilgiler için GitHub repository'yi takip edin.
