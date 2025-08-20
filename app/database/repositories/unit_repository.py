"""
Unit Repository - Unit Management
Handles all database operations for units
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository

class UnitRepository(BaseRepository):
    """Üniteleri yöneten repository"""
    
    def __init__(self):
        """Unit repository'yi başlatır"""
        super().__init__()
        self.table_name = 'units'
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm üniteleri getirir"""
        try:
            query = """
                SELECT * FROM units 
                ORDER BY subject_id ASC, unit_number ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting all units: {e}")
            return []
    
    def get_all_with_subject(self) -> List[Dict[str, Any]]:
        """Tüm üniteleri ders bilgileriyle birlikte getirir"""
        try:
            query = """
                SELECT u.*, s.subject_name, g.grade_name
                FROM units u
                LEFT JOIN subjects s ON u.subject_id = s.subject_id
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                ORDER BY s.subject_name ASC, u.unit_number ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting units with subject: {e}")
            return []
    
    def get_by_id(self, unit_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ünite getirir"""
        try:
            query = "SELECT * FROM units WHERE unit_id = %s"
            return self.fetch_one(query, (unit_id,))
        except Exception as e:
            print(f"Error getting unit by ID: {e}")
            return None
    
    def get_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """Derse göre üniteleri getirir"""
        try:
            query = """
                SELECT * FROM units 
                WHERE subject_id = %s
                ORDER BY unit_number ASC
            """
            return self.fetch_all(query, (subject_id,))
        except Exception as e:
            print(f"Error getting units by subject: {e}")
            return []
    
    def get_by_number_and_subject(self, unit_number: int, subject_id: int) -> Optional[Dict[str, Any]]:
        """Numara ve derse göre ünite getirir"""
        try:
            query = "SELECT * FROM units WHERE unit_number = %s AND subject_id = %s"
            return self.fetch_one(query, (unit_number, subject_id))
        except Exception as e:
            print(f"Error getting unit by number and subject: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Yeni ünite oluşturur"""
        try:
            query = """
                INSERT INTO units (unit_name, unit_number, subject_id, description, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            params = (
                data.get('unit_name'),
                data.get('unit_number'),
                data.get('subject_id'),
                data.get('description', ''),
                data.get('is_active', True)
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating unit: {e}")
            return None
    
    def update(self, unit_id: int, data: Dict[str, Any]) -> bool:
        """Ünite bilgilerini günceller"""
        try:
            query = """
                UPDATE units 
                SET unit_name = %s, unit_number = %s, subject_id = %s, 
                    description = %s, is_active = %s, updated_at = NOW()
                WHERE unit_id = %s
            """
            
            params = (
                data.get('unit_name'),
                data.get('unit_number'),
                data.get('subject_id'),
                data.get('description', ''),
                data.get('is_active', True),
                unit_id
            )
            
            return self.execute_query(query, params) > 0
            
        except Exception as e:
            print(f"Error updating unit: {e}")
            return False
    
    def delete(self, unit_id: int) -> bool:
        """Üniteyi siler"""
        try:
            query = "DELETE FROM units WHERE unit_id = %s"
            return self.execute_query(query, (unit_id,)) > 0
        except Exception as e:
            print(f"Error deleting unit: {e}")
            return False
    
    def count_all(self) -> int:
        """Toplam ünite sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM units"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting units: {e}")
            return 0
    
    def count_by_subject(self, subject_id: int) -> int:
        """Belirli dersteki ünite sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM units WHERE subject_id = %s"
            result = self.fetch_one(query, (subject_id,))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting units by subject: {e}")
            return 0
    
    def count_active(self) -> int:
        """Aktif ünite sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM units WHERE is_active = 1"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting active units: {e}")
            return 0
