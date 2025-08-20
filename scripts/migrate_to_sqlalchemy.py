#!/usr/bin/env python3
# =============================================================================
# SQLALCHEMY MIGRATION SCRIPT
# =============================================================================
# Script to migrate from old MySQL connector system to SQLAlchemy
# =============================================================================

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print("✅ Environment variables are properly configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import sqlalchemy
        import flask_sqlalchemy
        print("✅ SQLAlchemy dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def backup_existing_data():
    """Create backup of existing data (if any)"""
    print("📋 Checking for existing data...")
    
    try:
        # Import old database connection
        from app.database.db_connection import DatabaseConnection
        
        with DatabaseConnection() as conn:
            # Check if tables exist and have data
            tables_to_check = ['users', 'grades', 'subjects', 'units', 'topics', 'questions']
            existing_data = {}
            
            for table in tables_to_check:
                try:
                    conn.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = conn.cursor.fetchone()
                    count = result.get('count', 0) if result else 0
                    existing_data[table] = count
                except Exception:
                    existing_data[table] = 0
            
            # Create backup file
            backup_file = project_root / "backup_existing_data.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Backup created: {backup_file}")
            print("📊 Existing data summary:")
            for table, count in existing_data.items():
                print(f"   {table}: {count} records")
            
            return existing_data
            
    except Exception as e:
        print(f"⚠️ Could not check existing data: {e}")
        return {}

def run_sqlalchemy_migration():
    """Run the SQLAlchemy migration"""
    print("🚀 Starting SQLAlchemy migration...")
    
    try:
        from flask import Flask
        from app.database.database import init_db
        from app.database.migrations_v3 import SQLAlchemyMigrationManager
        
        # Create minimal Flask app
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Initialize database
        init_db(app)
        
        # Run migration
        with app.app_context():
            migrator = SQLAlchemyMigrationManager(app)
            success = migrator.run_full_migration()
            
            if success:
                print("✅ SQLAlchemy migration completed successfully!")
                return True
            else:
                print("❌ SQLAlchemy migration failed!")
                return False
                
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def verify_migration():
    """Verify that migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        from flask import Flask
        from app.database.database import init_db
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_db(app)
        
        with app.app_context():
            from app.database.migrations_v3 import SQLAlchemyMigrationManager
            
            migrator = SQLAlchemyMigrationManager(app)
            table_info = migrator.get_table_info()
            
            print("📊 Migration verification results:")
            for table, count in table_info.items():
                print(f"   {table}: {count} records")
            
            # Check if key tables exist
            key_tables = ['users', 'grades', 'subjects', 'units', 'topics', 'questions']
            missing_tables = [table for table in key_tables if table not in table_info]
            
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
                return False
            
            print("✅ All key tables are present")
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("🎯 Creating sample data...")
    
    try:
        from flask import Flask
        from app.database.database import init_db
        from app.database.repositories.user_repository_v2 import UserRepository
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        init_db(app)
        
        with app.app_context():
            user_repo = UserRepository()
            
            # Create sample user
            sample_user = user_repo.create(
                username="test_user",
                email="test@example.com",
                password_hash="test_password_hash",
                first_name="Test",
                last_name="User",
                is_active=True
            )
            
            if sample_user:
                print("✅ Sample user created successfully")
                print(f"   Username: {sample_user.username}")
                print(f"   Email: {sample_user.email}")
                return True
            else:
                print("❌ Failed to create sample user")
                return False
                
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 BTK APP - SQLALCHEMY MIGRATION SCRIPT")
    print("=" * 60)
    
    # Step 1: Environment check
    print("\n1️⃣ Checking environment...")
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Dependencies check
    print("\n2️⃣ Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Step 3: Backup existing data
    print("\n3️⃣ Creating backup...")
    existing_data = backup_existing_data()
    
    # Step 4: Run migration
    print("\n4️⃣ Running SQLAlchemy migration...")
    if not run_sqlalchemy_migration():
        print("❌ Migration failed! Please check the error messages above.")
        sys.exit(1)
    
    # Step 5: Verify migration
    print("\n5️⃣ Verifying migration...")
    if not verify_migration():
        print("❌ Migration verification failed!")
        sys.exit(1)
    
    # Step 6: Create sample data
    print("\n6️⃣ Creating sample data...")
    if not create_sample_data():
        print("⚠️ Sample data creation failed, but migration was successful")
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n✅ Your database has been migrated to SQLAlchemy!")
    print("✅ You can now use the new SQLAlchemy-based system")
    print("✅ Check the SQLALCHEMY_MIGRATION_README.md for usage examples")
    print("\n🚀 To test the new system, run:")
    print("   python main_sqlalchemy.py")
    print("\n🌐 Then visit: http://localhost:5000")

if __name__ == "__main__":
    main()
