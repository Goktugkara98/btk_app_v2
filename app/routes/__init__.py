# Import blueprints
from .api import api_bp
from .pages import pages_bp

# This makes the blueprints available when importing from app.routes
__all__ = ['api_bp', 'pages_bp']
