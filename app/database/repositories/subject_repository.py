"""
Subject Repository - Subject Management
Handles all database operations for subjects
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository

class SubjectRepository(BaseRepository):
    """Dersleri yöneten repository"""
    
    def __init__(self):
        """Subject repository'yi başlatır"""
        super().__init__()
        self.table_name = 'subjects'
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm dersleri getirir"""
        try:
            query = """
                SELECT * FROM subjects 
                ORDER BY grade_id ASC, subject_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting all subjects: {e}")
            return []
    
    def get_all_with_grade(self) -> List[Dict[str, Any]]:
        """Tüm dersleri sınıf bilgileriyle birlikte getirir"""
        try:
            query = """
                SELECT s.*, g.grade_name
                FROM subjects s
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                ORDER BY s.subject_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting subjects with grade: {e}")
            return []
    
    def get_by_id(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ders getirir"""
        try:
            query = "SELECT * FROM subjects WHERE subject_id = %s"
            return self.fetch_one(query, (subject_id,))
        except Exception as e:
            print(f"Error getting subject by ID: {e}")
            return None
    
    def get_by_name(self, subject_name: str) -> Optional[Dict[str, Any]]:
        """İsme göre ders getirir"""
        try:
            query = "SELECT * FROM subjects WHERE subject_name = %s"
            return self.fetch_one(query, (subject_name,))
        except Exception as e:
            print(f"Error getting subject by name: {e}")
            return None
    
    def get_by_grade(self, grade_id: int) -> List[Dict[str, Any]]:
        """Sınıfa göre dersleri getirir"""
        try:
            query = """
                SELECT * FROM subjects 
                WHERE grade_id = %s
                ORDER BY subject_name ASC
            """
            return self.fetch_all(query, (grade_id,))
        except Exception as e:
            print(f"Error getting subjects by grade: {e}")
            return []
    
    def get_by_name_and_grade(self, subject_name: str, grade_id: int) -> Optional[Dict[str, Any]]:
        """İsim ve sınıfa göre ders getirir"""
        try:
            query = "SELECT * FROM subjects WHERE subject_name = %s AND grade_id = %s"
            return self.fetch_one(query, (subject_name, grade_id))
        except Exception as e:
            print(f"Error getting subject by name and grade: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Yeni ders oluşturur"""
        try:
            query = """
                INSERT INTO subjects (subject_name, grade_id, description, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            
            params = (
                data.get('subject_name'),
                data.get('grade_id'),
                data.get('description', ''),
                data.get('is_active', True)
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating subject: {e}")
            return None
    
    def update(self, subject_id: int, data: Dict[str, Any]) -> bool:
        """Ders bilgilerini günceller"""
        try:
            query = """
                UPDATE subjects 
                SET subject_name = %s, grade_id = %s, description = %s, 
                    is_active = %s, updated_at = NOW()
                WHERE subject_id = %s
            """
            
            params = (
                data.get('subject_name'),
                data.get('grade_id'),
                data.get('description', ''),
                data.get('is_active', True),
                subject_id
            )
            
            return self.execute_query(query, params) > 0
            
        except Exception as e:
            print(f"Error updating subject: {e}")
            return False
    
    def delete(self, subject_id: int) -> bool:
        """Dersi siler"""
        try:
            query = "DELETE FROM subjects WHERE subject_id = %s"
            return self.execute_query(query, (subject_id,)) > 0
        except Exception as e:
            print(f"Error deleting subject: {e}")
            return False
    
    def count_all(self) -> int:
        """Toplam ders sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM subjects"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting subjects: {e}")
            return 0
    
    def count_by_grade(self, grade_id: int) -> int:
        """Belirli sınıftaki ders sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM subjects WHERE grade_id = %s"
            result = self.fetch_one(query, (grade_id,))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting subjects by grade: {e}")
            return 0
    
    def count_active(self) -> int:
        """Aktif ders sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM subjects WHERE is_active = 1"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting active subjects: {e}")
            return 0
    
    def get_by_name_and_grade(self, subject_name: str, grade_id: int) -> Optional[Dict[str, Any]]:
        """Ders adı ve sınıf ID'sine göre ders getirir"""
        try:
            query = "SELECT * FROM subjects WHERE subject_name = %s AND grade_id = %s"
            return self.fetch_one(query, (subject_name, grade_id))
        except Exception as e:
            print(f"Error getting subject by name and grade: {e}")
            return None
    
    def get_with_unit_count(self) -> List[Dict[str, Any]]:
        """Dersleri ünite sayılarıyla birlikte getirir"""
        try:
            query = """
                SELECT s.*, g.grade_name, COUNT(u.unit_id) as unit_count
                FROM subjects s
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                LEFT JOIN units u ON s.subject_id = u.subject_id
                GROUP BY s.subject_id
                ORDER BY s.subject_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting subjects with unit count: {e}")
            return []
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """Arama terimine göre ders arar"""
        try:
            query = """
                SELECT s.*, g.grade_name
                FROM subjects s
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                WHERE s.subject_name LIKE %s OR s.description LIKE %s OR g.grade_name LIKE %s
                ORDER BY s.subject_name ASC
            """
            search_pattern = f"%{search_term}%"
            return self.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        except Exception as e:
            print(f"Error searching subjects: {e}")
            return []
    
    def get_active_subjects(self) -> List[Dict[str, Any]]:
        """Sadece aktif dersleri getirir"""
        try:
            query = """
                SELECT s.*, g.grade_name
                FROM subjects s
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                WHERE s.is_active = 1
                ORDER BY s.subject_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting active subjects: {e}")
            return []
    
    def bulk_update_status(self, subject_ids: List[int], is_active: bool) -> bool:
        """Birden fazla dersin durumunu toplu günceller"""
        try:
            if not subject_ids:
                return True
            
            placeholders = ','.join(['%s'] * len(subject_ids))
            query = f"""
                UPDATE subjects 
                SET is_active = %s, updated_at = NOW()
                WHERE subject_id IN ({placeholders})
            """
            
            params = [is_active] + subject_ids
            return self.execute_query(query, tuple(params)) > 0
            
        except Exception as e:
            print(f"Error bulk updating subject status: {e}")
            return False
    
    def get_subjects_by_grade_range(self, min_grade: int, max_grade: int) -> List[Dict[str, Any]]:
        """Sınıf aralığına göre dersleri getirir"""
        try:
            query = """
                SELECT s.*, g.grade_name
                FROM subjects s
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                WHERE g.grade_level BETWEEN %s AND %s
                ORDER BY s.subject_name ASC
            """
            return self.fetch_all(query, (min_grade, max_grade))
        except Exception as e:
            print(f"Error getting subjects by grade range: {e}")
            return []
