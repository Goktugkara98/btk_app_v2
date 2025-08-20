"""
Validation Utilities - Data Validation Helpers
Provides validation functions for API input data
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Gerekli alanların varlığını kontrol eder
    
    Args:
        data: Kontrol edilecek veri
        required_fields: Gerekli alan listesi
    
    Returns:
        bool: Tüm gerekli alanlar mevcutsa True
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False
    
    return True

def validate_email(email: str) -> bool:
    """
    Email formatını kontrol eder
    
    Args:
        email: Kontrol edilecek email
    
    Returns:
        bool: Geçerli email formatı ise True
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basit email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    """
    Kullanıcı adı formatını kontrol eder
    
    Args:
        username: Kontrol edilecek kullanıcı adı
    
    Returns:
        bool: Geçerli kullanıcı adı formatı ise True
    """
    if not username or not isinstance(username, str):
        return False
    
    # Kullanıcı adı: 3-20 karakter, sadece harf, rakam, alt çizgi
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> bool:
    """
    Şifre güvenliğini kontrol eder
    
    Args:
        password: Kontrol edilecek şifre
    
    Returns:
        bool: Güvenli şifre ise True
    """
    if not password or not isinstance(password, str):
        return False
    
    # En az 8 karakter, en az 1 büyük harf, 1 küçük harf, 1 rakam
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit

def validate_string_length(value: str, min_length: int = 1, max_length: int = 255) -> bool:
    """
    String uzunluğunu kontrol eder
    
    Args:
        value: Kontrol edilecek string
        min_length: Minimum uzunluk
        max_length: Maksimum uzunluk
    
    Returns:
        bool: Uzunluk uygunsa True
    """
    if not isinstance(value, str):
        return False
    
    return min_length <= len(value) <= max_length

def validate_integer_range(value: Any, min_value: int = None, max_value: int = None) -> bool:
    """
    Integer değer aralığını kontrol eder
    
    Args:
        value: Kontrol edilecek değer
        min_value: Minimum değer (opsiyonel)
        max_value: Maksimum değer (opsiyonel)
    
    Returns:
        bool: Değer aralıkta ise True
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return False
    
    if min_value is not None and int_value < min_value:
        return False
    
    if max_value is not None and int_value > max_value:
        return False
    
    return True

def validate_positive_integer(value: Any) -> bool:
    """
    Pozitif integer değerini kontrol eder
    
    Args:
        value: Kontrol edilecek değer
    
    Returns:
        bool: Pozitif integer ise True
    """
    return validate_integer_range(value, min_value=1)

def validate_boolean(value: Any) -> bool:
    """
    Boolean değerini kontrol eder
    
    Args:
        value: Kontrol edilecek değer
    
    Returns:
        bool: Boolean değer ise True
    """
    if isinstance(value, bool):
        return True
    
    if isinstance(value, str):
        return value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
    
    if isinstance(value, int):
        return value in [0, 1]
    
    return False

def validate_date_format(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """
    Tarih formatını kontrol eder
    
    Args:
        date_string: Kontrol edilecek tarih string'i
        format: Beklenen tarih formatı
    
    Returns:
        bool: Geçerli tarih formatı ise True
    """
    if not isinstance(date_string, str):
        return False
    
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def validate_phone_number(phone: str) -> bool:
    """
    Telefon numarası formatını kontrol eder
    
    Args:
        phone: Kontrol edilecek telefon numarası
    
    Returns:
        bool: Geçerli telefon formatı ise True
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Türkiye telefon numarası formatı: +90 5XX XXX XX XX
    # Sadece rakamları al
    digits_only = re.sub(r'\D', '', phone)
    
    # Türkiye telefon numarası 10-11 haneli olmalı
    if len(digits_only) not in [10, 11]:
        return False
    
    # 5 ile başlamalı (mobil)
    if len(digits_only) == 11 and digits_only[0] == '0':
        digits_only = digits_only[1:]
    
    if not digits_only.startswith('5'):
        return False
    
    return True

def validate_curriculum_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Müfredat verilerini validate eder
    
    Args:
        data: Kontrol edilecek müfredat verisi
    
    Returns:
        Dict: Hata mesajları (field_name: [error_messages])
    """
    errors = {}
    
    # Grade validation
    if 'grade_name' in data:
        if not validate_string_length(data['grade_name'], min_length=2, max_length=50):
            errors.setdefault('grade_name', []).append('Sınıf adı 2-50 karakter arasında olmalı')
    
    if 'grade_level' in data:
        if not validate_integer_range(data['grade_level'], min_value=1, max_value=12):
            errors.setdefault('grade_level', []).append('Sınıf seviyesi 1-12 arasında olmalı')
    
    # Subject validation
    if 'subject_name' in data:
        if not validate_string_length(data['subject_name'], min_length=2, max_length=100):
            errors.setdefault('subject_name', []).append('Ders adı 2-100 karakter arasında olmalı')
    
    if 'grade_id' in data:
        if not validate_positive_integer(data['grade_id']):
            errors.setdefault('grade_id', []).append('Geçersiz sınıf ID')
    
    # Unit validation
    if 'unit_name' in data:
        if not validate_string_length(data['unit_name'], min_length=2, max_length=100):
            errors.setdefault('unit_name', []).append('Ünite adı 2-100 karakter arasında olmalı')
    
    if 'unit_number' in data:
        if not validate_positive_integer(data['unit_number']):
            errors.setdefault('unit_number', []).append('Geçersiz ünite numarası')
    
    if 'subject_id' in data:
        if not validate_positive_integer(data['subject_id']):
            errors.setdefault('subject_id', []).append('Geçersiz ders ID')
    
    # Topic validation
    if 'topic_name' in data:
        if not validate_string_length(data['topic_name'], min_length=2, max_length=100):
            errors.setdefault('topic_name', []).append('Konu adı 2-100 karakter arasında olmalı')
    
    if 'topic_number' in data:
        if not validate_positive_integer(data['topic_number']):
            errors.setdefault('topic_number', []).append('Geçersiz konu numarası')
    
    if 'unit_id' in data:
        if not validate_positive_integer(data['unit_id']):
            errors.setdefault('unit_id', []).append('Geçersiz ünite ID')
    
    return errors

def sanitize_string(value: str) -> str:
    """
    String'i temizler ve güvenli hale getirir
    
    Args:
        value: Temizlenecek string
    
    Returns:
        str: Temizlenmiş string
    """
    if not isinstance(value, str):
        return str(value)
    
    # HTML tag'lerini kaldır
    value = re.sub(r'<[^>]+>', '', value)
    
    # Fazla boşlukları temizle
    value = re.sub(r'\s+', ' ', value)
    
    # Başındaki ve sonundaki boşlukları kaldır
    value = value.strip()
    
    return value

def validate_file_upload(file, allowed_extensions: List[str] = None, max_size_mb: int = 10) -> Dict[str, Any]:
    """
    Dosya upload'ını validate eder
    
    Args:
        file: Upload edilen dosya
        allowed_extensions: İzin verilen dosya uzantıları
        max_size_mb: Maksimum dosya boyutu (MB)
    
    Returns:
        Dict: Validation sonucu
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if not file:
        result['valid'] = False
        result['errors'].append('Dosya bulunamadı')
        return result
    
    if file.filename == '':
        result['valid'] = False
        result['errors'].append('Dosya seçilmedi')
        return result
    
    # File extension validation
    if allowed_extensions:
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            result['valid'] = False
            result['errors'].append(f'Desteklenmeyen dosya türü. İzin verilen: {", ".join(allowed_extensions)}')
    
    # File size validation
    try:
        file.seek(0, 2)  # End of file
        file_size = file.tell()
        file.seek(0)  # Back to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            result['valid'] = False
            result['errors'].append(f'Dosya boyutu çok büyük. Maksimum: {max_size_mb}MB')
    
    except Exception as e:
        result['warnings'].append(f'Dosya boyutu kontrol edilemedi: {str(e)}')
    
    return result
