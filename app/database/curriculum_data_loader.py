# =============================================================================
# JSON DATA LOADER
# =============================================================================
# Bu modül, JSON dosyalarından veri okur ve veritabanı için SQL insert
# ifadeleri oluşturur.
# =============================================================================

import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class JSONDataLoader:
    """
    JSON dosyalarından veri okur ve veritabanı için SQL insert ifadeleri oluşturur.
    """
    
    def __init__(self, data_dir: str = "app/data/curriculum_structure"):
        """
        JSONDataLoader sınıfının kurucu metodu.
        
        Args:
            data_dir: JSON dosyalarının bulunduğu dizin
        """
        self.data_dir = Path(data_dir)
        self.grades_data = {}
        self.subjects_data = {}
        self.topics_data = {}
        
    def load_all_grade_files(self) -> Dict[int, dict]:
        """
        Tüm grade JSON dosyalarını yükler.
        
        Returns:
            Grade seviyesi -> veri sözlüğü
        """
        if not self.data_dir.exists():
            print(f"❌ Veri dizini bulunamadı: {self.data_dir}")
            return {}
            
        grade_files = list(self.data_dir.glob("grade_*.json"))
        
        if not grade_files:
            print(f"❌ Grade dosyası bulunamadı: {self.data_dir}")
            return {}
            
        for file_path in grade_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if data and isinstance(data, list) and len(data) > 0:
                    grade_info = data[0]  # İlk eleman grade bilgilerini içerir
                    grade_level = grade_info.get('gradeLevel')
                    
                    if grade_level:
                        self.grades_data[grade_level] = grade_info
                        
            except Exception as e:
                print(f"❌ Dosya okuma hatası {file_path.name}: {e}")
                
        return self.grades_data
    
    def extract_subjects(self) -> List[Tuple[int, str, str, str]]:
        """
        Tüm grade'lerden dersleri çıkarır.
        
        Returns:
            (grade_level, course_id, course_name, description) listesi
        """
        subjects = []
        
        for grade_level, grade_data in self.grades_data.items():
            courses = grade_data.get('subjects', [])
            
            for course in courses:
                course_id = course.get('subjectId')
                course_name = course.get('subjectName')
                
                if course_id and course_name:
                    subjects.append((
                        grade_level,
                        course_id,
                        course_name,
                        f'{course_name} dersi'
                    ))
                        
        self.subjects_data = subjects
        return subjects
    
    def extract_units(self) -> List[Tuple[str, str, str, str]]:
        """
        Tüm grade'lerden üniteleri çıkarır.
        
        Returns:
            (unit_id, unit_name, subject_code, description) listesi
        """
        units = []
        
        for grade_level, grade_data in self.grades_data.items():
            courses = grade_data.get('subjects', [])
            
            for course in courses:
                course_id = course.get('subjectId')
                units_list = course.get('units', [])
                
                for unit in units_list:
                    unit_id = unit.get('unitId')
                    unit_name = unit.get('unitName')
                    
                    if unit_id and unit_name:
                        units.append((
                            unit_id,
                            unit_name,
                            course_id,
                            f'{unit_name} ünitesi'
                        ))
                                
        self.units_data = units
        return units
    
    def extract_topics(self) -> List[Tuple[str, str, str, str]]:
        """
        Tüm grade'lerden konuları çıkarır.
        
        Returns:
            (topic_id, topic_name, unit_id, açıklama) listesi
        """
        topics = []
        
        for grade_level, grade_data in self.grades_data.items():
            courses = grade_data.get('subjects', [])
            
            for course in courses:
                units_list = course.get('units', [])
                
                for unit in units_list:
                    unit_id = unit.get('unitId')
                    unit_name = unit.get('unitName')
                    unit_topics = unit.get('topics', [])
                    
                    if unit_id and unit_name:
                        # Alt konular
                        for topic in unit_topics:
                            if isinstance(topic, dict):
                                # Yeni format: {"topicId": "...", "topicName": "..."}
                                topic_id = topic.get('topicId')
                                topic_name = topic.get('topicName')
                                
                                if topic_id and topic_name:
                                    topics.append((
                                        topic_id,
                                        topic_name,
                                        unit_id,
                                        f'{unit_name} - {topic_name}'
                                    ))
                            elif isinstance(topic, str) and topic:
                                # Eski format: string (geriye uyumluluk için)
                                topics.append((
                                    topic.lower().replace(' ', '_'),
                                    topic,
                                    unit_id,
                                    f'{unit_name} - {topic}'
                                ))
                                
        self.topics_data = topics
        return topics
    
    def generate_grades_sql(self) -> str:
        """
        Grade verilerinden SQL insert ifadesi oluşturur.
        
        Returns:
            SQL insert ifadesi
        """
        if not self.grades_data:
            return ""
            
        values = []
        for grade_level, grade_data in self.grades_data.items():
            grade_name = grade_data.get('gradeName', f'{grade_level}. Sınıf')
            grade_name_id = f'grade_{grade_level}'
            description = f'{grade_name} seviyesi'
            
            values.append(f"('{grade_name}', '{grade_name_id}', {grade_level}, '{description}')")
            
        if not values:
            return ""
            
        sql = f"""
INSERT INTO grades (name, name_id, level, description) VALUES
{', '.join(values)}
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description);
"""
        return sql
    
    def generate_subjects_sql(self, grade_id_map: Dict[int, int]) -> str:
        """
        Ders verilerinden SQL insert ifadesi oluşturur.
        
        Args:
            grade_id_map: Grade seviyesi -> veritabanı ID eşlemesi
            
        Returns:
            SQL insert ifadesi
        """
        if not self.subjects_data:
            return ""
            
        values = []
        for grade_level, subject_code, subject_name, description in self.subjects_data:
            grade_id = grade_id_map.get(grade_level)
            
            if grade_id:
                # SQL injection'a karşı koruma
                subject_name_escaped = subject_name.replace("'", "''")
                description_escaped = description.replace("'", "''")
                
                values.append(f"({grade_id}, '{subject_name_escaped}', '{subject_code.upper()}', '{description_escaped}')")
            
        if not values:
            return ""
            
        sql = f"""
INSERT INTO subjects (grade_id, name, name_id, description) VALUES
{', '.join(values)}
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description);
"""
        return sql
    
    def generate_units_sql(self, subject_id_map: Dict[str, int]) -> str:
        """
        Ünite verilerinden SQL insert ifadesi oluşturur.
        
        Args:
            subject_id_map: Ders kodu -> veritabanı ID eşlemesi
            
        Returns:
            SQL insert ifadesi
        """
        if not self.units_data:
            return ""
            
        values = []
        for unit_id, unit_name, subject_code, description in self.units_data:
            subject_id = subject_id_map.get(subject_code)
            
            if subject_id:
                # SQL injection'a karşı koruma
                unit_name_escaped = unit_name.replace("'", "''")
                description_escaped = description.replace("'", "''")
                
                values.append(f"({subject_id}, '{unit_name_escaped}', '{unit_id}', '{description_escaped}')")
            
        if not values:
            return ""
            
        sql = f"""
INSERT INTO units (subject_id, name, name_id, description) VALUES
{', '.join(values)}
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description);
"""
        return sql
    
    def generate_topics_sql(self, unit_id_map: Dict[str, int]) -> str:
        """
        Konu verilerinden SQL insert ifadesi oluşturur.
        
        Args:
            unit_id_map: Ünite ID'si -> veritabanı ID eşlemesi
            
        Returns:
            SQL insert ifadesi
        """
        if not self.topics_data:
            return ""
            
        values = []
        for topic_id, topic_name, unit_id, description in self.topics_data:
            db_unit_id = unit_id_map.get(unit_id)
            
            if db_unit_id:
                # SQL injection'a karşı koruma
                topic_id_escaped = topic_id.replace("'", "''")
                topic_name_escaped = topic_name.replace("'", "''")
                description_escaped = description.replace("'", "''")
                
                values.append(f"({db_unit_id}, '{topic_name_escaped}', '{topic_id_escaped}', '{description_escaped}')")
            
        if not values:
            return ""
            
        sql = f"""
INSERT INTO topics (unit_id, name, name_id, description) VALUES
{', '.join(values)}
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description);
"""
        return sql
    
    def process_all_data(self) -> Tuple[str, str, str, str]:
        """
        Tüm JSON verilerini işler ve SQL ifadeleri oluşturur.
        
        Returns:
            (grades_sql, subjects_sql, units_sql, topics_sql) tuple
        """
        # 1. Grade dosyalarını yükle
        self.load_all_grade_files()
        
        # 2. Dersleri çıkar
        self.extract_subjects()
        
        # 3. Üniteleri çıkar
        self.extract_units()
        
        # 4. Konuları çıkar
        self.extract_topics()
        
        # 5. SQL ifadelerini oluştur
        grades_sql = self.generate_grades_sql()
        subjects_sql = ""  # grade_id_map gerektirir
        units_sql = ""     # subject_id_map gerektirir
        topics_sql = ""    # unit_id_map gerektirir
        
        return grades_sql, subjects_sql, units_sql, topics_sql
    
    def get_grade_id_map(self, db_connection) -> Dict[int, int]:
        """
        Veritabanından grade seviyelerini ID'lere eşler.
        
        Args:
            db_connection: Veritabanı bağlantısı
            
        Returns:
            Grade seviyesi -> ID eşlemesi
        """
        grade_id_map = {}
        
        try:
            with db_connection as conn:
                for grade_level in self.grades_data.keys():
                    conn.cursor.execute(
                        "SELECT id FROM grades WHERE level = %s",
                        (grade_level,)
                    )
                    result = conn.cursor.fetchone()
                    if result:
                        grade_id_map[grade_level] = result['id']
                        
        except Exception as e:
            print(f"❌ Grade ID map oluşturma hatası: {e}")
            
        return grade_id_map
    
    def get_subject_id_map(self, db_connection) -> Dict[str, int]:
        """
        Veritabanından ders kodlarını ID'lere eşler.
        
        Args:
            db_connection: Veritabanı bağlantısı
            
        Returns:
            Ders kodu -> ID eşlemesi
        """
        subject_id_map = {}
        
        try:
            with db_connection as conn:
                for grade_level, subject_code, subject_name, description in self.subjects_data:
                    conn.cursor.execute(
                        "SELECT s.id FROM subjects s JOIN grades g ON s.grade_id = g.id WHERE s.name_id = %s AND g.level = %s",
                        (subject_code.upper(), grade_level)
                    )
                    result = conn.cursor.fetchone()
                    if result:
                        subject_id_map[subject_code] = result['id']
                        
        except Exception as e:
            print(f"❌ Subject ID map oluşturma hatası: {e}")
            
        return subject_id_map
    
    def get_unit_id_map(self, db_connection) -> Dict[str, int]:
        """
        Veritabanından ünite ID'lerini veritabanı ID'lerine eşler.
        
        Args:
            db_connection: Veritabanı bağlantısı
            
        Returns:
            Ünite ID'si -> veritabanı ID eşlemesi
        """
        unit_id_map = {}
        
        try:
            with db_connection as conn:
                for unit_id, unit_name, subject_code, description in self.units_data:
                    conn.cursor.execute(
                        "SELECT u.id FROM units u JOIN subjects s ON u.subject_id = s.id WHERE u.name_id = %s AND s.name_id = %s",
                        (unit_id, subject_code.upper())
                    )
                    result = conn.cursor.fetchone()
                    if result:
                        unit_id_map[unit_id] = result['id']
                        
        except Exception as e:
            print(f"❌ Unit ID map oluşturma hatası: {e}")
            
        return unit_id_map 