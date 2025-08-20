"""
Custom Exceptions - Application-specific Error Classes
Provides custom exception classes for better error handling
"""

class BTKAppException(Exception):
    """Base exception class for BTK App"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Exception'ı dictionary'e çevirir"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }

class ValidationError(BTKAppException):
    """Data validation hatası"""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.field = field
        self.value = value
        
        if field:
            self.details['field'] = field
        if value is not None:
            self.details['value'] = value

class NotFoundError(BTKAppException):
    """Kaynak bulunamadı hatası"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: any = None):
        super().__init__(message, 'NOT_FOUND')
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        if resource_type:
            self.details['resource_type'] = resource_type
        if resource_id is not None:
            self.details['resource_id'] = resource_id

class DatabaseError(BTKAppException):
    """Database işlem hatası"""
    
    def __init__(self, message: str, operation: str = None, table: str = None):
        super().__init__(message, 'DATABASE_ERROR')
        self.operation = operation
        self.table = table
        
        if operation:
            self.details['operation'] = operation
        if table:
            self.details['table'] = table

class AuthenticationError(BTKAppException):
    """Kimlik doğrulama hatası"""
    
    def __init__(self, message: str, auth_type: str = None):
        super().__init__(message, 'AUTHENTICATION_ERROR')
        self.auth_type = auth_type
        
        if auth_type:
            self.details['auth_type'] = auth_type

class AuthorizationError(BTKAppException):
    """Yetkilendirme hatası"""
    
    def __init__(self, message: str, required_permission: str = None, user_permissions: list = None):
        super().__init__(message, 'AUTHORIZATION_ERROR')
        self.required_permission = required_permission
        self.user_permissions = user_permissions
        
        if required_permission:
            self.details['required_permission'] = required_permission
        if user_permissions:
            self.details['user_permissions'] = user_permissions

class BusinessLogicError(BTKAppException):
    """İş mantığı hatası"""
    
    def __init__(self, message: str, business_rule: str = None, context: dict = None):
        super().__init__(message, 'BUSINESS_LOGIC_ERROR')
        self.business_rule = business_rule
        self.context = context or {}
        
        if business_rule:
            self.details['business_rule'] = business_rule
        if context:
            self.details['context'] = context

class ExternalServiceError(BTKAppException):
    """Dış servis hatası"""
    
    def __init__(self, message: str, service_name: str = None, response_code: int = None):
        super().__init__(message, 'EXTERNAL_SERVICE_ERROR')
        self.service_name = service_name
        self.response_code = response_code
        
        if service_name:
            self.details['service_name'] = service_name
        if response_code:
            self.details['response_code'] = response_code

class ConfigurationError(BTKAppException):
    """Konfigürasyon hatası"""
    
    def __init__(self, message: str, config_key: str = None, config_value: any = None):
        super().__init__(message, 'CONFIGURATION_ERROR')
        self.config_key = config_key
        self.config_value = config_value
        
        if config_key:
            self.details['config_key'] = config_key
        if config_value is not None:
            self.details['config_value'] = config_value

class FileOperationError(BTKAppException):
    """Dosya işlem hatası"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        super().__init__(message, 'FILE_OPERATION_ERROR')
        self.file_path = file_path
        self.operation = operation
        
        if file_path:
            self.details['file_path'] = file_path
        if operation:
            self.details['operation'] = operation

class ImportExportError(BTKAppException):
    """Import/Export işlem hatası"""
    
    def __init__(self, message: str, operation_type: str = None, file_format: str = None):
        super().__init__(message, 'IMPORT_EXPORT_ERROR')
        self.operation_type = operation_type
        self.file_format = file_format
        
        if operation_type:
            self.details['operation_type'] = operation_type
        if file_format:
            self.details['file_format'] = file_format

class RateLimitError(BTKAppException):
    """Rate limit hatası"""
    
    def __init__(self, message: str, limit: int = None, window: str = None):
        super().__init__(message, 'RATE_LIMIT_ERROR')
        self.limit = limit
        self.window = window
        
        if limit:
            self.details['limit'] = limit
        if window:
            self.details['window'] = window

class MaintenanceError(BTKAppException):
    """Bakım modu hatası"""
    
    def __init__(self, message: str, estimated_duration: str = None, maintenance_type: str = None):
        super().__init__(message, 'MAINTENANCE_ERROR')
        self.estimated_duration = estimated_duration
        self.maintenance_type = maintenance_type
        
        if estimated_duration:
            self.details['estimated_duration'] = estimated_duration
        if maintenance_type:
            self.details['maintenance_type'] = maintenance_type

# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 422,
    NotFoundError: 404,
    DatabaseError: 500,
    AuthenticationError: 401,
    AuthorizationError: 403,
    BusinessLogicError: 400,
    ExternalServiceError: 502,
    ConfigurationError: 500,
    FileOperationError: 500,
    ImportExportError: 400,
    RateLimitError: 429,
    MaintenanceError: 503
}

def get_http_status_code(exception: Exception) -> int:
    """Exception için HTTP status code döner"""
    exception_class = exception.__class__
    
    # Check exact class match first
    if exception_class in EXCEPTION_STATUS_MAP:
        return EXCEPTION_STATUS_MAP[exception_class]
    
    # Check inheritance hierarchy
    for base_class, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, base_class):
            return status_code
    
    # Default to 500 for unknown exceptions
    return 500
