import { stateManager } from './StateManager.js';
import { eventBus } from './EventBus.js';
import { ApiService } from '../services/ApiService.js';

/**
 * =============================================================================
 * QuizEngine – Sınav Motoru | Quiz Engine
 * =============================================================================
 * Çekirdek quiz mantığını, durum yönetimini ve akış kontrolünü yönetir; kurulum, veri
 * yükleme, zamanlayıcı, gezinme, cevaplama ve tamamlama adımlarını koordine eder.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Kurulum ve Başlatma | Setup & Initialization
 *    - constructor() - Servisleri kurar ve dinleyicileri bağlar.
 *    - initializeEventListeners() - Quiz akışı için tüm eventleri abone eder.
 * 2) Oturum ve Veri Yönetimi | Session & Data Management
 *    - loadQuestions() - Soruları ve oturum bilgisini yükler, state'i hazırlar.
 *    - updateSessionStatus(sessionId) - Oturum durumunu (özellikle zamanlayıcı) günceller.
 * 3) Zamanlayıcı Yönetimi | Timer Management
 *    - startTimerUpdate() - Her saniye tikler ve periyodik kaydeder.
 *    - saveTimerToDatabase(remainingTimeSeconds) - Kalan süreyi API'ye yazar.
 * 4) Quiz Navigasyonu | Quiz Navigation
 *    - nextQuestion() - Sonraki soruya geçer; yoksa tamamlama tetikler.
 *    - previousQuestion() - Önceki soruya geçer.
 *    - goToQuestion(index) - Belirtilen soruya gider ve durumu yayınlar.
 * 5) Cevaplama İşlemleri | Answering Logic
 *    - submitAnswer({ questionId, answer }) - Cevabı kaydeder ve gönderir.
 *    - removeAnswer({ questionId }) - Cevabı kaldırır ve API'ye iletir.
 *    - handleWrongAnswer(data) - Yanlış cevap kancası.
 *    - checkAnswerLocally(questionId, userAnswer) - Yerel doğruluk kontrolü.
 *    - getCorrectAnswer(questionId) - Doğru seçenek nesnesini döndürür.
 * 6) Quiz Tamamlama | Quiz Completion
 *    - completeQuiz() - Sonuçları gönderir ve yönlendirir.
 * =============================================================================
 */
export class QuizEngine {

  /* =========================================================================
   * 1) Kurulum ve Başlatma | Setup & Initialization
   * ========================================================================= */

  /**
   * constructor - Gerekli servisleri başlatır ve olay dinleyicilerini ayarlar.
   */
  constructor() {
    this.apiService = new ApiService();
    this.initializeEventListeners();
  }

  /**
   * initializeEventListeners - Quiz akışı için gerekli tüm olay dinleyicilerini
   * merkezi olarak başlatır.
   */
  initializeEventListeners() {
    eventBus.subscribe('quiz:start', this.loadQuestions.bind(this));
    eventBus.subscribe('quiz:complete', this.completeQuiz.bind(this));
    
    eventBus.subscribe('question:next', this.nextQuestion.bind(this));
    eventBus.subscribe('question:previous', this.previousQuestion.bind(this));
    eventBus.subscribe('question:goTo', ({ index }) => this.goToQuestion(index));
    
    eventBus.subscribe('answer:submit', this.submitAnswer.bind(this));
    eventBus.subscribe('answer:remove', this.removeAnswer.bind(this));
    eventBus.subscribe('answer:wrong', this.handleWrongAnswer.bind(this));
    
    // Timer'ı başlat
    this.startTimerUpdate();
  }

  /* =========================================================================
   * 2) Oturum ve Veri Yönetimi | Session & Data Management
   * ========================================================================= */

  /**
   * loadQuestions - API'den quiz sorularını ve oturum bilgilerini yükler,
   * ardından state'i (durumu) günceller.
   */
  async loadQuestions() {
    try {
      stateManager.setLoading(true);
      let sessionId = stateManager.getState('sessionId');
      
      // Session ID yoksa, global window nesnesinden almayı dener.
      if (!sessionId) {
        sessionId = window.QUIZ_CONFIG?.sessionId || window.QUIZ_SESSION_ID;
        if (sessionId) {
          stateManager.setState({ sessionId });
        }
      }
      
      if (!sessionId) {
        throw new Error('Geçerli bir oturum ID bulunamadı. Lütfen sayfayı yenileyin.');
      }

      // Soruları ve oturum bilgilerini eş zamanlı olarak çeker.
      const [questionsResp, sessionInfoResp] = await Promise.all([
        this.apiService.fetchQuestions({ sessionId }),
        this.apiService.getSessionInfo(sessionId).catch(() => ({ data: null }))
      ]);

      const responseData = questionsResp.data;
      if (!responseData || !Array.isArray(responseData.questions)) {
        throw new Error('API yanıtı geçersiz formatta veya soru listesi bulunamadı.');
      }
      
      // API'den gelen veriyi uygulamanın beklediği formata dönüştürür.
      const questions = responseData.questions.map(q => ({
        question_number: q.question_number,
        total_questions: q.total_questions,
        question: {
          id: q.question.id,
          text: q.question.text,
          explanation: q.question.explanation,
          difficulty_level: q.question.difficulty_level,
          points: q.question.points,
          subject_name: q.question.subject_name,
          topic_name: q.question.topic_name,
          options: q.question.options || []
        },
        user_answer_option_id: q.user_answer_option_id,
        progress: q.progress
      }));
      
      stateManager.setQuestions(questions);
      
      // Quiz ile ilgili temel bilgileri state'e kaydeder.
      stateManager.setState({ 
        quizMode: 'educational',
        sessionId: responseData.session_id || sessionId
      });

      // Oturum meta verilerini (sınıf, konu vb.) işler.
      const sessionMeta = sessionInfoResp?.data?.session;
      if (sessionMeta) {
        stateManager.setMetadata({
          grade: sessionMeta.grade || sessionMeta.grade_name,
          subject: sessionMeta.subject || sessionMeta.subject_name,
          unit: sessionMeta.unit || sessionMeta.unit_name,
          topic: sessionMeta.topic || sessionMeta.topic_name,
          difficulty: sessionMeta.difficulty || sessionMeta.difficulty_level
        });

        // Oturumdan gelen zamanlayıcı bilgilerini state'e uygular.
        if (typeof sessionMeta.remaining_time_seconds === 'number' || typeof sessionMeta.timer_duration === 'number') {
          stateManager.setState({
            timer: {
              ...stateManager.getState('timer'),
              enabled: !!sessionMeta.timer_enabled,
              remainingTimeSeconds: sessionMeta.remaining_time_seconds ?? stateManager.getState('timer').remainingTimeSeconds,
              totalTime: sessionMeta.timer_duration ?? stateManager.getState('timer').totalTime
            }
          }, 'INIT_TIMER_FROM_SESSION');
        }
      }
      
      await this.updateSessionStatus(sessionId);
      
      console.info('[QuizEngine] Quiz başarıyla yüklendi ve başlatıldı.', stateManager.getState());
      eventBus.publish('quiz:questionsLoaded');
      
    } catch (error) {
      console.error('Sorular yüklenirken hata oluştu:', error);
      stateManager.setError({
        message: 'Sorular yüklenirken bir hata oluştu.',
        details: error.message
      });
    } finally {
      stateManager.setLoading(false);
    }
  }

  /**
   * updateSessionStatus - Oturumun mevcut durumunu (özellikle zamanlayıcı) API'den
   * alarak günceller.
   * @param {string} sessionId - Güncellenecek oturumun ID'si.
   */
  async updateSessionStatus(sessionId) {
    try {
      const response = await this.apiService.getSessionStatus(sessionId);
      if (response.data) {
        const statusData = response.data;
        stateManager.setState({
          timer: {
            enabled: statusData.timer_enabled || false,
            remainingTimeSeconds: statusData.remaining_time_seconds || 0,
            totalTime: statusData.timer_duration || 0
          }
        }, 'UPDATE_SESSION_STATUS');
      }
    } catch (error) {
      console.warn('Oturum durumu güncellenirken bir hata oluştu (kritik değil):', error);
    }
  }

  /* =========================================================================
   * 3) Zamanlayıcı Yönetimi | Timer Management
   * ========================================================================= */

  /**
   * startTimerUpdate - Her saniye zamanlayıcıyı güncelleyen ve periyodik olarak
   * sunucuya kaydeden bir interval başlatır.
   */
  startTimerUpdate() {
    let saveCounter = 0; // Her 10 saniyede bir kaydetmek için sayaç.
    
    setInterval(() => {
      const timer = stateManager.getState('timer');
      
      if (timer.enabled && timer.remainingTimeSeconds > 0) {
        const newRemainingTime = timer.remainingTimeSeconds - 1;
        
        stateManager.setState({
          timer: { ...timer, remainingTimeSeconds: newRemainingTime }
        }, 'TIMER_TICK');
        
        // Her 10 saniyede bir zamanı veritabanına kaydeder.
        saveCounter++;
        if (saveCounter >= 10) {
          this.saveTimerToDatabase(newRemainingTime);
          saveCounter = 0;
        }
        
        // Süre bittiğinde quiz'i otomatik olarak tamamlar.
        if (newRemainingTime <= 0) {
          eventBus.publish('quiz:complete');
        }
      }
    }, 1000);
  }
  
  /**
   * saveTimerToDatabase - Kalan süreyi periyodik olarak veritabanına kaydeder.
   * @param {number} remainingTimeSeconds - Veritabanına kaydedilecek kalan süre.
   */
  async saveTimerToDatabase(remainingTimeSeconds) {
    try {
      const sessionId = stateManager.getState('sessionId');
      if (!sessionId) return;
      
      await this.apiService.updateTimer({ sessionId, remainingTimeSeconds });
    } catch (error) {
      console.warn('Zamanlayıcı veritabanına kaydedilirken hata oluştu (kritik değil):', error);
    }
  }

  /* =========================================================================
   * 4) Quiz Navigasyonu | Quiz Navigation
   * ========================================================================= */

  /**
   * nextQuestion - Mevcut sorudan bir sonraki soruya geçer.
   * Eğer son sorudaysa, quiz'i tamamlama olayını tetikler.
   */
  nextQuestion() {
    const { currentQuestionIndex, questions } = stateManager.getState();
    const nextIndex = currentQuestionIndex + 1;
    
    if (nextIndex < questions.length) {
      this.goToQuestion(nextIndex);
    } else {
      eventBus.publish('quiz:complete');
    }
  }

  /**
   * previousQuestion - Mevcut sorudan bir önceki soruya geçer.
   */
  previousQuestion() {
    const { currentQuestionIndex } = stateManager.getState();
    const prevIndex = currentQuestionIndex - 1;
    if (prevIndex >= 0) {
      this.goToQuestion(prevIndex);
    }
  }

  /**
   * goToQuestion - Belirtilen indeksteki soruya doğrudan gider.
   * @param {number} index - Gidilecek sorunun indeksi.
   */
  async goToQuestion(index) {
    const currentIndex = stateManager.getState('currentQuestionIndex');
    stateManager.setCurrentQuestionIndex(index);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    eventBus.publish('question:navigated', {
      fromIndex: currentIndex,
      toIndex: index,
      type: index > currentIndex ? 'forward' : 'backward'
    });
    
    const sessionId = stateManager.getState('sessionId');
    if (sessionId) {
      await this.updateSessionStatus(sessionId);
    }
  }

  /* =========================================================================
   * 5) Cevaplama İşlemleri | Answering Logic
   * ========================================================================= */

  /**
   * submitAnswer - Kullanıcının cevabını alır, yerel state'i günceller ve
   * sunucuya gönderir. Cevabın doğruluğuna göre akışı yönlendirir.
   * @param {object} params - { questionId, answer }
   */
  async submitAnswer({ questionId, answer }) {
    if (stateManager.getState('isSubmitting')) return;
    
    try {
      stateManager.setState({ isSubmitting: true }, 'SUBMIT_ANSWER_START');
      
      const sessionId = stateManager.getState('sessionId');
      if (!sessionId || questionId == null || answer == null) {
        throw new Error('Cevap göndermek için oturum, soru veya cevap ID eksik.');
      }
      
      // UI'ın anında tepki vermesi için cevabı hemen state'e kaydeder.
      stateManager.setAnswer(questionId, answer);
      
      // Frontend-only validation: Sadece yerel doğrulama kullan
      const isCorrect = this.checkAnswerLocally(questionId, answer);
      console.log('[QuizEngine] Frontend validation result:', isCorrect, 'for answer:', answer, 'question:', questionId);
      
      // Debug: Doğru cevabı da logla
      const correctAnswer = this.getCorrectAnswer(questionId);
      console.log('[QuizEngine] Correct answer for question', questionId, ':', correctAnswer?.id, correctAnswer);
      
      // API'ye cevabı gönder (sadece kaydetmek için, doğruluk kontrolü yapmadan)
      try {
        await this.apiService.submitAnswer({ sessionId, questionId, answer });
      } catch (error) {
        console.warn('[QuizEngine] Answer save failed (non-critical):', error);
      }
      
      stateManager.setState({ isSubmitting: false }, 'SUBMIT_ANSWER_END');
      
      const isEducationalMode = stateManager.getState('quizMode') === 'educational';
      if (isEducationalMode && !isCorrect) {
        eventBus.publish('answer:wrong', {
          questionId: questionId,
          userAnswer: answer,
          correctAnswer: this.getCorrectAnswer(questionId)
        });
        return;
      }
      
      // Doğru cevap veya normal modda, kısa bir beklemenin ardından sonraki soruya geçer.
      setTimeout(() => this.nextQuestion(), 300);
      
    } catch (error) {
      console.error('Cevap gönderilirken hata oluştu:', error);
      stateManager.setError({
        message: 'Cevap gönderilirken bir hata oluştu.',
        details: error.message
      });
      stateManager.setState({ isSubmitting: false }, 'SUBMIT_ANSWER_ERROR');
    }
  }

  /**
   * removeAnswer - Bir soruya verilen cevabı kaldırır.
   * @param {object} params - { questionId }
   */
  async removeAnswer({ questionId }) {
    if (stateManager.getState('isSubmitting')) return;
    
    try {
      const sessionId = stateManager.getState('sessionId');
      if (!sessionId || !questionId) {
        throw new Error('Cevap kaldırmak için gerekli bilgiler eksik.');
      }
      
      // Cevabı anında state'den kaldırır.
      stateManager.removeAnswer(questionId);
      
      // API'ye cevabı kaldırma isteği gönderir (answer: null).
      await this.apiService.submitAnswer({ sessionId, questionId, answer: null });
      
    } catch (error) {
      console.error('Cevap kaldırılırken hata oluştu:', error);
      stateManager.setError({
        message: 'Cevap kaldırılırken bir hata oluştu.',
        details: error.message
      });
    }
  }

  /**
   * handleWrongAnswer - 'educational' modda yanlış cevap verildiğinde tetiklenir.
   * Bu fonksiyon, yanlış cevap durumunda yapılacak özel işlemleri (örn. AI chat'e bilgi gönderme)
   * yönetmek için bir kancadır (hook).
   * @param {object} data - { questionId, userAnswer, correctAnswer }
   */
  handleWrongAnswer(data) {
    // Bu fonksiyon, yanlış cevap verildiğinde özel mantık eklemek için bir yer tutucudur.
    // Örneğin, kullanıcıya ek yardım sunmak veya analitik verisi göndermek için kullanılabilir.
    console.log('Yanlış cevap işleniyor:', data);
  }

  /**
   * checkAnswerLocally - Sunucu yanıtı olmadığında bir cevabın doğruluğunu
   * yerel veriye göre kontrol eder.
   * @param {number|string} questionId - Soru ID'si.
   * @param {string} userAnswer - Kullanıcının verdiği cevap ID'si.
   * @returns {boolean} Cevabın doğru olup olmadığını döndürür.
   */
  checkAnswerLocally(questionId, userAnswer) {
    console.log('[DEBUG] checkAnswerLocally called:', { questionId, userAnswer });
    
    const st = stateManager.getState();
    const q = (st.questions || []).find(item => String(item?.question?.id) === String(questionId));
    console.log('[DEBUG] Found question:', q);
    
    const options = q?.question?.options || [];
    console.log('[DEBUG] Question options:', options);
    
    const correct = options.find(o => {
      if (!o) return false;
      console.log('[DEBUG] Checking option:', o, {
        is_correct: o.is_correct,
        isCorrect: o.isCorrect,
        correct: o.correct
      });
      
      const result = (o.is_correct === true || o.is_correct === 1 || o.is_correct === '1') ||
                     (o.isCorrect === true || o.isCorrect === 1 || o.isCorrect === '1') ||
                     (o.correct === true || o.correct === 1 || o.correct === '1');
      
      console.log('[DEBUG] Option check result:', result);
      return result;
    });
    
    console.log('[DEBUG] Found correct option:', correct);
    
    const finalResult = correct ? String(correct.id) === String(userAnswer) : false;
    console.log('[DEBUG] Final validation result:', finalResult, {
      correctId: correct?.id,
      userAnswer,
      comparison: `${correct?.id} === ${userAnswer}`
    });
    
    return finalResult;
  }

  /**
   * getCorrectAnswer - Belirtilen sorunun doğru cevap seçeneği nesnesini döndürür.
   * @param {number|string} questionId - Soru ID'si.
   * @returns {object|null} Doğru cevap seçeneği veya bulunamazsa null.
   */
  getCorrectAnswer(questionId) {
    const st = stateManager.getState();
    const q = (st.questions || []).find(item => String(item?.question?.id) === String(questionId));
    const options = q?.question?.options || [];
    return options.find(o => {
      if (!o) return false;
      // Tüm olası doğru cevap formatlarını kontrol et
      return (o.is_correct === true || o.is_correct === 1 || o.is_correct === '1') ||
             (o.isCorrect === true || o.isCorrect === 1 || o.isCorrect === '1') ||
             (o.correct === true || o.correct === 1 || o.correct === '1');
    }) || null;
  }

  /* =========================================================================
   * 6) Frontend Scoring | Frontend Puanlama
   * ========================================================================= */

  /**
   * calculateFrontendScore - Frontend'de quiz sonuçlarını hesaplar
   * @returns {Object} Quiz sonuçları
   */
  calculateFrontendScore() {
    const { questions, answers } = stateManager.getState();
    let correctCount = 0;
    let totalScore = 0;
    const questionResults = [];

    questions.forEach(questionItem => {
      const questionId = questionItem.question.id;
      const userAnswer = answers.get(questionId);
      const isCorrect = userAnswer ? this.checkAnswerLocally(questionId, userAnswer) : false;
      const points = questionItem.question.points || 1;

      if (isCorrect) {
        correctCount++;
        totalScore += points;
      }

      questionResults.push({
        questionId,
        userAnswer,
        correctAnswer: this.getCorrectAnswer(questionId),
        isCorrect,
        points: isCorrect ? points : 0
      });
    });

    const totalQuestions = questions.length;
    const percentage = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

    return {
      correctCount,
      totalQuestions,
      totalScore,
      percentage,
      questionResults,
      timestamp: new Date().toISOString()
    };
  }

  /* =========================================================================
   * 7) Quiz Tamamlama | Quiz Completion
   * ========================================================================= */

  /**
   * completeQuiz - Quiz'i sonlandırır, frontend'de hesaplanan sonuçları kullanır
   */
  async completeQuiz() {
    if (stateManager.getState('isSubmitting')) return;
    
    try {
      stateManager.setState({ isLoading: true, isSubmitting: true }, 'QUIZ_COMPLETE_START');
      
      const sessionId = stateManager.getState('sessionId');
      const answers = stateManager.getState('answers');
      
      // Frontend'de sonuçları hesapla
      const frontendResults = this.calculateFrontendScore();
      console.log('[QuizEngine] Frontend calculated results:', frontendResults);
      
      // API'ye sadece cevapları gönder (sonuç hesaplama için değil)
      try {
        await this.apiService.completeQuiz({ sessionId, answers });
      } catch (error) {
        console.warn('[QuizEngine] API completion failed (non-critical):', error);
      }
      
      stateManager.setState({ quizCompleted: true, results: frontendResults }, 'QUIZ_COMPLETED');
      eventBus.publish('quiz:completed', { results: frontendResults });
      
      // Kullanıcıyı sonuç sayfasına yönlendir.
      window.location.href = `/quiz/results?session_id=${sessionId}`;
      
    } catch (error) {
      console.error('Quiz tamamlanırken hata oluştu:', error);
      stateManager.setError({
        message: 'Sınav tamamlanırken bir hata oluştu.',
        details: error.message
      });
    } finally {
      stateManager.setState({ isLoading: false, isSubmitting: false }, 'QUIZ_COMPLETE_END');
    }
  }
}
