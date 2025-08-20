"""
Response Utilities - Standardized API Response Helpers
Provides consistent response formatting for all API endpoints
"""

from flask import jsonify
from typing import Any, Optional, Union
from datetime import datetime

def success_response(message: str, data: Any = None, status_code: int = 200) -> tuple:
    """
    Başarılı API response'u oluşturur
    
    Args:
        message: Başarı mesajı
        data: Response data'sı (opsiyonel)
        status_code: HTTP status code (varsayılan: 200)
    
    Returns:
        Flask response tuple (json, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None, details: Optional[Any] = None) -> tuple:
    """
    Hata API response'u oluşturur
    
    Args:
        message: Hata mesajı
        status_code: HTTP status code (varsayılan: 400)
        error_code: Özel hata kodu (opsiyonel)
        details: Hata detayları (opsiyonel)
    
    Returns:
        Flask response tuple (json, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def paginated_response(message: str, data: list, page: int, per_page: int, total: int, status_code: int = 200) -> tuple:
    """
    Sayfalanmış API response'u oluşturur
    
    Args:
        message: Başarı mesajı
        data: Sayfa verisi
        page: Mevcut sayfa numarası
        per_page: Sayfa başına kayıt sayısı
        total: Toplam kayıt sayısı
        status_code: HTTP status code (varsayılan: 200)
    
    Returns:
        Flask response tuple (json, status_code)
    """
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), status_code

def validation_error_response(errors: Union[list, dict], message: str = "Validation failed") -> tuple:
    """
    Validation hatası response'u oluşturur
    
    Args:
        errors: Validation hataları listesi veya dict'i
        message: Ana hata mesajı
    
    Returns:
        Flask response tuple (json, 422)
    """
    return error_response(
        message=message,
        status_code=422,
        error_code='VALIDATION_ERROR',
        details=errors
    )

def not_found_response(resource: str, resource_id: Optional[Union[int, str]] = None) -> tuple:
    """
    404 Not Found response'u oluşturur
    
    Args:
        resource: Aranan kaynak türü
        resource_id: Kaynak ID'si (opsiyonel)
    
    Returns:
        Flask response tuple (json, 404)
    """
    message = f"{resource} bulunamadı"
    if resource_id:
        message += f" (ID: {resource_id})"
    
    return error_response(
        message=message,
        status_code=404,
        error_code='NOT_FOUND'
    )

def unauthorized_response(message: str = "Yetkilendirme gerekli") -> tuple:
    """
    401 Unauthorized response'u oluşturur
    
    Args:
        message: Hata mesajı
    
    Returns:
        Flask response tuple (json, 401)
    """
    return error_response(
        message=message,
        status_code=401,
        error_code='UNAUTHORIZED'
    )

def forbidden_response(message: str = "Bu işlem için yetkiniz yok") -> tuple:
    """
    403 Forbidden response'u oluşturur
    
    Args:
        message: Hata mesajı
    
    Returns:
        Flask response tuple (json, 403)
    """
    return error_response(
        message=message,
        status_code=403,
        error_code='FORBIDDEN'
    )

def server_error_response(message: str = "Sunucu hatası oluştu") -> tuple:
    """
    500 Internal Server Error response'u oluşturur
    
    Args:
        message: Hata mesajı
    
    Returns:
        Flask response tuple (json, 500)
    """
    return error_response(
        message=message,
        status_code=500,
        error_code='INTERNAL_SERVER_ERROR'
    )
