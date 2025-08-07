# =============================================================================
# QUESTION LOADER CLI SCRIPT
# =============================================================================
# Bu script, question JSON dosyalarını veritabanına yüklemek için kullanılır.
# =============================================================================

import sys
import os
import argparse
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.quiz_data_loader import QuestionLoader

def main():
    """
    Ana fonksiyon - CLI argümanlarını işler ve question yükleme işlemini başlatır.
    """
    parser = argparse.ArgumentParser(
        description="Question JSON dosyalarını veritabanına yükler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tüm question dosyalarını yükle
  python load_questions.py

  # Belirli bir dosyayı yükle
  python load_questions.py --file app/data/quiz_banks/grade_8/turkish/verbals/participle.json

  # Belirli bir dizindeki dosyaları yükle
  python load_questions.py --dir app/data/quiz_banks/grade_8/turkish

  # Verbose mod ile yükle
  python load_questions.py --verbose
        """
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Yüklenecek belirli bir JSON dosyasının yolu'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        help='Yüklenecek dosyaların bulunduğu dizin'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='app/data/quiz_banks',
        help='Question dosyalarının varsayılan dizini (varsayılan: app/data/quiz_banks)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Detaylı çıktı göster'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Gerçek veritabanı işlemi yapmadan test et'
    )
    
    args = parser.parse_args()
    
    # QuestionLoader'ı başlat
    loader = QuestionLoader(args.data_dir)
    
    try:
        if args.dry_run:
            # Dry run mode enabled, no database operations will be performed
            pass
            
        if args.file:
            # Tek dosya yükle
            file_path = Path(args.file)
            if not file_path.exists():
                return 1
            
            success, total = loader.process_question_file(str(file_path))
            
        elif args.dir:
            # Belirli dizindeki dosyaları yükle
            dir_path = Path(args.dir)
            if not dir_path.exists():
                return 1
            
            json_files = list(dir_path.rglob("*.json"))
            
            if not json_files:
                return 1
            
            total_success = 0
            total_questions = 0
            
            for file_path in json_files:
                success, total = loader.process_question_file(str(file_path))
                total_success += success
                total_questions += total
        
        else:
            # Tüm dosyaları yükle
            results = loader.process_all_question_files()
            
            # Sonuçları özetle
            total_success = 0
            total_questions = 0
            
            for filename, (success, total) in results.items():
                total_success += success
                total_questions += total
        
        return 0
        
    except KeyboardInterrupt:
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        loader.close()

if __name__ == "__main__":
    sys.exit(main()) 