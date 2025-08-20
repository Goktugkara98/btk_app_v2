"""
Activity Repository - User Activity Logging
Handles logging and retrieval of user activities for audit purposes
"""

from typing import List, Dict, Any, Optional
from app.database.repositories.base_repository import BaseRepository
from app.database.db_connection import DatabaseConnection

class ActivityRepository(BaseRepository):
    """Kullanıcı aktivitelerini yöneten repository"""
    
    def __init__(self):
        """Activity repository'yi başlatır"""
        super().__init__()
        self.table_name = 'user_activities'
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Yeni aktivite kaydı oluşturur"""
        try:
            query = """
                INSERT INTO user_activities (user_id, action, details, ip_address, user_agent, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            params = (
                data.get('user_id'),
                data.get('action'),
                data.get('details'),
                data.get('ip_address'),
                data.get('user_agent')
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"Error creating activity: {e}")
            return None
    
    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Belirli kullanıcının aktivitelerini getirir"""
        try:
            query = """
                SELECT a.*, u.username
                FROM user_activities a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            
            return self.fetch_all(query, (user_id, limit))
            
        except Exception as e:
            print(f"Error getting activities by user: {e}")
            return []
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son aktiviteleri getirir"""
        try:
            query = """
                SELECT a.*, u.username
                FROM user_activities a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            
            return self.fetch_all(query, (limit,))
            
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []
    
    def get_by_action(self, action: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Belirli aksiyona göre aktiviteleri getirir"""
        try:
            query = """
                SELECT a.*, u.username
                FROM user_activities a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.action = %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            
            return self.fetch_all(query, (action, limit))
            
        except Exception as e:
            print(f"Error getting activities by action: {e}")
            return []
    
    def get_by_date_range(self, start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Tarih aralığına göre aktiviteleri getirir"""
        try:
            query = """
                SELECT a.*, u.username
                FROM user_activities a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE DATE(a.created_at) BETWEEN %s AND %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            
            return self.fetch_all(query, (start_date, end_date, limit))
            
        except Exception as e:
            print(f"Error getting activities by date range: {e}")
            return []
    
    def count_by_user(self, user_id: int) -> int:
        """Kullanıcının toplam aktivite sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM user_activities WHERE user_id = %s"
            result = self.fetch_one(query, (user_id,))
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"Error counting activities by user: {e}")
            return 0
    
    def count_by_action(self, action: str) -> int:
        """Belirli aksiyonun toplam sayısını getirir"""
        try:
            query = "SELECT COUNT(*) as count FROM user_activities WHERE action = %s"
            result = self.fetch_one(query, (action,))
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"Error counting activities by action: {e}")
            return 0
    
    def cleanup_old_activities(self, days: int = 90) -> int:
        """Eski aktivite kayıtlarını temizler"""
        try:
            query = "DELETE FROM user_activities WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
            return self.execute_query(query, (days,))
            
        except Exception as e:
            print(f"Error cleaning up old activities: {e}")
            return 0
    
    def get_activity_summary(self, days: int = 30) -> Dict[str, Any]:
        """Aktivite özetini getirir"""
        try:
            query = """
                SELECT 
                    action,
                    COUNT(*) as count,
                    COUNT(DISTINCT user_id) as unique_users
                FROM user_activities 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY action
                ORDER BY count DESC
            """
            
            activities = self.fetch_all(query, (days,))
            
            summary = {
                'total_activities': sum(a['count'] for a in activities),
                'unique_users': len(set(a['user_id'] for a in activities if a['user_id'])),
                'actions': activities
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting activity summary: {e}")
            return {
                'total_activities': 0,
                'unique_users': 0,
                'actions': []
            }
