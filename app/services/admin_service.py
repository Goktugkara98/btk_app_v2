# =============================================================================
# ADMIN SERVICE
# =============================================================================
# Admin paneli için iş mantığı servisi
# Sadece müfredat yönetimi için gerekli metodlar
# =============================================================================

from typing import Dict, List, Any, Optional
from app.services.curriculum_service import CurriculumService
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Admin paneli için iş mantığı servisi"""
    
    def __init__(self):
        self.curriculum_service = CurriculumService()
    
    def get_curriculum_overview(self) -> Dict[str, Any]:
        """Müfredat genel bakış verilerini getirir"""
        try:
            # Curriculum service'den istatistikleri al
            stats = self.curriculum_service.get_curriculum_statistics()
            
            return {
                'total_grades': stats.get('total_grades', 0),
                'total_subjects': stats.get('total_subjects', 0),
                'total_units': stats.get('total_units', 0),
                'total_topics': stats.get('total_topics', 0)
            }
        except Exception as e:
            logger.error(f"Curriculum overview error: {str(e)}")
            return self._get_default_curriculum_overview()
    
    def _get_default_curriculum_overview(self) -> Dict[str, Any]:
        """Varsayılan müfredat genel bakış"""
        return {
            'total_grades': 0,
            'total_subjects': 0,
            'total_units': 0,
            'total_topics': 0
        }
