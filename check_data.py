#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from app.database.connection import get_db
    
    db = get_db()
    
    # Check existing data counts
    grades_count = db.execute('SELECT COUNT(*) FROM grades').fetchone()[0]
    subjects_count = db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]
    units_count = db.execute('SELECT COUNT(*) FROM units').fetchone()[0]
    topics_count = db.execute('SELECT COUNT(*) FROM topics').fetchone()[0]
    
    print(f"Grades: {grades_count}")
    print(f"Subjects: {subjects_count}")
    print(f"Units: {units_count}")
    print(f"Topics: {topics_count}")
    
    # Check if tables exist and have structure
    print("\nTable structures:")
    
    try:
        grades_structure = db.execute("PRAGMA table_info(grades)").fetchall()
        print(f"Grades table columns: {len(grades_structure)}")
    except Exception as e:
        print(f"Grades table error: {e}")
    
    try:
        subjects_structure = db.execute("PRAGMA table_info(subjects)").fetchall()
        print(f"Subjects table columns: {len(subjects_structure)}")
    except Exception as e:
        print(f"Subjects table error: {e}")
    
    try:
        units_structure = db.execute("PRAGMA table_info(units)").fetchall()
        print(f"Units table columns: {len(units_structure)}")
    except Exception as e:
        print(f"Units table error: {e}")
    
    try:
        topics_structure = db.execute("PRAGMA table_info(topics)").fetchall()
        print(f"Topics table columns: {len(topics_structure)}")
    except Exception as e:
        print(f"Topics table error: {e}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
