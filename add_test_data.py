#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.database.connection import get_db
    from app.services.curriculum_service import CurriculumService
    
    print("Test verileri ekleniyor...")
    
    # Initialize services
    curriculum_service = CurriculumService()
    db = get_db()
    
    # Test Grades
    print("Sınıflar ekleniyor...")
    test_grades = [
        {"grade_name": "9. Sınıf", "description": "Lise 9. sınıf müfredatı", "is_active": True},
        {"grade_name": "10. Sınıf", "description": "Lise 10. sınıf müfredatı", "is_active": True},
        {"grade_name": "11. Sınıf", "description": "Lise 11. sınıf müfredatı", "is_active": True},
        {"grade_name": "12. Sınıf", "description": "Lise 12. sınıf müfredatı", "is_active": True}
    ]
    
    for grade_data in test_grades:
        try:
            result = curriculum_service.create_grade(**grade_data)
            if result:
                print(f"✓ {grade_data['grade_name']} eklendi")
            else:
                print(f"✗ {grade_data['grade_name']} eklenemedi")
        except Exception as e:
            print(f"✗ {grade_data['grade_name']} hatası: {e}")
    
    # Get grades for subjects
    grades = curriculum_service.get_all_grades()
    print(f"\nToplam {len(grades)} sınıf bulundu")
    
    # Test Subjects
    print("\nDersler ekleniyor...")
    test_subjects = [
        {"subject_name": "Matematik", "description": "Matematik dersi", "grade_id": grades[0]['grade_id'], "is_active": True},
        {"subject_name": "Fizik", "description": "Fizik dersi", "grade_id": grades[0]['grade_id'], "is_active": True},
        {"subject_name": "Kimya", "description": "Kimya dersi", "grade_id": grades[0]['grade_id'], "is_active": True},
        {"subject_name": "Biyoloji", "description": "Biyoloji dersi", "grade_id": grades[0]['grade_id'], "is_active": True},
        {"subject_name": "Türkçe", "description": "Türkçe dersi", "grade_id": grades[0]['grade_id'], "is_active": True},
        {"subject_name": "Tarih", "description": "Tarih dersi", "grade_id": grades[0]['grade_id'], "is_active": True}
    ]
    
    for subject_data in test_subjects:
        try:
            result = curriculum_service.create_subject(**subject_data)
            if result:
                print(f"✓ {subject_data['subject_name']} eklendi")
            else:
                print(f"✗ {subject_data['subject_name']} eklenemedi")
        except Exception as e:
            print(f"✗ {subject_data['subject_name']} hatası: {e}")
    
    # Get subjects for units
    subjects = curriculum_service.get_all_subjects()
    print(f"\nToplam {len(subjects)} ders bulundu")
    
    # Test Units
    print("\nÜniteler ekleniyor...")
    test_units = [
        {"unit_name": "Sayılar", "description": "Sayılar ünitesi", "subject_id": subjects[0]['subject_id'], "is_active": True},
        {"unit_name": "Cebir", "description": "Cebir ünitesi", "subject_id": subjects[0]['subject_id'], "is_active": True},
        {"unit_name": "Geometri", "description": "Geometri ünitesi", "subject_id": subjects[0]['subject_id'], "is_active": True},
        {"unit_name": "Mekanik", "description": "Mekanik ünitesi", "subject_id": subjects[1]['subject_id'], "is_active": True},
        {"unit_name": "Elektrik", "description": "Elektrik ünitesi", "subject_id": subjects[1]['subject_id'], "is_active": True}
    ]
    
    for unit_data in test_units:
        try:
            result = curriculum_service.create_unit(**unit_data)
            if result:
                print(f"✓ {unit_data['unit_name']} eklendi")
            else:
                print(f"✗ {unit_data['unit_name']} eklenemedi")
        except Exception as e:
            print(f"✗ {unit_data['unit_name']} hatası: {e}")
    
    # Get units for topics
    units = curriculum_service.get_all_units()
    print(f"\nToplam {len(units)} ünite bulundu")
    
    # Test Topics
    print("\nKonular ekleniyor...")
    test_topics = [
        {"topic_name": "Doğal Sayılar", "description": "Doğal sayılar konusu", "unit_id": units[0]['unit_id'], "is_active": True},
        {"topic_name": "Tam Sayılar", "description": "Tam sayılar konusu", "unit_id": units[0]['unit_id'], "is_active": True},
        {"topic_name": "Rasyonel Sayılar", "description": "Rasyonel sayılar konusu", "unit_id": units[0]['unit_id'], "is_active": True},
        {"topic_name": "Denklemler", "description": "Denklemler konusu", "unit_id": units[1]['unit_id'], "is_active": True},
        {"topic_name": "Eşitsizlikler", "description": "Eşitsizlikler konusu", "unit_id": units[1]['unit_id'], "is_active": True},
        {"topic_name": "Üçgenler", "description": "Üçgenler konusu", "unit_id": units[2]['unit_id'], "is_active": True},
        {"topic_name": "Çemberler", "description": "Çemberler konusu", "unit_id": units[2]['unit_id'], "is_active": True}
    ]
    
    for topic_data in test_topics:
        try:
            result = curriculum_service.create_topic(**topic_data)
            if result:
                print(f"✓ {topic_data['topic_name']} eklendi")
            else:
                print(f"✗ {topic_data['topic_name']} eklenemedi")
        except Exception as e:
            print(f"✗ {topic_data['topic_name']} hatası: {e}")
    
    # Final count
    final_grades = len(curriculum_service.get_all_grades())
    final_subjects = len(curriculum_service.get_all_subjects())
    final_units = len(curriculum_service.get_all_units())
    final_topics = len(curriculum_service.get_all_topics())
    
    print(f"\n{'='*50}")
    print("TEST VERİLERİ EKLENDİ!")
    print(f"{'='*50}")
    print(f"Toplam Sınıf: {final_grades}")
    print(f"Toplam Ders: {final_subjects}")
    print(f"Toplam Ünite: {final_units}")
    print(f"Toplam Konu: {final_topics}")
    print(f"{'='*50}")
    
except Exception as e:
    print(f"Hata oluştu: {e}")
    import traceback
    traceback.print_exc()
