# =============================================================================
# CURRICULUM SERVICE
# =============================================================================
# Müfredat yönetimi için servis katmanı
# Grades, Subjects, Units ve Topics için CRUD işlemleri
# =============================================================================

import json
import os
from typing import List, Dict, Optional, Any
from app.database.repositories.base_repository import BaseRepository

class CurriculumService:
    """Müfredat yönetimi için servis sınıfı"""
    
    def __init__(self):
        self.base_repo = BaseRepository()
        self.curriculum_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'curriculum_structure'
        )
    
    # =============================================================================
    # GRADES (SINIFLAR) YÖNETİMİ
    # =============================================================================
    
    def get_all_grades(self) -> List[Dict[str, Any]]:
        """Tüm sınıfları getirir"""
        query = """
        SELECT grade_id, grade_name, description, is_active, 
               created_at, updated_at
        FROM grades 
        ORDER BY grade_name
        """
        return self.base_repo.fetch_all(query)
    
    def get_grade_by_id(self, grade_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre sınıf getirir"""
        query = "SELECT * FROM grades WHERE grade_id = %s"
        return self.base_repo.fetch_one(query, (grade_id,))
    
    def create_grade(self, grade_name: str, description: str = None) -> int:
        """Yeni sınıf oluşturur"""
        query = """
        INSERT INTO grades (grade_name, description) 
        VALUES (%s, %s)
        """
        return self.base_repo.execute_query(query, (grade_name, description))
    
    def update_grade(self, grade_id: int, grade_name: str, description: str = None, is_active: bool = True) -> bool:
        """Sınıf bilgilerini günceller"""
        query = """
        UPDATE grades 
        SET grade_name = %s, description = %s, is_active = %s 
        WHERE grade_id = %s
        """
        result = self.base_repo.execute_query(query, (grade_name, description, is_active, grade_id))
        return result > 0
    
    def delete_grade(self, grade_id: int) -> bool:
        """Sınıfı siler (soft delete)"""
        query = "UPDATE grades SET is_active = false WHERE grade_id = %s"
        result = self.base_repo.execute_query(query, (grade_id,))
        return result > 0
    
    # =============================================================================
    # SUBJECTS (DERSLER) YÖNETİMİ
    # =============================================================================
    
    def get_subjects_by_grade(self, grade_id: int) -> List[Dict[str, Any]]:
        """Sınıfa göre dersleri getirir"""
        query = """
        SELECT s.subject_id, s.grade_id, s.subject_name, s.description, 
               s.is_active, s.created_at, s.updated_at, g.grade_name
        FROM subjects s
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE s.grade_id = %s AND s.is_active = true
        ORDER BY s.subject_name
        """
        return self.base_repo.fetch_all(query, (grade_id,))
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """Tüm dersleri getirir"""
        query = """
        SELECT s.subject_id, s.grade_id, s.subject_name, s.description, 
               s.is_active, s.created_at, s.updated_at, g.grade_name
        FROM subjects s
        JOIN grades g ON s.grade_id = g.grade_id
        ORDER BY g.grade_name, s.subject_name
        """
        return self.base_repo.fetch_all(query)
    
    def get_subject_by_id(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ders getirir"""
        query = """
        SELECT s.*, g.grade_name 
        FROM subjects s
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE s.subject_id = %s
        """
        return self.base_repo.fetch_one(query, (subject_id,))
    
    def create_subject(self, grade_id: int, subject_name: str, description: str = None) -> int:
        """Yeni ders oluşturur"""
        query = """
        INSERT INTO subjects (grade_id, subject_name, description) 
        VALUES (%s, %s, %s)
        """
        return self.base_repo.execute_query(query, (grade_id, subject_name, description))
    
    def update_subject(self, subject_id: int, grade_id: int, subject_name: str, 
                      description: str = None, is_active: bool = True) -> bool:
        """Ders bilgilerini günceller"""
        query = """
        UPDATE subjects 
        SET grade_id = %s, subject_name = %s, description = %s, is_active = %s 
        WHERE subject_id = %s
        """
        result = self.base_repo.execute_query(query, (grade_id, subject_name, description, is_active, subject_id))
        return result > 0
    
    def delete_subject(self, subject_id: int) -> bool:
        """Dersi siler (soft delete)"""
        query = "UPDATE subjects SET is_active = false WHERE subject_id = %s"
        result = self.base_repo.execute_query(query, (subject_id,))
        return result > 0
    
    # =============================================================================
    # UNITS (ÜNİTELER) YÖNETİMİ
    # =============================================================================
    
    def get_units_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """Derse göre üniteleri getirir"""
        query = """
        SELECT u.unit_id, u.subject_id, u.unit_name, u.description, 
               u.is_active, u.created_at, u.updated_at, u.order_number,
               s.subject_name, g.grade_name
        FROM units u
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE u.subject_id = %s AND u.is_active = true
        ORDER BY u.order_number, u.unit_name
        """
        return self.base_repo.fetch_all(query, (subject_id,))
    
    def get_all_units(self) -> List[Dict[str, Any]]:
        """Tüm üniteleri getirir"""
        query = """
        SELECT u.unit_id, u.subject_id, u.unit_name, u.description, 
               u.is_active, u.created_at, u.updated_at, u.order_number,
               s.subject_name, g.grade_name
        FROM units u
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        ORDER BY g.grade_name, s.subject_name, u.order_number, u.unit_name
        """
        return self.base_repo.fetch_all(query)
    
    def get_unit_by_id(self, unit_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ünite getirir"""
        query = """
        SELECT u.*, s.subject_name, g.grade_name 
        FROM units u
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE u.unit_id = %s
        """
        return self.base_repo.fetch_one(query, (unit_id,))
    
    def create_unit(self, subject_id: int, unit_name: str, description: str = None, order_number: int = None) -> int:
        """Yeni ünite oluşturur"""
        if order_number is None:
            # Get next order number
            max_order = self.base_repo.fetch_one(
                "SELECT COALESCE(MAX(order_number), 0) as max_order FROM units WHERE subject_id = %s",
                (subject_id,)
            )
            order_number = (max_order['max_order'] if max_order else 0) + 1
        
        query = """
        INSERT INTO units (subject_id, unit_name, description, order_number) 
        VALUES (%s, %s, %s, %s)
        """
        return self.base_repo.execute_query(query, (subject_id, unit_name, description, order_number))
    
    def update_unit(self, unit_id: int, subject_id: int, unit_name: str, 
                   description: str = None, is_active: bool = True, order_number: int = None) -> bool:
        """Ünite bilgilerini günceller"""
        if order_number is not None:
            query = """
            UPDATE units 
            SET subject_id = %s, unit_name = %s, description = %s, is_active = %s, order_number = %s 
            WHERE unit_id = %s
            """
            result = self.base_repo.execute_query(query, (subject_id, unit_name, description, is_active, order_number, unit_id))
        else:
            query = """
            UPDATE units 
            SET subject_id = %s, unit_name = %s, description = %s, is_active = %s 
            WHERE unit_id = %s
            """
            result = self.base_repo.execute_query(query, (subject_id, unit_name, description, is_active, unit_id))
        return result > 0
    
    def delete_unit(self, unit_id: int) -> bool:
        """Üniteyi siler (soft delete)"""
        query = "UPDATE units SET is_active = false WHERE unit_id = %s"
        result = self.base_repo.execute_query(query, (unit_id,))
        return result > 0
    
    # =============================================================================
    # TOPICS (KONULAR) YÖNETİMİ
    # =============================================================================
    
    def get_topics_by_unit(self, unit_id: int) -> List[Dict[str, Any]]:
        """Üniteye göre konuları getirir"""
        query = """
        SELECT t.topic_id, t.unit_id, t.topic_name, t.description, 
               t.is_active, t.created_at, t.updated_at,
               u.unit_name, s.subject_name, g.grade_name
        FROM topics t
        JOIN units u ON t.unit_id = u.unit_id
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE t.unit_id = %s AND t.is_active = true
        ORDER BY t.topic_name
        """
        return self.base_repo.fetch_all(query, (unit_id,))
    
    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Tüm konuları getirir"""
        query = """
        SELECT t.topic_id, t.unit_id, t.topic_name, t.description, 
               t.is_active, t.created_at, t.updated_at,
               u.unit_name, s.subject_name, g.grade_name
        FROM topics t
        JOIN units u ON t.unit_id = u.unit_id
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        ORDER BY g.grade_name, s.subject_name, u.unit_name, t.topic_name
        """
        return self.base_repo.fetch_all(query)
    
    def get_topic_by_id(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre konu getirir"""
        query = """
        SELECT t.*, u.unit_name, s.subject_name, g.grade_name 
        FROM topics t
        JOIN units u ON t.unit_id = u.unit_id
        JOIN subjects s ON u.subject_id = s.subject_id
        JOIN grades g ON s.grade_id = g.grade_id
        WHERE t.topic_id = %s
        """
        return self.base_repo.fetch_one(query, (topic_id,))
    
    def create_topic(self, unit_id: int, topic_name: str, description: str = None) -> int:
        """Yeni konu oluşturur"""
        query = """
        INSERT INTO topics (unit_id, topic_name, description) 
        VALUES (%s, %s, %s)
        """
        return self.base_repo.execute_query(query, (unit_id, topic_name, description))
    
    def update_topic(self, topic_id: int, unit_id: int, topic_name: str, 
                    description: str = None, is_active: bool = True) -> bool:
        """Konu bilgilerini günceller"""
        query = """
        UPDATE topics 
        SET unit_id = %s, topic_name = %s, description = %s, is_active = %s 
        WHERE topic_id = %s
        """
        result = self.base_repo.execute_query(query, (unit_id, topic_name, description, is_active, topic_id))
        return result > 0
    
    def delete_topic(self, topic_id: int) -> bool:
        """Konuyu siler (soft delete)"""
        query = "UPDATE topics SET is_active = false WHERE topic_id = %s"
        result = self.base_repo.execute_query(query, (topic_id,))
        return result > 0
    
    # =============================================================================
    # JSON DOSYALARI YÖNETİMİ
    # =============================================================================
    
    def get_curriculum_json_files(self) -> List[str]:
        """Mevcut JSON müfredat dosyalarını listeler"""
        if not os.path.exists(self.curriculum_data_path):
            return []
        
        json_files = []
        for file in os.listdir(self.curriculum_data_path):
            if file.endswith('.json'):
                json_files.append(file)
        return sorted(json_files)
    
    def load_curriculum_from_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """JSON dosyasından müfredat verilerini yükler"""
        file_path = os.path.join(self.curriculum_data_path, filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON dosyası yüklenirken hata: {e}")
            return None
    
    def save_curriculum_to_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Müfredat verilerini JSON dosyasına kaydeder"""
        file_path = os.path.join(self.curriculum_data_path, filename)
        
        try:
            # Dizin yoksa oluştur
            os.makedirs(self.curriculum_data_path, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"JSON dosyası kaydedilirken hata: {e}")
            return False
    
    def import_json_to_database(self, filename: str) -> Dict[str, Any]:
        """JSON dosyasından veritabanına müfredat verilerini aktarır"""
        data = self.load_curriculum_from_json(filename)
        if not data:
            return {"success": False, "message": "JSON dosyası yüklenemedi"}
        
        try:
            imported_count = {"grades": 0, "subjects": 0, "units": 0, "topics": 0}
            
            # JSON verisi liste formatında olabilir
            curriculum_data = data[0] if isinstance(data, list) else data
            
            # Sınıf oluştur veya bul
            grade_name = curriculum_data.get("gradeName", f"Grade {curriculum_data.get('gradeLevel', 'Unknown')}")
            
            # Mevcut sınıfı kontrol et
            existing_grade = self.base_repo.fetch_one(
                "SELECT grade_id FROM grades WHERE grade_name = %s", 
                (grade_name,)
            )
            
            if existing_grade:
                grade_id = existing_grade['grade_id']
            else:
                grade_id = self.create_grade(grade_name)
                imported_count["grades"] += 1
            
            # Dersleri işle
            for subject_data in curriculum_data.get("subjects", []):
                subject_name = subject_data.get("subjectName")
                if not subject_name:
                    continue
                
                # Mevcut dersi kontrol et
                existing_subject = self.base_repo.fetch_one(
                    "SELECT subject_id FROM subjects WHERE grade_id = %s AND subject_name = %s",
                    (grade_id, subject_name)
                )
                
                if existing_subject:
                    subject_id = existing_subject['subject_id']
                else:
                    subject_id = self.create_subject(grade_id, subject_name)
                    imported_count["subjects"] += 1
                
                # Üniteleri işle
                for unit_data in subject_data.get("units", []):
                    unit_name = unit_data.get("unitName")
                    if not unit_name:
                        continue
                    
                    # Mevcut üniteyi kontrol et
                    existing_unit = self.base_repo.fetch_one(
                        "SELECT unit_id FROM units WHERE subject_id = %s AND unit_name = %s",
                        (subject_id, unit_name)
                    )
                    
                    if existing_unit:
                        unit_id = existing_unit['unit_id']
                    else:
                        unit_id = self.create_unit(subject_id, unit_name)
                        imported_count["units"] += 1
                    
                    # Konuları işle
                    for topic_data in unit_data.get("topics", []):
                        topic_name = topic_data.get("topicName")
                        if not topic_name:
                            continue
                        
                        # Mevcut konuyu kontrol et
                        existing_topic = self.base_repo.fetch_one(
                            "SELECT topic_id FROM topics WHERE unit_id = %s AND topic_name = %s",
                            (unit_id, topic_name)
                        )
                        
                        if not existing_topic:
                            self.create_topic(unit_id, topic_name)
                            imported_count["topics"] += 1
            
            return {
                "success": True, 
                "message": "JSON verisi başarıyla aktarıldı",
                "imported": imported_count
            }
            
        except Exception as e:
            return {"success": False, "message": f"Aktarım sırasında hata: {str(e)}"}
    
    def export_database_to_json(self, grade_id: int) -> Optional[Dict[str, Any]]:
        """Veritabanından belirli sınıfın müfredat verilerini JSON formatında çıkarır"""
        try:
            # Sınıf bilgisini al
            grade = self.get_grade_by_id(grade_id)
            if not grade:
                return None
            
            # Dersleri al
            subjects = self.get_subjects_by_grade(grade_id)
            subjects_data = []
            
            for subject in subjects:
                # Üniteleri al
                units = self.get_units_by_subject(subject['subject_id'])
                units_data = []
                
                for unit in units:
                    # Konuları al
                    topics = self.get_topics_by_unit(unit['unit_id'])
                    topics_data = [
                        {
                            "topicId": f"topic_{topic['topic_id']}",
                            "topicName": topic['topic_name']
                        }
                        for topic in topics
                    ]
                    
                    units_data.append({
                        "unitId": f"unit_{unit['unit_id']}",
                        "unitName": unit['unit_name'],
                        "topics": topics_data
                    })
                
                subjects_data.append({
                    "subjectId": f"subject_{subject['subject_id']}",
                    "subjectName": subject['subject_name'],
                    "units": units_data
                })
            
            return [{
                "gradeLevel": grade_id,
                "gradeName": grade['grade_name'],
                "subjects": subjects_data
            }]
            
        except Exception as e:
            print(f"Export sırasında hata: {e}")
            return None
    
    # =============================================================================
    # İSTATİSTİKLER VE ÖZET BİLGİLER
    # =============================================================================
    
    def get_curriculum_statistics(self) -> Dict[str, Any]:
        """Müfredat istatistiklerini getirir"""
        stats = {}
        
        try:
            # Toplam sayılar - null check ile ve basit sorgular
            grades_result = self.base_repo.fetch_one("SELECT COUNT(*) as count FROM grades")
            stats['total_grades'] = grades_result['count'] if grades_result else 0
            
            subjects_result = self.base_repo.fetch_one("SELECT COUNT(*) as count FROM subjects")
            stats['total_subjects'] = subjects_result['count'] if subjects_result else 0
            
            units_result = self.base_repo.fetch_one("SELECT COUNT(*) as count FROM units")
            stats['total_units'] = units_result['count'] if units_result else 0
            
            topics_result = self.base_repo.fetch_one("SELECT COUNT(*) as count FROM topics")
            stats['total_topics'] = topics_result['count'] if topics_result else 0
            
            # Sınıf bazında istatistikler - basitleştirilmiş sorgu
            grade_stats_query = """
            SELECT g.grade_name,
                   COUNT(DISTINCT s.subject_id) as subject_count,
                   COUNT(DISTINCT u.unit_id) as unit_count,
                   COUNT(DISTINCT t.topic_id) as topic_count
            FROM grades g
            LEFT JOIN subjects s ON g.grade_id = s.grade_id
            LEFT JOIN units u ON s.subject_id = u.subject_id
            LEFT JOIN topics t ON u.unit_id = t.unit_id
            GROUP BY g.grade_id, g.grade_name
            ORDER BY g.grade_name
            """
            grade_breakdown = self.base_repo.fetch_all(grade_stats_query)
            stats['grade_breakdown'] = grade_breakdown if grade_breakdown else []
            
        except Exception as e:
            print(f"Statistics error: {e}")
            # Varsayılan değerler döndür
            stats = {
                'total_grades': 0,
                'total_subjects': 0,
                'total_units': 0,
                'total_topics': 0,
                'grade_breakdown': []
            }
        
        return stats
