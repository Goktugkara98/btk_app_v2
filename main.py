from flask import Flask, render_template, session
from config import Config
from app.database.db_connection import DatabaseConnection
from app.database.db_migrations import DatabaseMigrations
from app.database.quiz_data_loader import QuestionLoader
import os
import secrets

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    template_dir = os.path.abspath('app/templates')
    static_dir = os.path.abspath('app/static')
    app = Flask(__name__, 
               template_folder=template_dir,
               static_folder=static_dir,
               static_url_path='/static')
    app.config.from_object(config_class)
    
    # Session configuration
    app.secret_key = secrets.token_hex(16)
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        app.logger.error(f"Failed to create instance directory: {e}")
    
    # Initialize database
    db_connection = None
    try:
        # Create database connection
        db_connection = DatabaseConnection()
        
        # Run database migrations
        migrations = DatabaseMigrations(db_connection)
        migrations.run_migrations()
        
        # Load question data if tables are empty
        try:
            question_loader = QuestionLoader(db_connection=db_connection)
            
            # Check if questions table is empty
            with db_connection as conn:
                conn.cursor.execute("SELECT COUNT(*) as count FROM questions")
                question_count = conn.cursor.fetchone()['count']
            
            if question_count == 0:
                app.logger.info("Questions table is empty. Loading question data...")
                results = question_loader.process_all_question_files()
                
                total_success = 0
                total_questions = 0
                for filename, (success, total) in results.items():
                    app.logger.info(f"Loaded {filename}: {success}/{total} questions")
                    total_success += success
                    total_questions += total
                
                app.logger.info(f"Question loading completed: {total_success}/{total_questions} questions loaded")
            else:
                app.logger.info(f"Questions table already contains {question_count} questions. Skipping question loading.")
                
        except Exception as e:
            app.logger.warning(f"Failed to load question data: {e}")
            # Don't raise here, as the main app should still work without questions
        
        # Store the database connection in the app context
        app.config['DB_CONNECTION'] = db_connection
        
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
        if db_connection:
            db_connection.close()
        raise
    
    # Register blueprints
    try:
        from app.routes import api_bp, pages_bp
        
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(pages_bp)
        app.logger.info("App blueprints registered successfully")
    except ImportError as e:
        app.logger.error(f"Failed to import app blueprints: {e}")
        raise
    except Exception as e:
        app.logger.error(f"Failed to register app blueprints: {e}")
        raise
    
    @app.context_processor
    def inject_session_data():
        return dict(session=session)
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)