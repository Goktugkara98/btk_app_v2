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
        try:
            query = """
            SELECT grade_id, grade_name, description, is_active, 
                   created_at, updated_at
            FROM grades 
            ORDER BY grade_name
            """
            return self.base_repo.fetch_all(query)
        except Exception as e:
            print(f"Grades fetch error: {e}")
            return []
    
    def get_grade_by_id(self, grade_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre sınıf getirir"""
        try:
            query = "SELECT * FROM grades WHERE grade_id = %s"
            return self.base_repo.fetch_one(query, (grade_id,))
        except Exception as e:
            print(f"Grade fetch error: {e}")
            return None
    
    def create_grade(self, grade_name: str, description: str = None, is_active: bool = True) -> Optional[int]:
        """Yeni sınıf oluşturur"""
        try:
            query = """
            INSERT INTO grades (grade_name, description, is_active) 
            VALUES (%s, %s, %s)
            """
            return self.base_repo.execute_query(query, (grade_name, description, is_active))
        except Exception as e:
            print(f"Grade creation error: {e}")
            return None
    
    def update_grade(self, grade_id: int, grade_name: str, description: str = None, is_active: bool = True) -> bool:
        """Sınıf günceller"""
        try:
            query = """
            UPDATE grades 
            SET grade_name = %s, description = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE grade_id = %s
            """
            return self.base_repo.execute_query(query, (grade_name, description, is_active, grade_id)) > 0
        except Exception as e:
            print(f"Grade update error: {e}")
            return False
    
    def delete_grade(self, grade_id: int) -> bool:
        """Sınıf siler"""
        try:
            query = "DELETE FROM grades WHERE grade_id = %s"
            return self.base_repo.execute_query(query, (grade_id,)) > 0
        except Exception as e:
            print(f"Grade deletion error: {e}")
            return False
    
    # =============================================================================
    # SUBJECTS (DERSLER) YÖNETİMİ
    # =============================================================================
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """Tüm dersleri getirir"""
        try:
            query = """
            SELECT s.subject_id, s.subject_name, s.description, s.is_active, 
                   s.created_at, s.updated_at, s.grade_id,
                   g.grade_name
            FROM subjects s
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            ORDER BY g.grade_name, s.subject_name
            """
            return self.base_repo.fetch_all(query)
        except Exception as e:
            print(f"Subjects fetch error: {e}")
            return []
    
    def get_subject_by_id(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ders getirir"""
        try:
            query = """
            SELECT s.*, g.grade_name 
            FROM subjects s
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE s.subject_id = %s
            """
            return self.base_repo.fetch_one(query, (subject_id,))
        except Exception as e:
            print(f"Subject fetch error: {e}")
            return None
    
    def get_subjects_by_grade(self, grade_id: int) -> List[Dict[str, Any]]:
        """Belirli bir sınıfa ait tüm dersleri getirir"""
        try:
            query = """
            SELECT s.subject_id, s.subject_name, s.description, s.is_active,
                   s.created_at, s.updated_at, s.grade_id,
                   g.grade_name
            FROM subjects s
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE s.grade_id = %s
            ORDER BY s.subject_name
            """
            return self.base_repo.fetch_all(query, (grade_id,))
        except Exception as e:
            print(f"Subjects by grade fetch error: {e}")
            return []

    def create_subject(self, subject_name: str, grade_id: int, description: str = None, is_active: bool = True) -> Optional[int]:
        """Yeni ders oluşturur"""
        try:
            query = """
            INSERT INTO subjects (subject_name, grade_id, description, is_active) 
            VALUES (%s, %s, %s, %s)
            """
            return self.base_repo.execute_query(query, (subject_name, grade_id, description, is_active))
        except Exception as e:
            print(f"Subject creation error: {e}")
            return None
    
    def update_subject(self, subject_id: int, subject_name: str, grade_id: int, description: str = None, is_active: bool = True) -> bool:
        """Ders günceller"""
        try:
            query = """
            UPDATE subjects 
            SET subject_name = %s, grade_id = %s, description = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE subject_id = %s
            """
            return self.base_repo.execute_query(query, (subject_name, grade_id, description, is_active, subject_id)) > 0
        except Exception as e:
            print(f"Subject update error: {e}")
            return False
    
    def delete_subject(self, subject_id: int) -> bool:
        """Ders siler"""
        try:
            query = "DELETE FROM subjects WHERE subject_id = %s"
            return self.base_repo.execute_query(query, (subject_id,)) > 0
        except Exception as e:
            print(f"Subject deletion error: {e}")
            return False
    
    # =============================================================================
    # UNITS (ÜNİTELER) YÖNETİMİ
    # =============================================================================
    
    def get_all_units(self) -> List[Dict[str, Any]]:
        """Tüm üniteleri getirir"""
        try:
            query = """
            SELECT u.unit_id, u.unit_name, u.description, u.is_active, 
                   u.created_at, u.updated_at, u.subject_id,
                   s.subject_name, g.grade_id, g.grade_name
            FROM units u
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            ORDER BY g.grade_name, s.subject_name, u.unit_name
            """
            return self.base_repo.fetch_all(query)
        except Exception as e:
            print(f"Units fetch error: {e}")
            return []
    
    def get_unit_by_id(self, unit_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre ünite getirir"""
        try:
            query = """
            SELECT u.*, s.subject_name, g.grade_name 
            FROM units u
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE u.unit_id = %s
            """
            return self.base_repo.fetch_one(query, (unit_id,))
        except Exception as e:
            print(f"Unit fetch error: {e}")
            return None
    
    def get_units_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """Belirli bir derse ait tüm üniteleri getirir"""
        try:
            query = """
            SELECT u.unit_id, u.unit_name, u.description, u.is_active,
                   u.created_at, u.updated_at, u.subject_id,
                   s.subject_name, g.grade_id, g.grade_name
            FROM units u
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE u.subject_id = %s
            ORDER BY u.unit_name
            """
            return self.base_repo.fetch_all(query, (subject_id,))
        except Exception as e:
            print(f"Units by subject fetch error: {e}")
            return []

    def create_unit(self, unit_name: str, subject_id: int, description: str = None, is_active: bool = True) -> Optional[int]:
        """Yeni ünite oluşturur"""
        try:
            query = """
            INSERT INTO units (unit_name, subject_id, description, is_active) 
            VALUES (%s, %s, %s, %s)
            """
            return self.base_repo.execute_query(query, (unit_name, subject_id, description, is_active))
        except Exception as e:
            print(f"Unit creation error: {e}")
            return None
    
    def update_unit(self, unit_id: int, unit_name: str, subject_id: int, description: str = None, is_active: bool = True) -> bool:
        """Ünite günceller"""
        try:
            query = """
            UPDATE units 
            SET unit_name = %s, subject_id = %s, description = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE unit_id = %s
            """
            return self.base_repo.execute_query(query, (unit_name, subject_id, description, is_active, unit_id)) > 0
        except Exception as e:
            print(f"Unit update error: {e}")
            return False
    
    def delete_unit(self, unit_id: int) -> bool:
        """Ünite siler"""
        try:
            query = "DELETE FROM units WHERE unit_id = %s"
            return self.base_repo.execute_query(query, (unit_id,)) > 0
        except Exception as e:
            print(f"Unit deletion error: {e}")
            return False
    
    # =============================================================================
    # TOPICS (KONULAR) YÖNETİMİ
    # =============================================================================
    
    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Tüm konuları getirir"""
        try:
            query = """
            SELECT t.topic_id, t.topic_name, t.description, t.is_active, 
                   t.created_at, t.updated_at, t.unit_id,
                   u.unit_name, s.subject_id, s.subject_name, g.grade_id, g.grade_name
            FROM topics t
            LEFT JOIN units u ON t.unit_id = u.unit_id
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            ORDER BY g.grade_name, s.subject_name, u.unit_name, t.topic_name
            """
            return self.base_repo.fetch_all(query)
        except Exception as e:
            print(f"Topics fetch error: {e}")
            return []
    
    def get_topic_by_id(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre konu getirir"""
        try:
            query = """
            SELECT t.*, u.unit_name, s.subject_name, g.grade_name 
            FROM topics t
            LEFT JOIN units u ON t.unit_id = u.unit_id
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE t.topic_id = %s
            """
            return self.base_repo.fetch_one(query, (topic_id,))
        except Exception as e:
            print(f"Topic fetch error: {e}")
            return None
    
    def get_topics_by_unit(self, unit_id: int) -> List[Dict[str, Any]]:
        """Belirli bir üniteye ait tüm konuları getirir"""
        try:
            query = """
            SELECT t.topic_id, t.topic_name, t.description, t.is_active,
                   t.created_at, t.updated_at, t.unit_id,
                   u.unit_name, s.subject_id, s.subject_name, g.grade_id, g.grade_name
            FROM topics t
            LEFT JOIN units u ON t.unit_id = u.unit_id
            LEFT JOIN subjects s ON u.subject_id = s.subject_id
            LEFT JOIN grades g ON s.grade_id = g.grade_id
            WHERE t.unit_id = %s
            ORDER BY t.topic_name
            """
            return self.base_repo.fetch_all(query, (unit_id,))
        except Exception as e:
            print(f"Topics by unit fetch error: {e}")
            return []

    def create_topic(self, topic_name: str, unit_id: int, description: str = None, is_active: bool = True) -> Optional[int]:
        """Yeni konu oluşturur"""
        try:
            query = """
            INSERT INTO topics (topic_name, unit_id, description, is_active) 
            VALUES (%s, %s, %s, %s)
            """
            return self.base_repo.execute_query(query, (topic_name, unit_id, description, is_active))
        except Exception as e:
            print(f"Topic creation error: {e}")
            return None
    
    def update_topic(self, topic_id: int, topic_name: str, unit_id: int, description: str = None, is_active: bool = True) -> bool:
        """Konu günceller"""
        try:
            query = """
            UPDATE topics 
            SET topic_name = %s, unit_id = %s, description = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = %s
            """
            return self.base_repo.execute_query(query, (topic_name, unit_id, description, is_active, topic_id)) > 0
        except Exception as e:
            print(f"Topic update error: {e}")
            return False
    
    def delete_topic(self, topic_id: int) -> bool:
        """Konu siler"""
        try:
            query = "DELETE FROM topics WHERE topic_id = %s"
            return self.base_repo.execute_query(query, (topic_id,)) > 0
        except Exception as e:
            print(f"Topic deletion error: {e}")
            return False
    
    # =============================================================================
    # VERİ AKTARIMI
    # =============================================================================
    
    def export_curriculum_data(self) -> Dict[str, Any]:
        """Müfredat verilerini export eder"""
        try:
            return {
                'grades': self.get_all_grades(),
                'subjects': self.get_all_subjects(),
                'units': self.get_all_units(),
                'topics': self.get_all_topics()
            }
        except Exception as e:
            print(f"Export error: {e}")
            return {}
    
    def import_curriculum_data(self, data: Dict[str, Any]) -> bool:
        """Müfredat verilerini import eder"""
        try:
            # Counters for optional debugging
            imported = {"grades": 0, "subjects": 0, "units": 0, "topics": 0}

            # Helper upsert-like ensure functions using name-based lookups
            def ensure_grade(grade_name: str, description: Optional[str] = None, is_active: bool = True):
                row = self.base_repo.fetch_one(
                    "SELECT grade_id FROM grades WHERE grade_name = %s", (grade_name,)
                )
                if row:
                    return row["grade_id"], False
                gid = self.create_grade(grade_name, description, is_active)
                return gid, True

            def ensure_subject(grade_id: int, subject_name: str, description: Optional[str] = None, is_active: bool = True):
                row = self.base_repo.fetch_one(
                    "SELECT subject_id FROM subjects WHERE grade_id = %s AND subject_name = %s",
                    (grade_id, subject_name),
                )
                if row:
                    return row["subject_id"], False
                sid = self.create_subject(subject_name, grade_id, description, is_active)
                return sid, True

            def ensure_unit(subject_id: int, unit_name: str, description: Optional[str] = None, is_active: bool = True):
                row = self.base_repo.fetch_one(
                    "SELECT unit_id FROM units WHERE subject_id = %s AND unit_name = %s",
                    (subject_id, unit_name),
                )
                if row:
                    return row["unit_id"], False
                uid = self.create_unit(unit_name, subject_id, description, is_active)
                return uid, True

            def ensure_topic(unit_id: int, topic_name: str, description: Optional[str] = None, is_active: bool = True):
                row = self.base_repo.fetch_one(
                    "SELECT topic_id FROM topics WHERE unit_id = %s AND topic_name = %s",
                    (unit_id, topic_name),
                )
                if row:
                    return row["topic_id"], False
                tid = self.create_topic(topic_name, unit_id, description, is_active)
                return tid, True

            # Resolver helpers for flat data
            def resolve_subject_id(subject_name: str, grade_name: Optional[str] = None) -> Optional[int]:
                if grade_name:
                    row = self.base_repo.fetch_one(
                        """
                        SELECT s.subject_id
                        FROM subjects s
                        LEFT JOIN grades g ON s.grade_id = g.grade_id
                        WHERE s.subject_name = %s AND g.grade_name = %s
                        """,
                        (subject_name, grade_name),
                    )
                    if row:
                        return row["subject_id"]
                row = self.base_repo.fetch_one(
                    "SELECT subject_id FROM subjects WHERE subject_name = %s ORDER BY subject_id LIMIT 1",
                    (subject_name,),
                )
                return row["subject_id"] if row else None

            def resolve_unit_id(unit_name: str, subject_name: Optional[str] = None, grade_name: Optional[str] = None) -> Optional[int]:
                if subject_name and grade_name:
                    row = self.base_repo.fetch_one(
                        """
                        SELECT u.unit_id
                        FROM units u
                        LEFT JOIN subjects s ON u.subject_id = s.subject_id
                        LEFT JOIN grades g ON s.grade_id = g.grade_id
                        WHERE u.unit_name = %s AND s.subject_name = %s AND g.grade_name = %s
                        """,
                        (unit_name, subject_name, grade_name),
                    )
                    if row:
                        return row["unit_id"]
                row = self.base_repo.fetch_one(
                    "SELECT unit_id FROM units WHERE unit_name = %s ORDER BY unit_id LIMIT 1",
                    (unit_name,),
                )
                return row["unit_id"] if row else None

            processed_any = False

            # Case 1: Flat export format like {'grades': [...], 'subjects': [...], 'units': [...], 'topics': [...]}.
            if isinstance(data, dict) and any(k in data for k in ("grades", "subjects", "units", "topics")):
                grade_name_to_id: Dict[str, int] = {}

                # Grades
                for g in data.get("grades", []) or []:
                    gname = g.get("grade_name") or g.get("gradeName") or g.get("name")
                    if not gname:
                        continue
                    gid, created = ensure_grade(gname, g.get("description"), g.get("is_active", True))
                    grade_name_to_id[gname] = gid
                    if created:
                        imported["grades"] += 1

                # Subjects
                for s in data.get("subjects", []) or []:
                    sname = s.get("subject_name") or s.get("subjectName")
                    if not sname:
                        continue
                    gname = s.get("grade_name") or s.get("gradeName")
                    gid = None
                    if gname:
                        # Ensure referenced grade exists
                        gid = grade_name_to_id.get(gname)
                        if not gid:
                            gid, gcreated = ensure_grade(gname)
                            if gcreated:
                                imported["grades"] += 1
                            grade_name_to_id[gname] = gid
                    else:
                        gid = s.get("grade_id")
                    if not gid:
                        continue
                    _, screated = ensure_subject(gid, sname, s.get("description"), s.get("is_active", True))
                    if screated:
                        imported["subjects"] += 1

                # Units
                for u in data.get("units", []) or []:
                    uname = u.get("unit_name") or u.get("unitName")
                    if not uname:
                        continue
                    sname = u.get("subject_name") or u.get("subjectName")
                    gname = u.get("grade_name") or u.get("gradeName")
                    sid = resolve_subject_id(sname, gname) if sname else (u.get("subject_id") or None)
                    if not sid:
                        continue
                    _, ucreated = ensure_unit(sid, uname, u.get("description"), u.get("is_active", True))
                    if ucreated:
                        imported["units"] += 1

                # Topics
                for t in data.get("topics", []) or []:
                    tname = t.get("topic_name") or t.get("topicName")
                    if not tname:
                        continue
                    uname = t.get("unit_name") or t.get("unitName")
                    sname = t.get("subject_name") or t.get("subjectName")
                    gname = t.get("grade_name") or t.get("gradeName")
                    uid = resolve_unit_id(uname, sname, gname) if uname else (t.get("unit_id") or None)
                    if not uid:
                        continue
                    _, tcreated = ensure_topic(uid, tname, t.get("description"), t.get("is_active", True))
                    if tcreated:
                        imported["topics"] += 1

                processed_any = True

            # Case 2: Hierarchical format like [{'gradeLevel':..., 'gradeName':..., 'subjects':[...]}] or dict
            if not processed_any:
                items = data if isinstance(data, list) else [data]
                for curriculum_data in items:
                    grade_name = (
                        curriculum_data.get("gradeName")
                        or curriculum_data.get("grade_name")
                        or curriculum_data.get("grade")
                        or f"Grade {curriculum_data.get('gradeLevel', 'Unknown')}"
                    )
                    gid, gcreated = ensure_grade(grade_name)
                    if gcreated:
                        imported["grades"] += 1

                    for subject_data in curriculum_data.get("subjects", []) or []:
                        sname = subject_data.get("subjectName") or subject_data.get("subject_name")
                        if not sname:
                            continue
                        sid, screated = ensure_subject(gid, sname)
                        if screated:
                            imported["subjects"] += 1

                        for unit_data in subject_data.get("units", []) or []:
                            uname = unit_data.get("unitName") or unit_data.get("unit_name")
                            if not uname:
                                continue
                            uid, ucreated = ensure_unit(sid, uname)
                            if ucreated:
                                imported["units"] += 1

                            for topic_data in unit_data.get("topics", []) or []:
                                tname = topic_data.get("topicName") or topic_data.get("topic_name")
                                if not tname:
                                    continue
                                _, tcreated = ensure_topic(uid, tname)
                                if tcreated:
                                    imported["topics"] += 1

            # Successful import
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    # =============================================================================
    # JSON DOSYA İŞLEMLERİ (ESKİ KOD - KORUNUYOR)
    # =============================================================================
    
    def get_curriculum_json_files(self) -> List[str]:
        """Müfredat JSON dosyalarını listeler"""
        json_files = []
        if os.path.exists(self.curriculum_data_path):
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
                    subject_id = self.create_subject(subject_name, grade_id)
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
                        unit_id = self.create_unit(unit_name, subject_id)
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
                            self.create_topic(topic_name, unit_id)
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
