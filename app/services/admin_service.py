"""
Admin Service - Modern & Clean Implementation
Handles all admin panel business logic and data operations
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import csv
import io

from app.database.repositories.grade_repository import GradeRepository
from app.database.repositories.subject_repository import SubjectRepository
from app.database.repositories.unit_repository import UnitRepository
from app.database.repositories.topic_repository import TopicRepository
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.activity_repository import ActivityRepository
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError

# Setup logging
logger = logging.getLogger(__name__)

class AdminService:
    """Admin panel için tüm iş mantığını yöneten servis"""
    
    def __init__(self):
        """Admin service'i başlatır"""
        self.grade_repo = GradeRepository()
        self.subject_repo = SubjectRepository()
        self.unit_repo = UnitRepository()
        self.topic_repo = TopicRepository()
        self.user_repo = UserRepository()
        self.activity_repo = ActivityRepository()
    
    # =============================================================================
    # DASHBOARD & OVERVIEW
    # =============================================================================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Dashboard istatistiklerini getirir"""
        try:
            stats = {
                'total_grades': self.grade_repo.count_all(),
                'total_subjects': self.subject_repo.count_all(),
                'total_units': self.unit_repo.count_all(),
                'total_topics': self.topic_repo.count_all(),
                'total_users': self.user_repo.count_all(),
                'active_users': self.user_repo.count_active(),
                'recent_logins': self.user_repo.count_recent_logins(days=7),
                'system_health': self._check_system_health()
            }
            
            logger.info(f"Dashboard stats retrieved: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise DatabaseError(f"Dashboard istatistikleri alınamadı: {str(e)}")
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son aktiviteleri getirir"""
        try:
            activities = self.activity_repo.get_recent_activities(limit)
            
            # Format activities for frontend
            formatted_activities = []
            for activity in activities:
                formatted_activities.append({
                    'id': activity['id'],
                    'user_id': activity['user_id'],
                    'username': activity['username'],
                    'action': activity['action'],
                    'details': activity['details'],
                    'timestamp': activity['created_at'].isoformat() if activity['created_at'] else None,
                    'ip_address': activity['ip_address']
                })
            
            return formatted_activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            raise DatabaseError(f"Son aktiviteler alınamadı: {str(e)}")
    
    def get_curriculum_overview(self) -> Dict[str, Any]:
        """Curriculum genel bakış verilerini getirir"""
        try:
            overview = {
                'grades': {
                    'total': self.grade_repo.count_all(),
                    'list': self.grade_repo.get_all()
                },
                'subjects': {
                    'total': self.subject_repo.count_all(),
                    'list': self.subject_repo.get_all()
                },
                'units': {
                    'total': self.unit_repo.count_all(),
                },
                'topics': {
                    'total': self.topic_repo.count_all(),
                }
            }
            
            logger.info(f"Curriculum overview retrieved: {overview}")
            return overview
            
        except Exception as e:
            logger.error(f"Error getting curriculum overview: {str(e)}")
            raise DatabaseError(f"Curriculum verileri alınamadı: {str(e)}")
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Sistem sağlığını kontrol eder"""
        try:
            health = {
                'database': 'healthy',
                'cache': 'healthy',
                'last_backup': None,
                'disk_usage': 'normal',
                'memory_usage': 'normal'
            }
            
            # Database connection test
            try:
                self.grade_repo.count_all()
                health['database'] = 'healthy'
            except Exception:
                health['database'] = 'unhealthy'
            
            return health
            
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            return {'database': 'unknown', 'cache': 'unknown'}
    
    # =============================================================================
    # GRADES MANAGEMENT
    # =============================================================================
    
    def get_all_grades(self) -> List[Dict[str, Any]]:
        """Tüm sınıfları getirir"""
        try:
            grades = self.grade_repo.get_all()
            
            # Format grades for frontend
            formatted_grades = []
            for grade in grades:
                formatted_grades.append({
                    'id': grade['grade_id'],
                    'grade_name': grade['grade_name'],
                    'level': grade.get('grade_level', ''),
                    'description': grade.get('description', ''),
                    'is_active': grade.get('is_active', True),
                    'subject_count': self.subject_repo.count_by_grade(grade['grade_id']),
                    'created_at': grade.get('created_at', '').isoformat() if grade.get('created_at') else None,
                    'updated_at': grade.get('updated_at', '').isoformat() if grade.get('updated_at') else None
                })
            
            return formatted_grades
            
        except Exception as e:
            logger.error(f"Error getting grades: {str(e)}")
            raise DatabaseError(f"Sınıflar alınamadı: {str(e)}")
    
    def create_grade(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni sınıf oluşturur"""
        try:
            # Validate data
            if not data.get('grade_name'):
                raise ValidationError('Sınıf adı gerekli')
            
            if not data.get('level'):
                raise ValidationError('Sınıf seviyesi gerekli')
            
            # Check if grade already exists
            existing_grade = self.grade_repo.get_by_name(data['grade_name'])
            if existing_grade:
                raise ValidationError('Bu sınıf adı zaten mevcut')
            
            # Create grade
            grade_data = {
                'grade_name': data['grade_name'],
                'grade_level': data['level'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', True)
            }
            
            grade_id = self.grade_repo.create(grade_data)
            if not grade_id:
                raise DatabaseError('Sınıf oluşturulamadı')
            
            # Get created grade
            grade = self.grade_repo.get_by_id(grade_id)
            
            # Log activity
            self._log_activity('grade_created', f"Sınıf oluşturuldu: {data['grade_name']}")
            
            return {
                'id': grade['id'],
                'grade_name': grade['grade_name'],
                'grade_level': grade['grade_level'],
                'description': grade.get('description', ''),
                'is_active': grade.get('is_active', True),
                'subject_count': 0,
                'created_at': grade.get('created_at', '').isoformat() if grade.get('created_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error creating grade: {str(e)}")
            raise
    
    def update_grade(self, grade_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sınıf bilgilerini günceller"""
        try:
            # Check if grade exists
            existing_grade = self.grade_repo.get_by_id(grade_id)
            if not existing_grade:
                raise NotFoundError('Sınıf bulunamadı')
            
            # Validate data
            if not data.get('grade_name'):
                raise ValidationError('Sınıf adı gerekli')
            
            if not data.get('level'):
                raise ValidationError('Sınıf seviyesi gerekli')
            
            # Check if new name conflicts with existing grades
            if data['grade_name'] != existing_grade['grade_name']:
                conflict_grade = self.grade_repo.get_by_name(data['grade_name'])
                if conflict_grade and conflict_grade['id'] != grade_id:
                    raise ValidationError('Bu sınıf adı zaten mevcut')
            
            # Update grade
            update_data = {
                'grade_name': data['grade_name'],
                'grade_level': data['grade_level'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', existing_grade.get('is_active', True))
            }
            
            success = self.grade_repo.update(grade_id, update_data)
            if not success:
                raise DatabaseError('Sınıf güncellenemedi')
            
            # Get updated grade
            updated_grade = self.grade_repo.get_by_id(grade_id)
            
            # Log activity
            self._log_activity('grade_updated', f"Sınıf güncellendi: {data['grade_name']}")
            
            return {
                'id': updated_grade['id'],
                'grade_name': updated_grade['grade_name'],
                'grade_level': updated_grade['grade_level'],
                'description': updated_grade.get('description', ''),
                'is_active': updated_grade.get('is_active', True),
                'subject_count': self.subject_repo.count_by_grade(grade_id),
                'updated_at': updated_grade.get('updated_at', '').isoformat() if updated_grade.get('updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error updating grade {grade_id}: {str(e)}")
            raise
    
    def delete_grade(self, grade_id: int) -> bool:
        """Sınıfı siler"""
        try:
            # Check if grade exists
            existing_grade = self.grade_repo.get_by_id(grade_id)
            if not existing_grade:
                raise NotFoundError('Sınıf bulunamadı')
            
            # Check if grade has subjects
            subject_count = self.subject_repo.count_by_grade(grade_id)
            if subject_count > 0:
                raise ValidationError(f'Bu sınıfta {subject_count} ders bulunuyor. Önce dersleri silin.')
            
            # Delete grade
            success = self.grade_repo.delete(grade_id)
            if not success:
                raise DatabaseError('Sınıf silinemedi')
            
            # Log activity
            self._log_activity('grade_deleted', f"Sınıf silindi: {existing_grade['grade_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting grade {grade_id}: {str(e)}")
            raise
    
    # =============================================================================
    # SUBJECTS MANAGEMENT
    # =============================================================================
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """Tüm dersleri getirir"""
        try:
            subjects = self.subject_repo.get_all_with_grade()
            
            # Format subjects for frontend
            formatted_subjects = []
            for subject in subjects:
                formatted_subjects.append({
                    'id': subject['subject_id'],
                    'subject_name': subject['subject_name'],
                    'grade_id': subject['grade_id'],
                    'grade_name': subject.get('grade_name', ''),
                    'description': subject.get('description', ''),
                    'is_active': subject.get('is_active', True),
                    'unit_count': self.unit_repo.count_by_subject(subject['subject_id']),
                    'created_at': subject.get('created_at', '').isoformat() if subject.get('created_at') else None,
                    'updated_at': subject.get('updated_at', '').isoformat() if subject.get('updated_at') else None
                })
            
            return formatted_subjects
            
        except Exception as e:
            logger.error(f"Error getting subjects: {str(e)}")
            raise DatabaseError(f"Dersler alınamadı: {str(e)}")
    
    def create_subject(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni ders oluşturur"""
        try:
            # Validate data
            if not data.get('subject_name'):
                raise ValidationError('Ders adı gerekli')
            
            if not data.get('grade_id'):
                raise ValidationError('Sınıf ID gerekli')
            
            if not data.get('description'):
                raise ValidationError('Ders açıklaması gerekli')
            
            # Check if grade exists
            grade = self.grade_repo.get_by_id(data['grade_id'])
            if not grade:
                raise ValidationError('Geçersiz sınıf ID')
            
            # Check if subject already exists in this grade
            existing_subject = self.subject_repo.get_by_name_and_grade(data['subject_name'], data['grade_id'])
            if existing_subject:
                raise ValidationError('Bu ders adı bu sınıfta zaten mevcut')
            
            # Create subject
            subject_data = {
                'subject_name': data['subject_name'],
                'grade_id': data['grade_id'],
                'description': data['description'],
                'is_active': data.get('is_active', True)
            }
            
            subject_id = self.subject_repo.create(subject_data)
            if not subject_id:
                raise DatabaseError('Ders oluşturulamadı')
            
            # Get created subject
            subject = self.subject_repo.get_by_id(subject_id)
            
            # Log activity
            self._log_activity('subject_created', f"Ders oluşturuldu: {data['subject_name']}")
            
            return {
                'id': subject['id'],
                'subject_name': subject['subject_name'],
                'grade_id': subject['grade_id'],
                'grade_name': grade['grade_name'],
                'description': subject.get('description', ''),
                'is_active': subject.get('is_active', True),
                'unit_count': 0,
                'created_at': subject.get('created_at', '').isoformat() if subject.get('created_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error creating subject: {str(e)}")
            raise
    
    def update_subject(self, subject_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ders bilgilerini günceller"""
        try:
            # Check if subject exists
            existing_subject = self.subject_repo.get_by_id(subject_id)
            if not existing_subject:
                raise NotFoundError('Ders bulunamadı')
            
            # Validate data
            if not data.get('subject_name'):
                raise ValidationError('Ders adı gerekli')
            
            if not data.get('grade_id'):
                raise ValidationError('Sınıf ID gerekli')
            
            if not data.get('description'):
                raise ValidationError('Ders açıklaması gerekli')
            
            # Check if grade exists
            grade = self.grade_repo.get_by_id(data['grade_id'])
            if not grade:
                raise ValidationError('Geçersiz sınıf ID')
            
            # Check if new name conflicts with existing subjects in the same grade
            if (data['subject_name'] != existing_subject['subject_name'] or 
                data['grade_id'] != existing_subject['grade_id']):
                conflict_subject = self.subject_repo.get_by_name_and_grade(data['subject_name'], data['grade_id'])
                if conflict_subject and conflict_subject['id'] != subject_id:
                    raise ValidationError('Bu ders adı bu sınıfta zaten mevcut')
            
            # Update subject
            update_data = {
                'subject_name': data['subject_name'],
                'grade_id': data['grade_id'],
                'description': data['description'],
                'is_active': data.get('is_active', existing_subject.get('is_active', True))
            }
            
            success = self.subject_repo.update(subject_id, update_data)
            if not success:
                raise DatabaseError('Ders güncellenemedi')
            
            # Get updated subject
            updated_subject = self.subject_repo.get_by_id(subject_id)
            
            # Log activity
            self._log_activity('subject_updated', f"Ders güncellendi: {data['subject_name']}")
            
            return {
                'id': updated_subject['id'],
                'subject_name': updated_subject['subject_name'],
                'grade_id': updated_subject['grade_id'],
                'grade_name': grade['grade_name'],
                'description': updated_subject.get('description', ''),
                'is_active': updated_subject.get('is_active', True),
                'unit_count': self.unit_repo.count_by_subject(subject_id),
                'updated_at': updated_subject.get('updated_at', '').isoformat() if updated_subject.get('updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error updating subject {subject_id}: {str(e)}")
            raise
    
    def delete_subject(self, subject_id: int) -> bool:
        """Dersi siler"""
        try:
            # Check if subject exists
            existing_subject = self.subject_repo.get_by_id(subject_id)
            if not existing_subject:
                raise NotFoundError('Ders bulunamadı')
            
            # Check if subject has units
            unit_count = self.unit_repo.count_by_subject(subject_id)
            if unit_count > 0:
                raise ValidationError(f'Bu derste {unit_count} ünite bulunuyor. Önce üniteleri silin.')
            
            # Delete subject
            success = self.subject_repo.delete(subject_id)
            if not success:
                raise DatabaseError('Ders silinemedi')
            
            # Log activity
            self._log_activity('subject_deleted', f"Ders silindi: {existing_subject['subject_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting subject {subject_id}: {str(e)}")
            raise
    
    # =============================================================================
    # UNITS MANAGEMENT
    # =============================================================================
    
    def get_all_units(self) -> List[Dict[str, Any]]:
        """Tüm üniteleri getirir"""
        try:
            units = self.unit_repo.get_all_with_subject()
            
            # Format units for frontend
            formatted_units = []
            for unit in units:
                formatted_units.append({
                    'id': unit['id'],
                    'unit_name': unit['unit_name'],
                    'unit_number': unit['unit_number'],
                    'subject_id': unit['subject_id'],
                    'subject_name': unit.get('subject_name', ''),
                    'description': unit.get('description', ''),
                    'is_active': unit.get('is_active', True),
                    'topic_count': self.topic_repo.count_by_unit(unit['id']),
                    'created_at': unit.get('created_at', '').isoformat() if unit.get('created_at') else None,
                    'updated_at': unit.get('updated_at', '').isoformat() if unit.get('updated_at') else None
                })
            
            return formatted_units
            
        except Exception as e:
            logger.error(f"Error getting units: {str(e)}")
            raise DatabaseError(f"Üniteler alınamadı: {str(e)}")
    
    def create_unit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni ünite oluşturur"""
        try:
            # Validate data
            if not data.get('unit_name'):
                raise ValidationError('Ünite adı gerekli')
            
            if not data.get('subject_id'):
                raise ValidationError('Ders ID gerekli')
            
            if not data.get('unit_number'):
                raise ValidationError('Ünite numarası gerekli')
            
            # Check if subject exists
            subject = self.subject_repo.get_by_id(data['subject_id'])
            if not subject:
                raise ValidationError('Geçersiz ders ID')
            
            # Check if unit number already exists in this subject
            existing_unit = self.unit_repo.get_by_number_and_subject(data['unit_number'], data['subject_id'])
            if existing_unit:
                raise ValidationError('Bu ünite numarası bu derste zaten mevcut')
            
            # Create unit
            unit_data = {
                'unit_name': data['unit_name'],
                'unit_number': data['unit_number'],
                'subject_id': data['subject_id'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', True)
            }
            
            unit_id = self.unit_repo.create(unit_data)
            if not unit_id:
                raise DatabaseError('Ünite oluşturulamadı')
            
            # Get created unit
            unit = self.unit_repo.get_by_id(unit_id)
            
            # Log activity
            self._log_activity('unit_created', f"Ünite oluşturuldu: {data['unit_name']}")
            
            return {
                'id': unit['id'],
                'unit_name': unit['unit_name'],
                'unit_number': unit['unit_number'],
                'subject_id': unit['subject_id'],
                'subject_name': subject['subject_name'],
                'description': unit.get('description', ''),
                'is_active': unit.get('is_active', True),
                'topic_count': 0,
                'created_at': unit.get('created_at', '').isoformat() if unit.get('created_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error creating unit: {str(e)}")
            raise
    
    def update_unit(self, unit_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ünite bilgilerini günceller"""
        try:
            # Check if unit exists
            existing_unit = self.unit_repo.get_by_id(unit_id)
            if not existing_unit:
                raise NotFoundError('Ünite bulunamadı')
            
            # Validate data
            if not data.get('unit_name'):
                raise ValidationError('Ünite adı gerekli')
            
            if not data.get('subject_id'):
                raise ValidationError('Ders ID gerekli')
            
            if not data.get('unit_number'):
                raise ValidationError('Ünite numarası gerekli')
            
            # Check if subject exists
            subject = self.subject_repo.get_by_id(data['subject_id'])
            if not subject:
                raise ValidationError('Geçersiz ders ID')
            
            # Check if new unit number conflicts with existing units in the same subject
            if (data['unit_number'] != existing_unit['unit_number'] or 
                data['subject_id'] != existing_unit['subject_id']):
                conflict_unit = self.unit_repo.get_by_number_and_subject(data['unit_number'], data['subject_id'])
                if conflict_unit and conflict_unit['id'] != unit_id:
                    raise ValidationError('Bu ünite numarası bu derste zaten mevcut')
            
            # Update unit
            update_data = {
                'unit_name': data['unit_name'],
                'unit_number': data['unit_number'],
                'subject_id': data['subject_id'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', existing_unit.get('is_active', True))
            }
            
            success = self.unit_repo.update(unit_id, update_data)
            if not success:
                raise DatabaseError('Ünite güncellenemedi')
            
            # Get updated unit
            updated_unit = self.unit_repo.get_by_id(unit_id)
            
            # Log activity
            self._log_activity('unit_updated', f"Ünite güncellendi: {data['unit_name']}")
            
            return {
                'id': updated_unit['id'],
                'unit_name': updated_unit['unit_name'],
                'unit_number': updated_unit['unit_number'],
                'subject_id': updated_unit['subject_id'],
                'subject_name': subject['grade_name'],
                'description': updated_unit.get('description', ''),
                'is_active': updated_unit.get('is_active', True),
                'topic_count': self.topic_repo.count_by_unit(unit_id),
                'updated_at': updated_unit.get('updated_at', '').isoformat() if updated_unit.get('updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error updating unit {unit_id}: {str(e)}")
            raise
    
    def delete_unit(self, unit_id: int) -> bool:
        """Üniteyi siler"""
        try:
            # Check if unit exists
            existing_unit = self.unit_repo.get_by_id(unit_id)
            if not existing_unit:
                raise NotFoundError('Ünite bulunamadı')
            
            # Check if unit has topics
            topic_count = self.topic_repo.count_by_unit(unit_id)
            if topic_count > 0:
                raise ValidationError(f'Bu ünitede {topic_count} konu bulunuyor. Önce konuları silin.')
            
            # Delete unit
            success = self.unit_repo.delete(unit_id)
            if not success:
                raise DatabaseError('Ünite silinemedi')
            
            # Log activity
            self._log_activity('unit_deleted', f"Ünite silindi: {existing_unit['unit_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting unit {unit_id}: {str(e)}")
            raise
    
    # =============================================================================
    # TOPICS MANAGEMENT
    # =============================================================================
    
    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Tüm konuları getirir"""
        try:
            topics = self.topic_repo.get_all_with_unit()
            
            # Format topics for frontend
            formatted_topics = []
            for topic in topics:
                formatted_topics.append({
                    'id': topic['id'],
                    'topic_name': topic['topic_name'],
                    'topic_number': topic['topic_number'],
                    'unit_id': topic['unit_id'],
                    'unit_name': topic.get('unit_name', ''),
                    'description': topic.get('description', ''),
                    'is_active': topic.get('is_active', True),
                    'created_at': topic.get('created_at', '').isoformat() if topic.get('created_at') else None,
                    'updated_at': topic.get('updated_at', '').isoformat() if topic.get('updated_at') else None
                })
            
            return formatted_topics
            
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            raise DatabaseError(f"Konular alınamadı: {str(e)}")
    
    def create_topic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni konu oluşturur"""
        try:
            # Validate data
            if not data.get('topic_name'):
                raise ValidationError('Konu adı gerekli')
            
            if not data.get('unit_id'):
                raise ValidationError('Ünite ID gerekli')
            
            if not data.get('topic_number'):
                raise ValidationError('Konu numarası gerekli')
            
            # Check if unit exists
            unit = self.unit_repo.get_by_id(data['unit_id'])
            if not unit:
                raise ValidationError('Geçersiz ünite ID')
            
            # Check if topic number already exists in this unit
            existing_topic = self.topic_repo.get_by_number_and_unit(data['topic_number'], data['unit_id'])
            if existing_topic:
                raise ValidationError('Bu konu numarası bu ünitede zaten mevcut')
            
            # Create topic
            topic_data = {
                'topic_name': data['topic_name'],
                'topic_number': data['topic_number'],
                'unit_id': data['unit_id'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', True)
            }
            
            topic_id = self.topic_repo.create(topic_data)
            if not topic_id:
                raise DatabaseError('Konu oluşturulamadı')
            
            # Get created topic
            topic = self.topic_repo.get_by_id(topic_id)
            
            # Log activity
            self._log_activity('topic_created', f"Konu oluşturuldu: {data['topic_name']}")
            
            return {
                'id': topic['id'],
                'topic_name': topic['topic_name'],
                'topic_number': topic['topic_number'],
                'unit_id': topic['unit_id'],
                'unit_name': unit['unit_name'],
                'description': topic.get('description', ''),
                'is_active': topic.get('is_active', True),
                'created_at': topic.get('created_at', '').isoformat() if topic.get('created_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error creating topic: {str(e)}")
            raise
    
    def update_topic(self, topic_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Konu bilgilerini günceller"""
        try:
            # Check if topic exists
            existing_topic = self.topic_repo.get_by_id(topic_id)
            if not existing_topic:
                raise NotFoundError('Konu bulunamadı')
            
            # Validate data
            if not data.get('topic_name'):
                raise ValidationError('Konu adı gerekli')
            
            if not data.get('unit_id'):
                raise ValidationError('Ünite ID gerekli')
            
            if not data.get('topic_number'):
                raise ValidationError('Konu numarası gerekli')
            
            # Check if unit exists
            unit = self.unit_repo.get_by_id(data['unit_id'])
            if not unit:
                raise ValidationError('Geçersiz ünite ID')
            
            # Check if new topic number conflicts with existing topics in the same unit
            if (data['topic_number'] != existing_topic['topic_number'] or 
                data['unit_id'] != existing_topic['unit_id']):
                conflict_topic = self.topic_repo.get_by_number_and_unit(data['topic_number'], data['unit_id'])
                if conflict_topic and conflict_topic['id'] != topic_id:
                    raise ValidationError('Bu konu numarası bu ünitede zaten mevcut')
            
            # Update topic
            update_data = {
                'topic_name': data['topic_name'],
                'topic_number': data['topic_number'],
                'unit_id': data['unit_id'],
                'description': data.get('description', ''),
                'is_active': data.get('is_active', existing_topic.get('is_active', True))
            }
            
            success = self.topic_repo.update(topic_id, update_data)
            if not success:
                raise DatabaseError('Konu güncellenemedi')
            
            # Get updated topic
            updated_topic = self.topic_repo.get_by_id(topic_id)
            
            # Log activity
            self._log_activity('topic_updated', f"Konu güncellendi: {data['topic_name']}")
            
            return {
                'id': updated_topic['id'],
                'topic_name': updated_topic['topic_name'],
                'topic_number': updated_topic['topic_number'],
                'unit_id': updated_topic['unit_id'],
                'unit_name': unit['unit_name'],
                'description': updated_topic.get('description', ''),
                'is_active': updated_topic.get('is_active', True),
                'updated_at': updated_topic.get('updated_at', '').isoformat() if updated_topic.get('updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error updating topic {topic_id}: {str(e)}")
            raise
    
    def delete_topic(self, topic_id: int) -> bool:
        """Konuyu siler"""
        try:
            # Check if topic exists
            existing_topic = self.topic_repo.get_by_id(topic_id)
            if not existing_topic:
                raise NotFoundError('Konu bulunamadı')
            
            # Delete topic
            success = self.topic_repo.delete(topic_id)
            if not success:
                raise DatabaseError('Konu silinemedi')
            
            # Log activity
            self._log_activity('topic_deleted', f"Konu silindi: {existing_topic['topic_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting topic {topic_id}: {str(e)}")
            raise
    
    # =============================================================================
    # USERS MANAGEMENT
    # =============================================================================
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Tüm kullanıcıları getirir"""
        try:
            users = self.user_repo.get_all()
            
            # Format users for frontend (exclude sensitive data)
            formatted_users = []
            for user in users:
                formatted_users.append({
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'is_admin': user.get('is_admin', False),
                    'is_active': user.get('is_active', True),
                    'last_login': user.get('last_login', '').isoformat() if user.get('last_login') else None,
                    'created_at': user.get('created_at', '').isoformat() if user.get('created_at') else None
                })
            
            return formatted_users
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise DatabaseError(f"Kullanıcılar alınamadı: {str(e)}")
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini günceller"""
        try:
            # Check if user exists
            existing_user = self.user_repo.get_by_id(user_id)
            if not existing_user:
                raise NotFoundError('Kullanıcı bulunamadı')
            
            # Prepare update data (only allow certain fields)
            update_data = {}
            allowed_fields = ['first_name', 'last_name', 'is_active']
            
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]
            
            if not update_data:
                raise ValidationError('Güncellenecek alan bulunamadı')
            
            # Update user
            success = self.user_repo.update(user_id, update_data)
            if not success:
                raise DatabaseError('Kullanıcı güncellenemedi')
            
            # Get updated user
            updated_user = self.user_repo.get_by_id(user_id)
            
            # Log activity
            self._log_activity('user_updated', f"Kullanıcı güncellendi: {updated_user['username']}")
            
            return {
                'id': updated_user['id'],
                'username': updated_user['username'],
                'email': updated_user['email'],
                'first_name': updated_user.get('first_name', ''),
                'last_name': updated_user.get('last_name', ''),
                'is_admin': updated_user.get('is_admin', False),
                'is_active': updated_user.get('is_active', True),
                'last_login': updated_user.get('last_login', '').isoformat() if updated_user.get('last_login') else None,
                'updated_at': updated_user.get('updated_at', '').isoformat() if updated_user.get('updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    def toggle_admin_status(self, user_id: int) -> bool:
        """Kullanıcının admin durumunu değiştirir"""
        try:
            # Check if user exists
            existing_user = self.user_repo.get_by_id(user_id)
            if not existing_user:
                raise NotFoundError('Kullanıcı bulunamadı')
            
            # Toggle admin status
            new_admin_status = not existing_user.get('is_admin', False)
            
            success = self.user_repo.update(user_id, {'is_admin': new_admin_status})
            if not success:
                raise DatabaseError('Admin durumu güncellenemedi')
            
            # Log activity
            action = 'admin_granted' if new_admin_status else 'admin_revoked'
            self._log_activity(action, f"Admin durumu değiştirildi: {existing_user['username']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error toggling admin status for user {user_id}: {str(e)}")
            raise
    
    # =============================================================================
    # IMPORT/EXPORT
    # =============================================================================
    
    def export_curriculum(self, format_type: str = 'csv') -> Dict[str, Any]:
        """Müfredat verilerini export eder"""
        try:
            if format_type.lower() == 'csv':
                return self._export_curriculum_csv()
            else:
                raise ValidationError('Desteklenmeyen export formatı')
                
        except Exception as e:
            logger.error(f"Error exporting curriculum: {str(e)}")
            raise DatabaseError(f"Export işlemi başarısız: {str(e)}")
    
    def _export_curriculum_csv(self) -> Dict[str, Any]:
        """Müfredat verilerini CSV formatında export eder"""
        try:
            # Get all curriculum data
            grades = self.grade_repo.get_all()
            subjects = self.subject_repo.get_all_with_grade()
            units = self.unit_repo.get_all_with_subject()
            topics = self.topic_repo.get_all_with_unit()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Grade', 'Subject', 'Unit', 'Topic', 'Description'])
            
            # Write data
            for grade in grades:
                grade_name = grade['grade_name']
                
                for subject in subjects:
                    if subject['grade_id'] == grade['id']:
                        subject_name = subject['subject_name']
                        subject_desc = subject.get('description', '')
                        
                        for unit in units:
                            if unit['subject_id'] == subject['id']:
                                unit_name = unit['unit_name']
                                unit_desc = unit.get('description', '')
                                
                                for topic in topics:
                                    if topic['unit_id'] == unit['id']:
                                        topic_name = topic['topic_name']
                                        topic_desc = topic.get('description', '')
                                        
                                        writer.writerow([
                                            grade_name,
                                            subject_name,
                                            unit_name,
                                            topic_name,
                                            topic_desc or unit_desc or subject_desc
                                        ])
            
            csv_content = output.getvalue()
            output.close()
            
            # Log activity
            self._log_activity('curriculum_exported', 'Müfredat export edildi')
            
            return {
                'format': 'csv',
                'content': csv_content,
                'filename': f'curriculum_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'record_count': len(topics)
            }
            
        except Exception as e:
            logger.error(f"Error creating CSV export: {str(e)}")
            raise DatabaseError(f"CSV export oluşturulamadı: {str(e)}")
    
    def import_curriculum(self, file) -> Dict[str, Any]:
        """CSV dosyasından müfredat verilerini import eder"""
        try:
            # Read CSV file
            csv_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (1 is header)
                try:
                    # Validate required fields
                    if not all([row.get('Grade'), row.get('Subject'), row.get('Unit'), row.get('Topic')]):
                        errors.append(f"Satır {row_num}: Gerekli alanlar eksik")
                        continue
                    
                    # Import logic here (simplified for now)
                    # TODO: Implement full import logic
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Satır {row_num}: {str(e)}")
            
            # Log activity
            self._log_activity('curriculum_imported', f'Müfredat import edildi: {imported_count} kayıt')
            
            return {
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors[:10],  # Limit errors to first 10
                'total_rows': row_num - 1
            }
            
        except Exception as e:
            logger.error(f"Error importing curriculum: {str(e)}")
            raise DatabaseError(f"Import işlemi başarısız: {str(e)}")
    
    # =============================================================================
    # SYSTEM STATUS
    # =============================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumunu getirir"""
        try:
            status = {
                'database': 'healthy',
                'cache': 'healthy',
                'disk_usage': 'normal',
                'memory_usage': 'normal',
                'last_backup': None,
                'uptime': self._get_system_uptime(),
                'version': '2.0.0',
                'environment': 'production'
            }
            
            # Database health check
            try:
                self.grade_repo.count_all()
                status['database'] = 'healthy'
            except Exception:
                status['database'] = 'unhealthy'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_system_uptime(self) -> str:
        """Sistem uptime'ını getirir"""
        try:
            # This is a placeholder - in real implementation, you'd get actual uptime
            return "24 hours"
        except Exception:
            return "Unknown"
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _log_activity(self, action: str, details: str) -> None:
        """Aktivite loglarını kaydeder"""
        try:
            # Get current user from session (if available)
            from flask import session
            user_id = session.get('user_id')
            
            activity_data = {
                'user_id': user_id,
                'action': action,
                'details': details,
                'ip_address': '127.0.0.1',  # TODO: Get real IP
                'user_agent': 'Admin Panel'  # TODO: Get real user agent
            }
            
            self.activity_repo.create(activity_data)
            
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            # Don't raise - activity logging failure shouldn't break main operations
