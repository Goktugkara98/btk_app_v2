# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, ana sayfa rotalarını (endpoints) içerir.
# Ana sayfa, hakkımızda, iletişim gibi genel sayfaları yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. ANA SAYFA ROTALARI (MAIN PAGE ROUTES)
#   4.1. Ana Sayfalar
#     4.1.1. GET /
#     4.1.2. GET /about
#     4.1.3. GET /contact
#   4.2. Veri Dosyaları
#     4.2.1. GET /app/data/<filename>
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, render_template, send_from_directory
import os

# Create the main pages blueprint
main_bp = Blueprint('main', __name__)

# =============================================================================
# 4.0. ANA SAYFA ROTALARI (MAIN PAGE ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 4.1. Ana Sayfalar
# -------------------------------------------------------------------------

@main_bp.route('/')
def index():
    """4.1.1. Ana sayfayı render eder."""
    return render_template('index.html', title='Home')

@main_bp.route('/about')
def about():
    """4.1.2. Hakkımızda sayfasını render eder."""
    return render_template('about.html', title='About')

@main_bp.route('/contact')
def contact():
    """4.1.3. İletişim sayfasını render eder."""
    return render_template('contact.html', title='Contact')

# -------------------------------------------------------------------------
# 4.2. Veri Dosyaları
# -------------------------------------------------------------------------

@main_bp.route('/app/data/<filename>')
def serve_data(filename):
    """4.2.1. app/data dizininden veri dosyalarını sunar."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    return send_from_directory(data_dir, filename) 