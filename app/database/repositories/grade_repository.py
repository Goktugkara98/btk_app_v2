"""
Grade Repository - Grade Management
Handles all database operations for grades
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository

class GradeRepository(BaseRepository):
    """Sınıfları yöneten repository"""
    
    def __init__(self):
        """Grade repository'yi başlatır"""
        super().__init__()
        self.table_name = 'grades'
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm sınıfları getirir"""
        try:
            query = """
                SELECT * FROM grades 
                ORDER BY grade_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting all grades: {e}")
            return []
    
    def get_by_id(self, grade_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre sınıf getirir"""
        try:
            query = "SELECT * FROM grades WHERE grade_id = %s"
            return self.fetch_one(query, (grade_id,))
        except Exception as e:
            print(f"Error getting grade by ID: {e}")
            return None
    
    def get_by_name(self, grade_name: str) -> Optional[Dict[str, Any]]:
        """İsme göre sınıf getirir"""
        try:
            query = "SELECT * FROM grades WHERE grade_name = %s"
            return self.fetch_one(query, (grade_name,))
        except Exception as e:
            print(f"Error getting grade by name: {e}")
            return None
    
    def get_by_level(self, grade_level: int) -> Optional[Dict[str, Any]]:
        """Seviyeye göre sınıf getirir"""
        try:
            query = "SELECT * FROM grades WHERE grade_level = %s"
            return self.fetch_one(query, (grade_level,))
        except Exception as e:
            print(f"Error getting grade by level: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Yeni sınıf oluşturur"""
        try:
            query = """
                INSERT INTO grades (grade_name, grade_level, description, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            
            params = (
                data.get('grade_name'),
                data.get('grade_level'),
                data.get('description', ''),
                data.get('is_active', True)
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating grade: {e}")
            return None
    
    def update(self, grade_id: int, data: Dict[str, Any]) -> bool:
        """Sınıf bilgilerini günceller"""
        try:
            query = """
                UPDATE grades 
                SET grade_name = %s, grade_level = %s, description = %s, 
                    is_active = %s, updated_at = NOW()
                WHERE grade_id = %s
            """
            
            params = (
                data.get('grade_name'),
                data.get('grade_level'),
                data.get('description', ''),
                data.get('is_active', True),
                grade_id
            )
            
            return self.execute_query(query, params) > 0
            
        except Exception as e:
            print(f"Error updating grade: {e}")
            return False
    
    def delete(self, grade_id: int) -> bool:
        """Sınıfı siler"""
        try:
            query = "DELETE FROM grades WHERE id = %s"
            return self.execute_query(query, (grade_id,)) > 0
        except Exception as e:
            print(f"Error deleting grade: {e}")
            return False
    
    def count_all(self) -> int:
        """Toplam sınıf sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM grades"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting grades: {e}")
            return 0
    
    def count_active(self) -> int:
        """Aktif sınıf sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM grades WHERE is_active = 1"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting active grades: {e}")
            return 0
    
    def get_with_subject_count(self) -> List[Dict[str, Any]]:
        """Sınıfları ders sayılarıyla birlikte getirir"""
        try:
            query = """
                SELECT g.*, COUNT(s.id) as subject_count
                FROM grades g
                LEFT JOIN subjects s ON g.id = s.grade_id
                GROUP BY g.id
                ORDER BY g.grade_level ASC, g.grade_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting grades with subject count: {e}")
            return []
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """Arama terimine göre sınıf arar"""
        try:
            query = """
                SELECT * FROM grades 
                WHERE grade_name LIKE %s OR description LIKE %s
                ORDER BY grade_level ASC, grade_name ASC
            """
            search_pattern = f"%{search_term}%"
            return self.fetch_all(query, (search_pattern, search_pattern))
        except Exception as e:
            print(f"Error searching grades: {e}")
            return []
    
    def get_active_grades(self) -> List[Dict[str, Any]]:
        """Sadece aktif sınıfları getirir"""
        try:
            query = """
                SELECT * FROM grades 
                WHERE is_active = 1
                ORDER BY grade_level ASC, grade_name ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting active grades: {e}")
            return []
    
    def bulk_update_status(self, grade_ids: List[int], is_active: bool) -> bool:
        """Birden fazla sınıfın durumunu toplu günceller"""
        try:
            if not grade_ids:
                return True
            
            placeholders = ','.join(['%s'] * len(grade_ids))
            query = f"""
                UPDATE grades 
                SET is_active = %s, updated_at = NOW()
                WHERE id IN ({placeholders})
            """
            
            params = [is_active] + grade_ids
            return self.execute_query(query, tuple(params)) > 0
            
        except Exception as e:
            print(f"Error bulk updating grade status: {e}")
            return False
