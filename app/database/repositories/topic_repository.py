"""
Topic Repository - Topic Management
Handles all database operations for topics
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository

class TopicRepository(BaseRepository):
    """Konuları yöneten repository"""
    
    def __init__(self):
        """Topic repository'yi başlatır"""
        super().__init__()
        self.table_name = 'topics'
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm konuları getirir"""
        try:
            query = """
                SELECT * FROM topics 
                ORDER BY unit_id ASC, topic_number ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting all topics: {e}")
            return []
    
    def get_all_with_unit(self) -> List[Dict[str, Any]]:
        """Tüm konuları ünite bilgileriyle birlikte getirir"""
        try:
            query = """
                SELECT t.*, u.unit_name, s.subject_name, g.grade_name
                FROM topics t
                LEFT JOIN units u ON t.unit_id = u.unit_id
                LEFT JOIN subjects s ON u.subject_id = s.subject_id
                LEFT JOIN grades g ON s.grade_id = g.grade_id
                ORDER BY s.subject_name ASC, u.unit_number ASC, t.topic_number ASC
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"Error getting topics with unit: {e}")
            return []
    
    def get_by_id(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre konu getirir"""
        try:
            query = "SELECT * FROM topics WHERE topic_id = %s"
            return self.fetch_one(query, (topic_id,))
        except Exception as e:
            print(f"Error getting topic by ID: {e}")
            return None
    
    def get_by_unit(self, unit_id: int) -> List[Dict[str, Any]]:
        """Üniteye göre konuları getirir"""
        try:
            query = """
                SELECT * FROM topics 
                WHERE unit_id = %s
                ORDER BY topic_number ASC
            """
            return self.fetch_all(query, (unit_id,))
        except Exception as e:
            print(f"Error getting topics by unit: {e}")
            return []
    
    def get_by_number_and_unit(self, topic_number: int, unit_id: int) -> Optional[Dict[str, Any]]:
        """Numara ve üniteye göre konu getirir"""
        try:
            query = "SELECT * FROM topics WHERE topic_number = %s AND unit_id = %s"
            return self.fetch_one(query, (topic_number, unit_id))
        except Exception as e:
            print(f"Error getting topic by number and unit: {e}")
            return None
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Yeni konu oluşturur"""
        try:
            query = """
                INSERT INTO topics (topic_name, topic_number, unit_id, description, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            params = (
                data.get('topic_name'),
                data.get('topic_number'),
                data.get('unit_id'),
                data.get('description', ''),
                data.get('is_active', True)
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating topic: {e}")
            return None
    
    def update(self, topic_id: int, data: Dict[str, Any]) -> bool:
        """Konu bilgilerini günceller"""
        try:
            query = """
                UPDATE topics 
                SET topic_name = %s, topic_number = %s, unit_id = %s, 
                    description = %s, is_active = %s, updated_at = NOW()
                WHERE topic_id = %s
            """
            
            params = (
                data.get('topic_name'),
                data.get('topic_number'),
                data.get('unit_id'),
                data.get('description', ''),
                data.get('is_active', True),
                topic_id
            )
            
            return self.execute_query(query, params) > 0
            
        except Exception as e:
            print(f"Error updating topic: {e}")
            return False
    
    def delete(self, topic_id: int) -> bool:
        """Konuyu siler"""
        try:
            query = "DELETE FROM topics WHERE topic_id = %s"
            return self.execute_query(query, (topic_id,)) > 0
        except Exception as e:
            print(f"Error deleting topic: {e}")
            return False
    
    def count_all(self) -> int:
        """Toplam konu sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM topics"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting topics: {e}")
            return 0
    
    def count_by_unit(self, unit_id: int) -> int:
        """Belirli ünitedeki konu sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM topics WHERE unit_id = %s"
            result = self.fetch_one(query, (unit_id,))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting topics by unit: {e}")
            return 0
    
    def count_active(self) -> int:
        """Aktif konu sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM topics WHERE is_active = 1"
            result = self.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting active topics: {e}")
            return 0
