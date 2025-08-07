# =============================================================================
# QUESTION LOADER MODULE
# =============================================================================
# Bu modül, JSON dosyalarından question verilerini okur ve veritabanına ekler.
# =============================================================================

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from .db_connection import DatabaseConnection

class QuestionLoader:
    """
    JSON dosyalarından question verilerini okur ve veritabanına ekler.
    """
    
    def __init__(self, data_dir: str = "app/data/quiz_banks", db_connection: Optional[DatabaseConnection] = None):
        """
        QuestionLoader sınıfının kurucu metodu.
        
        Args:
            data_dir: Question JSON dosyalarının bulunduğu dizin
            db_connection: Mevcut veritabanı bağlantısı (opsiyonel)
        """
        self.data_dir = Path(data_dir)
        if db_connection:
            self.db = db_connection
            self.own_connection = False
        else:
            self.db = DatabaseConnection()
            self.own_connection = True
        
    def load_question_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Belirtilen JSON dosyasından question verilerini yükler.
        
        Args:
            file_path: JSON dosyasının yolu
            
        Returns:
            Question verilerini içeren sözlük veya None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ Dosya okuma hatası {file_path}: {e}")
            return None
    
    def get_topic_id(self, grade: int, subject: str, unit: str, topic: str) -> Optional[int]:
        """
        Verilen bilgilere göre topic_id'yi veritabanından bulur.
        
        Args:
            grade: Sınıf seviyesi
            subject: Ders adı
            unit: Ünite adı
            topic: Konu adı
            
        Returns:
            Topic ID veya None
        """
        try:
            query = """
            SELECT t.id 
            FROM topics t
            JOIN units u ON t.unit_id = u.id
            JOIN subjects s ON u.subject_id = s.id
            JOIN grades g ON s.grade_id = g.id
            WHERE g.level = %s 
            AND s.name = %s 
            AND u.name = %s 
            AND t.name = %s
            """
            
            with self.db as conn:
                conn.cursor.execute(query, (grade, subject, unit, topic))
                result = conn.cursor.fetchone()
                
                if result:
                    return result['id']
                else:
                    print(f"⚠️  Topic bulunamadı: Grade {grade}, {subject}, {unit}, {topic}")
                    return None
                
        except Exception as e:
            print(f"❌ Topic ID sorgulama hatası: {e}")
            return None
    
    def insert_question(self, question_data: Dict[str, Any], topic_id: int) -> Optional[int]:
        """
        Tek bir question'ı veritabanına ekler.
        
        Args:
            question_data: Question verilerini içeren sözlük
            topic_id: Question'ın ait olduğu topic ID
            
        Returns:
            Eklenen question'ın ID'si veya None
        """
        try:
            with self.db as conn:
                # Question'ı ekle
                question_query = """
                INSERT INTO questions (name, name_id, topic_id, difficulty_level, question_type, points, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                question_name = question_data['questionText']
                question_name_id = f"q_{topic_id}_{hash(question_name) % 10000}"
                question_explanation = question_data.get('explanation', '')
                
                question_values = (
                    question_name,
                    question_name_id,
                    topic_id,
                    question_data['difficulty'],
                    question_data['questionType'],
                    1,  # Varsayılan puan
                    question_explanation
                )
                
                conn.cursor.execute(question_query, question_values)
                question_id = conn.cursor.lastrowid
                
                # Question options'ları ekle
                for i, option in enumerate(question_data['options']):
                    option_query = """
                    INSERT INTO question_options (question_id, name, name_id, is_correct, option_order, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    option_name = option['text']
                    option_name_id = f"opt_{question_id}_{i+1}"
                    option_explanation = option.get('explanation', '')
                    
                    option_values = (
                        question_id,
                        option_name,
                        option_name_id,
                        option['isCorrect'],
                        ord(option['id']) - ord('A') + 1,  # A=1, B=2, C=3, D=4
                        option_explanation
                    )
                    
                    conn.cursor.execute(option_query, option_values)
                
                return question_id
            
        except Exception as e:
            print(f"❌ Question ekleme hatası: {e}")
            return None
    
    def process_question_file(self, file_path: str) -> Tuple[int, int]:
        """
        Bir question JSON dosyasını işler ve veritabanına ekler.
        
        Args:
            file_path: JSON dosyasının yolu
            
        Returns:
            (başarılı eklenen question sayısı, toplam question sayısı)
        """
        data = self.load_question_file(file_path)
        if not data:
            return 0, 0
        
        metadata = data.get('metadata', {})
        questions = data.get('questions', [])
        
        grade = metadata.get('grade')
        subject = metadata.get('subject')
        unit = metadata.get('unit')
        topic = metadata.get('topic')
        
        if not all([grade, subject, unit, topic]):
            print(f"❌ Eksik metadata: {file_path}")
            return 0, len(questions)
        
        # Topic ID'yi bul
        topic_id = self.get_topic_id(grade, subject, unit, topic)
        if not topic_id:
            print(f"❌ Topic bulunamadı: {file_path}")
            return 0, len(questions)
        
        success_count = 0
        
        for i, question in enumerate(questions, 1):
            question_id = self.insert_question(question, topic_id)
            if question_id:
                success_count += 1
        return success_count, len(questions)
    
    def process_all_question_files(self) -> Dict[str, Tuple[int, int]]:
        """
        Tüm question JSON dosyalarını işler.
        
        Returns:
            Dosya adı -> (başarılı, toplam) sözlüğü
        """
        if not self.data_dir.exists():
            print(f"❌ Question data dizini bulunamadı: {self.data_dir}")
            return {}
        
        results = {}
        
        # Tüm JSON dosyalarını bul
        json_files = list(self.data_dir.rglob("*.json"))
        
        if not json_files:
            print(f"❌ Question JSON dosyası bulunamadı: {self.data_dir}")
            return {}
        

        
        for file_path in json_files:
            success, total = self.process_question_file(str(file_path))
            results[file_path.name] = (success, total)
        
        return results
    
    def close(self):
        """
        Veritabanı bağlantısını kapatır.
        """
        if hasattr(self, 'own_connection') and self.own_connection:
            self.db.close()

# =============================================================================
# KULLANIM ÖRNEĞİ
# =============================================================================
if __name__ == "__main__":
    loader = QuestionLoader()
    
    try:
        # Tüm dosyaları işle
        results = loader.process_all_question_files()
        
        # Sonuçları özetle
        total_success = 0
        total_questions = 0
        
        for filename, (success, total) in results.items():
            total_success += success
            total_questions += total
        
    except Exception as e:
        print(f"❌ Genel hata: {e}")
    finally:
        loader.close() 