from flask import Flask, session
from config import get_config
import os

def create_app(config_class=None):
    """Create and configure the Flask application."""
    # Get configuration
    config = config_class or get_config()
    
    # Create Flask app instance
    app = Flask(__name__, 
               template_folder=str(config.APP.TEMPLATE_DIR),
               static_folder=str(config.APP.STATIC_DIR),
               static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config)
    
    # Set secret key from config
    app.secret_key = config.SECURITY.SECRET_KEY
    
    # Ensure required directories exist
    config.APP.ensure_directories()
    
    # Import and register blueprints
    from app.routes import api_bp, pages_bp
    from app.routes.api.admin_routes import admin_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)
    app.register_blueprint(admin_bp)
    
    # Context processor for session injection into templates
    @app.context_processor
    def inject_session():
        return {'session': session}
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.debug)