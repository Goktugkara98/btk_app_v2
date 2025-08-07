# =============================================================================
# 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
# =============================================================================
# Bu modül, quiz ile ilgili sayfa rotalarını (endpoints) içerir.
# Quiz başlatma, quiz ekranı, sonuçlar gibi quiz sayfalarını yönetir.
# =============================================================================

# =============================================================================
# 2.0. İÇİNDEKİLER
# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# 4.0. QUIZ SAYFA ROTALARI (QUIZ PAGE ROUTES)
#   4.1. Quiz Sayfaları
#     4.1.1. GET /quiz
#     4.1.2. GET /quiz/start
#     4.1.3. GET /quiz/normal
#     4.1.4. GET /quiz/educational
#     4.1.5. GET /quiz/session/<session_id>
#     4.1.6. GET /quiz/results
#     4.1.7. GET /quiz/auto-start (Normal mode)
#     4.1.8. GET /quiz/auto-start-educational (Educational mode)
# =============================================================================

# =============================================================================
# 3.0. GEREKLİ KÜTÜPHANELER VE MODÜLLER
# =============================================================================
from flask import Blueprint, render_template, session, redirect, url_for, request

# Import authentication service
try:
    from app.services.auth_service import login_required
except ImportError as e:
    login_required = None

# Create the quiz pages blueprint
quiz_bp = Blueprint('quiz', __name__)

# =============================================================================
# 4.0. QUIZ SAYFA ROTALARI (QUIZ PAGE ROUTES)
# =============================================================================

# -------------------------------------------------------------------------
# 4.1. Quiz Sayfaları
# -------------------------------------------------------------------------

@quiz_bp.route('/quiz')
@login_required
def quiz():
    """4.1.1. Quiz sayfasını render eder."""
    return render_template('quiz_screen.html', title='Quiz')

@quiz_bp.route('/quiz/start')
# @login_required  # Temporarily disabled for testing
def quiz_start():
    """4.1.2. Quiz başlatma sayfasını render eder."""
    return render_template('quiz_start.html', title='Quiz Başlat')

@quiz_bp.route('/quiz/normal')
# @login_required  # Temporarily disabled for testing
def quiz_normal():
    """4.1.3. Normal quiz ekranını render eder."""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('quiz.quiz_start'))
    return render_template('quiz_normal.html', title='Normal Quiz', session_id=session_id)

@quiz_bp.route('/quiz/educational')
# @login_required  # Temporarily disabled for testing
def quiz_educational():
    """4.1.4. Öğretici quiz ekranını render eder."""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('quiz.quiz_start'))
    return render_template('quiz_educational.html', title='Öğretici Quiz', session_id=session_id)

@quiz_bp.route('/quiz/session/<session_id>')
# @login_required  # Temporarily disabled for testing
def quiz_session(session_id):
    """4.1.5. Quiz oturum sayfasını render eder (legacy - redirects to appropriate mode)."""
    # Session bilgilerini al ve quiz moduna göre yönlendir
    try:
        from app.services.quiz_session_service import QuizSessionService
        session_service = QuizSessionService()
        session_info = session_service.get_session_info(session_id)
        
        if session_info and session_info.get('session'):
            quiz_mode = session_info['session'].get('quiz_mode', 'normal')
            if quiz_mode == 'educational':
                return redirect(url_for('quiz.quiz_educational', session_id=session_id))
            else:
                return redirect(url_for('quiz.quiz_normal', session_id=session_id))
        else:
            # Session bulunamadıysa normal moda yönlendir
            return redirect(url_for('quiz.quiz_normal', session_id=session_id))
    except Exception as e:
        # Hata durumunda normal moda yönlendir
        return redirect(url_for('quiz.quiz_normal', session_id=session_id))

@quiz_bp.route('/quiz/screen')
# @login_required  # Temporarily disabled for testing
def quiz_screen():
    """4.1.6. Quiz ekranı sayfasını render eder (session_id query parameter ile) - legacy."""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('quiz.quiz_start'))
    
    # Session bilgilerini al ve quiz moduna göre yönlendir
    try:
        from app.services.quiz_session_service import QuizSessionService
        session_service = QuizSessionService()
        session_info = session_service.get_session_info(session_id)
        
        if session_info and session_info.get('session'):
            quiz_mode = session_info['session'].get('quiz_mode', 'normal')
            if quiz_mode == 'educational':
                return redirect(url_for('quiz.quiz_educational', session_id=session_id))
            else:
                return redirect(url_for('quiz.quiz_normal', session_id=session_id))
        else:
            # Session bulunamadıysa normal moda yönlendir
            return redirect(url_for('quiz.quiz_normal', session_id=session_id))
    except Exception as e:
        # Hata durumunda normal moda yönlendir
        return redirect(url_for('quiz.quiz_normal', session_id=session_id))

@quiz_bp.route('/quiz/results')
# @login_required  # Temporarily disabled for testing
def quiz_results():
    """4.1.7. Quiz sonuçları sayfasını render eder."""
    session_id = request.args.get('session_id')
    return render_template('quiz_results.html', title='Quiz Sonuçları', session_id=session_id)

@quiz_bp.route('/quiz/auto-start')
def quiz_auto_start():
    """4.1.7. Otomatik quiz başlatma - testuser ile 8. sınıf Türkçe sıfat-fiil konusu."""
    try:
        from app.database.db_connection import DatabaseConnection
        from app.database.user_repository import UserRepository
        from app.services.quiz_session_service import QuizSessionService
        import hashlib
        
        # Testuser'ı oluştur veya mevcut olanı bul
        with DatabaseConnection() as conn:
            # Önce testuser'ın var olup olmadığını kontrol et
            conn.cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
            user_result = conn.cursor.fetchone()
            
            if user_result:
                test_user_id = user_result['id']
            else:
                # Testuser yoksa oluştur
                
                # Basit şifre hash'i oluştur
                password_hash = hashlib.sha256("test123".encode()).hexdigest()
                
                # Direkt SQL ile kullanıcı oluştur
                conn.cursor.execute("""
                    INSERT INTO users (username, name_id, email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('testuser', 'testuser', 'testuser@example.com', password_hash, 'Test', 'User'))
                
                test_user_id = conn.cursor.lastrowid
                conn.connection.commit()
            
            # Mevcut sınıfları kontrol et
            conn.cursor.execute("SELECT id, name FROM grades WHERE is_active = 1")
            grades = conn.cursor.fetchall()
            
            # 8. sınıf ID'sini bul
            conn.cursor.execute("SELECT id FROM grades WHERE name = '8. Sınıf' AND is_active = 1")
            grade_result = conn.cursor.fetchone()
            if not grade_result:
                # Eğer 8. sınıf yoksa, ilk sınıfı kullan
                conn.cursor.execute("SELECT id FROM grades WHERE is_active = 1 LIMIT 1")
                grade_result = conn.cursor.fetchone()
                if not grade_result:
                    return "Hiç sınıf bulunamadı", 404
                grade_id = grade_result['id']
            else:
                grade_id = grade_result['id']
            
            # Mevcut dersleri kontrol et
            conn.cursor.execute("SELECT id, name FROM subjects WHERE grade_id = %s AND is_active = 1", (grade_id,))
            subjects = conn.cursor.fetchall()
            
            # Türkçe dersi ID'sini bul
            conn.cursor.execute("SELECT id FROM subjects WHERE name = 'Türkçe' AND grade_id = %s AND is_active = 1", (grade_id,))
            subject_result = conn.cursor.fetchone()
            if not subject_result:
                # Eğer Türkçe yoksa, ilk dersi kullan
                conn.cursor.execute("SELECT id FROM subjects WHERE grade_id = %s AND is_active = 1 LIMIT 1", (grade_id,))
                subject_result = conn.cursor.fetchone()
                if not subject_result:
                    return "Hiç ders bulunamadı", 404
                subject_id = subject_result['id']
            else:
                subject_id = subject_result['id']
            
            # Mevcut üniteleri kontrol et
            conn.cursor.execute("SELECT id, name FROM units WHERE subject_id = %s AND is_active = 1", (subject_id,))
            units = conn.cursor.fetchall()
            
            # Fiilimsiler ünitesi ID'sini bul
            conn.cursor.execute("SELECT id FROM units WHERE name = 'Fiilimsiler' AND subject_id = %s AND is_active = 1", (subject_id,))
            unit_result = conn.cursor.fetchone()
            if not unit_result:
                # Eğer Fiilimsiler yoksa, ilk üniteyi kullan
                conn.cursor.execute("SELECT id FROM units WHERE subject_id = %s AND is_active = 1 LIMIT 1", (subject_id,))
                unit_result = conn.cursor.fetchone()
                if not unit_result:
                    return "Hiç ünite bulunamadı", 404
                unit_id = unit_result['id']
            else:
                unit_id = unit_result['id']
            
            # Mevcut konuları kontrol et
            conn.cursor.execute("SELECT id, name FROM topics WHERE unit_id = %s AND is_active = 1", (unit_id,))
            topics = conn.cursor.fetchall()
            
            # Sıfat-fiil konusu ID'sini bul
            conn.cursor.execute("SELECT id FROM topics WHERE name = 'Sıfat-fiil' AND unit_id = %s AND is_active = 1", (unit_id,))
            topic_result = conn.cursor.fetchone()
            if not topic_result:
                # Eğer Sıfat-fiil yoksa, ilk konuyu kullan
                conn.cursor.execute("SELECT id FROM topics WHERE unit_id = %s AND is_active = 1 LIMIT 1", (unit_id,))
                topic_result = conn.cursor.fetchone()
                if not topic_result:
                    return "Hiç konu bulunamadı", 404
                topic_id = topic_result['id']
            else:
                topic_id = topic_result['id']
        
        # Quiz session oluştur
        quiz_config = {
            'grade_id': grade_id,
            'subject_id': subject_id,
            'unit_id': unit_id,
            'topic_id': topic_id,
            'difficulty_level': 'random',
            'quiz_mode': 'normal',  # Default to normal mode
            'timer_enabled': True,
            'timer_duration': 30,
            'question_count': 5
        }
        
        # Önce soruların var olup olmadığını kontrol et
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT COUNT(*) as count FROM questions q
                JOIN topics t ON q.topic_id = t.id
                WHERE t.id = %s AND q.is_active = 1
            """, (topic_id,))
            question_count = conn.cursor.fetchone()['count']
            
            if question_count == 0:
                # Eğer bu konuda soru yoksa, tüm konulardan soru sayısını kontrol et
                conn.cursor.execute("""
                    SELECT COUNT(*) as count FROM questions q
                    JOIN topics t ON q.topic_id = t.id
                    JOIN units u ON t.unit_id = u.id
                    WHERE u.id = %s AND q.is_active = 1
                """, (unit_id,))
                unit_question_count = conn.cursor.fetchone()['count']
                
                if unit_question_count == 0:
                    return "Bu konu ve ünite için hiç soru bulunamadı. Lütfen önce soru verilerini yükleyin.", 404
        
        session_service = QuizSessionService()
        success, result = session_service.start_quiz_session(test_user_id, quiz_config)
        
        if not success:
            error_msg = result.get('error', 'Bilinmeyen hata')
            return f"Quiz session oluşturulamadı: {error_msg}", 500
        
        # Quiz screen'e yönlendir
        session_id = result['session_id']
        
        return redirect(f'/quiz/normal?session_id={session_id}')
        
    except Exception as e:
        return f"Otomatik quiz başlatma hatası: {str(e)}", 500

@quiz_bp.route('/quiz/auto-start-educational')
def quiz_auto_start_educational():
    """4.1.9. Otomatik öğretici quiz başlatma - testuser ile 8. sınıf Türkçe sıfat-fiil konusu."""
    try:
        from app.database.db_connection import DatabaseConnection
        from app.database.user_repository import UserRepository
        from app.services.quiz_session_service import QuizSessionService
        import hashlib
        
        # Testuser'ı oluştur veya mevcut olanı bul
        with DatabaseConnection() as conn:
            # Önce testuser'ın var olup olmadığını kontrol et
            conn.cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
            user_result = conn.cursor.fetchone()
            
            if user_result:
                test_user_id = user_result['id']
            else:
                # Testuser yoksa oluştur
                
                # Basit şifre hash'i oluştur
                password_hash = hashlib.sha256("test123".encode()).hexdigest()
                
                # Direkt SQL ile kullanıcı oluştur
                conn.cursor.execute("""
                    INSERT INTO users (username, name_id, email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('testuser', 'testuser', 'testuser@example.com', password_hash, 'Test', 'User'))
                
                test_user_id = conn.cursor.lastrowid
                conn.connection.commit()
            
            # Mevcut sınıfları kontrol et
            conn.cursor.execute("SELECT id, name FROM grades WHERE is_active = 1")
            grades = conn.cursor.fetchall()
            
            # 8. sınıf ID'sini bul
            conn.cursor.execute("SELECT id FROM grades WHERE name = '8. Sınıf' AND is_active = 1")
            grade_result = conn.cursor.fetchone()
            if not grade_result:
                # Eğer 8. sınıf yoksa, ilk sınıfı kullan
                conn.cursor.execute("SELECT id FROM grades WHERE is_active = 1 LIMIT 1")
                grade_result = conn.cursor.fetchone()
                if not grade_result:
                    return "Hiç sınıf bulunamadı", 404
                grade_id = grade_result['id']
            else:
                grade_id = grade_result['id']
            
            # Mevcut dersleri kontrol et
            conn.cursor.execute("SELECT id, name FROM subjects WHERE grade_id = %s AND is_active = 1", (grade_id,))
            subjects = conn.cursor.fetchall()
            
            # Türkçe dersi ID'sini bul
            conn.cursor.execute("SELECT id FROM subjects WHERE name = 'Türkçe' AND grade_id = %s AND is_active = 1", (grade_id,))
            subject_result = conn.cursor.fetchone()
            if not subject_result:
                # Eğer Türkçe yoksa, ilk dersi kullan
                conn.cursor.execute("SELECT id FROM subjects WHERE grade_id = %s AND is_active = 1 LIMIT 1", (grade_id,))
                subject_result = conn.cursor.fetchone()
                if not subject_result:
                    return "Hiç ders bulunamadı", 404
                subject_id = subject_result['id']
            else:
                subject_id = subject_result['id']
            
            # Mevcut üniteleri kontrol et
            conn.cursor.execute("SELECT id, name FROM units WHERE subject_id = %s AND is_active = 1", (subject_id,))
            units = conn.cursor.fetchall()
            
            # Fiilimsiler ünitesi ID'sini bul
            conn.cursor.execute("SELECT id FROM units WHERE name = 'Fiilimsiler' AND subject_id = %s AND is_active = 1", (subject_id,))
            unit_result = conn.cursor.fetchone()
            if not unit_result:
                # Eğer Fiilimsiler yoksa, ilk üniteyi kullan
                conn.cursor.execute("SELECT id FROM units WHERE subject_id = %s AND is_active = 1 LIMIT 1", (subject_id,))
                unit_result = conn.cursor.fetchone()
                if not unit_result:
                    return "Hiç ünite bulunamadı", 404
                unit_id = unit_result['id']
            else:
                unit_id = unit_result['id']
            
            # Mevcut konuları kontrol et
            conn.cursor.execute("SELECT id, name FROM topics WHERE unit_id = %s AND is_active = 1", (unit_id,))
            topics = conn.cursor.fetchall()
            
            # Sıfat-fiil konusu ID'sini bul
            conn.cursor.execute("SELECT id FROM topics WHERE name = 'Sıfat-fiil' AND unit_id = %s AND is_active = 1", (unit_id,))
            topic_result = conn.cursor.fetchone()
            if not topic_result:
                # Eğer Sıfat-fiil yoksa, ilk konuyu kullan
                conn.cursor.execute("SELECT id FROM topics WHERE unit_id = %s AND is_active = 1 LIMIT 1", (unit_id,))
                topic_result = conn.cursor.fetchone()
                if not topic_result:
                    return "Hiç konu bulunamadı", 404
                topic_id = topic_result['id']
            else:
                topic_id = topic_result['id']
        
        # Quiz session oluştur
        quiz_config = {
            'grade_id': grade_id,
            'subject_id': subject_id,
            'unit_id': unit_id,
            'topic_id': topic_id,
            'difficulty_level': 'random',
            'quiz_mode': 'educational',  # Educational mode
            'timer_enabled': False,  # Educational mode doesn't use timer
            'timer_duration': 0,
            'question_count': 5
        }
        
        # Önce soruların var olup olmadığını kontrol et
        with DatabaseConnection() as conn:
            conn.cursor.execute("""
                SELECT COUNT(*) as count FROM questions q
                JOIN topics t ON q.topic_id = t.id
                WHERE t.id = %s AND q.is_active = 1
            """, (topic_id,))
            question_count = conn.cursor.fetchone()['count']
            
            if question_count == 0:
                # Eğer bu konuda soru yoksa, tüm konulardan soru sayısını kontrol et
                conn.cursor.execute("""
                    SELECT COUNT(*) as count FROM questions q
                    JOIN topics t ON q.topic_id = t.id
                    JOIN units u ON t.unit_id = u.id
                    WHERE u.id = %s AND q.is_active = 1
                """, (unit_id,))
                unit_question_count = conn.cursor.fetchone()['count']
                
                if unit_question_count == 0:
                    return "Bu konu ve ünite için hiç soru bulunamadı. Lütfen önce soru verilerini yükleyin.", 404
        
        session_service = QuizSessionService()
        success, result = session_service.start_quiz_session(test_user_id, quiz_config)
        
        if not success:
            error_msg = result.get('error', 'Bilinmeyen hata')
            return f"Öğretici quiz session oluşturulamadı: {error_msg}", 500
        
        # Quiz screen'e yönlendir
        session_id = result['session_id']
        
        return redirect(f'/quiz/educational?session_id={session_id}')
        
    except Exception as e:
        return f"Otomatik öğretici quiz başlatma hatası: {str(e)}", 500

@quiz_bp.route('/quiz/test-db')
def test_database():
    """4.1.9. Veritabanı bağlantısını test eder."""
    try:
        from app.database.db_connection import DatabaseConnection
        
        with DatabaseConnection() as conn:
            # Test basic connection
            conn.cursor.execute("SELECT 1 as test")
            result = conn.cursor.fetchone()
            
            if result and result['test'] == 1:
                return "✅ Database connection successful", 200
            else:
                return "❌ Database connection failed", 500
                
    except Exception as e:
        return f"❌ Database test error: {str(e)}", 500

@quiz_bp.route('/quiz/init-db')
def initialize_database():
    """4.1.10. Veritabanını manuel olarak başlatır."""
    try:
        from app.database.db_connection import DatabaseConnection
        from app.database.db_migrations import DatabaseMigrations
        from app.database.quiz_data_loader import QuestionLoader
        
        # Run migrations
        db_connection = DatabaseConnection()
        migrations = DatabaseMigrations(db_connection)
        migrations.run_migrations()
        
        # Load question data
        question_loader = QuestionLoader(db_connection=db_connection)
        results = question_loader.process_all_question_files()
        
        total_success = 0
        total_questions = 0
        for filename, (success, total) in results.items():
            total_success += success
            total_questions += total
        
        return f"✅ Database initialized successfully. Loaded {total_success}/{total_questions} questions.", 200
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Database initialization error: {str(e)}", 500 