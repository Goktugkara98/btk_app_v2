# =============================================================================
# SQLALCHEMY MIGRATION SYSTEM
# =============================================================================
# Modern SQLAlchemy-based database migration and management system
# =============================================================================

import os
from typing import Optional, Dict, List
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import db
from .models import *

class SQLAlchemyMigrationManager:
    """SQLAlchemy-based database migration manager"""
    
    def __init__(self, app=None):
        """Initialize migration manager"""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        db.init_app(app)
    
    def create_all_tables(self) -> bool:
        """Create all tables defined in models"""
        try:
            with self.app.app_context():
                db.create_all()
                print("✅ All tables created successfully")
                return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def drop_all_tables(self) -> bool:
        """Drop all tables (use with caution!)"""
        try:
            with self.app.app_context():
                db.drop_all()
                print("✅ All tables dropped successfully")
                return True
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            return False
    
    def recreate_all_tables(self) -> bool:
        """Drop and recreate all tables"""
        try:
            print("🔄 Recreating all tables...")
            if self.drop_all_tables():
                return self.create_all_tables()
            return False
        except Exception as e:
            print(f"❌ Error recreating tables: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, int]:
        """Get information about all tables and their row counts"""
        info = {}
        try:
            with self.app.app_context():
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                
                for table_name in table_names:
                    try:
                        result = db.session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                        count = result.scalar()
                        info[table_name] = count
                    except Exception as e:
                        print(f"Warning: Could not get count for table {table_name}: {e}")
                        info[table_name] = 0
                
                return info
        except Exception as e:
            print(f"❌ Error getting table info: {e}")
            return {}
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists"""
        try:
            with self.app.app_context():
                inspector = inspect(db.engine)
                return table_name in inspector.get_table_names()
        except Exception as e:
            print(f"❌ Error checking table existence: {e}")
            return False
    
    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema information for a specific table"""
        try:
            with self.app.app_context():
                inspector = inspect(db.engine)
                if table_name not in inspector.get_table_names():
                    return None
                
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'indexes': indexes,
                    'foreign_keys': foreign_keys
                }
        except Exception as e:
            print(f"❌ Error getting table schema: {e}")
            return None
    
    def seed_initial_data(self) -> bool:
        """Seed initial data into the database"""
        try:
            with self.app.app_context():
                # Seed grades
                self._seed_grades()
                
                # Seed subjects
                self._seed_subjects()
                
                # Seed units
                self._seed_units()
                
                # Seed topics
                self._seed_topics()
                
                print("✅ Initial data seeded successfully")
                return True
        except Exception as e:
            print(f"❌ Error seeding initial data: {e}")
            return False
    
    def _seed_grades(self):
        """Seed grade data"""
        if db.session.query(Grade).count() == 0:
            grades = [
                Grade(grade_name="8. Sınıf", grade_number=8, description="Ortaokul 8. sınıf"),
                Grade(grade_name="9. Sınıf", grade_number=9, description="Lise 9. sınıf"),
                Grade(grade_name="10. Sınıf", grade_number=10, description="Lise 10. sınıf"),
                Grade(grade_name="11. Sınıf", grade_number=11, description="Lise 11. sınıf"),
                Grade(grade_name="12. Sınıf", grade_number=12, description="Lise 12. sınıf")
            ]
            db.session.add_all(grades)
            db.session.commit()
            print("✅ Grades seeded")
    
    def _seed_subjects(self):
        """Seed subject data"""
        if db.session.query(Subject).count() == 0:
            # Get grade 8
            grade_8 = db.session.query(Grade).filter_by(grade_number=8).first()
            if grade_8:
                subjects = [
                    Subject(subject_name="Türkçe", subject_code="TRK8", grade_id=grade_8.grade_id),
                    Subject(subject_name="Matematik", subject_code="MAT8", grade_id=grade_8.grade_id),
                    Subject(subject_name="Fen Bilimleri", subject_code="FEN8", grade_id=grade_8.grade_id),
                    Subject(subject_name="Sosyal Bilgiler", subject_code="SOS8", grade_id=grade_8.grade_id),
                    Subject(subject_name="İngilizce", subject_code="ING8", grade_id=grade_8.grade_id)
                ]
                db.session.add_all(subjects)
                db.session.commit()
                print("✅ Subjects seeded")
    
    def _seed_units(self):
        """Seed unit data"""
        if db.session.query(Unit).count() == 0:
            # Get Turkish subject
            turkish = db.session.query(Subject).filter_by(subject_code="TRK8").first()
            if turkish:
                units = [
                    Unit(unit_name="Fiilimsiler", unit_number=1, subject_id=turkish.subject_id),
                    Unit(unit_name="Cümle Türleri", unit_number=2, subject_id=turkish.subject_id),
                    Unit(unit_name="Paragraf", unit_number=3, subject_id=turkish.subject_id)
                ]
                db.session.add_all(units)
                db.session.commit()
                print("✅ Units seeded")
    
    def _seed_topics(self):
        """Seed topic data"""
        if db.session.query(Topic).count() == 0:
            # Get Fiilimsiler unit
            fiilimsiler = db.session.query(Unit).filter_by(unit_name="Fiilimsiler").first()
            if fiilimsiler:
                topics = [
                    Topic(topic_name="Fiilimsi Türleri", topic_number=1, unit_id=fiilimsiler.unit_id),
                    Topic(topic_name="Fiilimsi Örnekleri", topic_number=2, unit_id=fiilimsiler.unit_id),
                    Topic(topic_name="Fiilimsi Cümleleri", topic_number=3, unit_id=fiilimsiler.unit_id)
                ]
                db.session.add_all(topics)
                db.session.commit()
                print("✅ Topics seeded")
    
    def create_sample_questions(self) -> bool:
        """Create sample questions for testing"""
        try:
            with self.app.app_context():
                if db.session.query(Question).count() > 0:
                    print("ℹ️ Questions already exist, skipping sample creation")
                    return True
                
                # Get first topic
                topic = db.session.query(Topic).first()
                if not topic:
                    print("❌ No topics found, cannot create questions")
                    return False
                
                # Create sample question
                question = Question(
                    question_text="Aşağıdakilerden hangisi bir fiilimsi türüdür?",
                    question_type="multiple_choice",
                    difficulty_level="easy",
                    explanation="Fiilimsiler üç türde bulunur: isim-fiil, sıfat-fiil ve zarf-fiil.",
                    topic_id=topic.topic_id
                )
                db.session.add(question)
                db.session.flush()  # Get the question ID
                
                # Create options
                options = [
                    QuestionOption(option_text="İsim-fiil", is_correct=True, option_order=1, question_id=question.question_id),
                    QuestionOption(option_text="Sıfat-fiil", is_correct=False, option_order=2, question_id=question.question_id),
                    QuestionOption(option_text="Zarf-fiil", is_correct=False, option_order=3, question_id=question.question_id),
                    QuestionOption(option_text="Fiil", is_correct=False, option_order=4, question_id=question.question_id)
                ]
                db.session.add_all(options)
                db.session.commit()
                
                print("✅ Sample questions created successfully")
                return True
        except Exception as e:
            print(f"❌ Error creating sample questions: {e}")
            return False
    
    def run_full_migration(self) -> bool:
        """Run complete migration process"""
        try:
            print("🚀 Starting full database migration...")
            
            # Create tables
            if not self.create_all_tables():
                return False
            
            # Seed initial data
            if not self.seed_initial_data():
                return False
            
            # Create sample questions
            if not self.create_sample_questions():
                return False
            
            print("🎉 Full migration completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Full migration failed: {e}")
            return False

# Convenience function for easy access
def run_migrations(app):
    """Run migrations for Flask app"""
    migrator = SQLAlchemyMigrationManager(app)
    return migrator.run_full_migration()
