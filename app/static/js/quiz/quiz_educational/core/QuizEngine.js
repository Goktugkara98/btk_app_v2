import { stateManager } from './StateManager.js';
import { eventBus } from './EventBus.js';
import { ApiService } from '../services/ApiService.js';

/**
 * QuizEngine - Çekirdek quiz mantığını ve akış kontrolünü yönetir.
 */
 /*
  * İÇİNDEKİLER (Table of Contents)
  * - [1] Kurulum
  *   - [1.1] constructor()
  *   - [1.2] initializeEventListeners()
  * - [2] Zamanlayıcı (Timer)
  *   - [2.1] startTimerUpdate()
  *   - [2.2] saveTimerToDatabase(remainingTimeSeconds)
  * - [3] Veri ve Oturum
  *   - [3.1] loadQuestions()
  *   - [3.2] updateSessionStatus(sessionId)
  * - [4] Navigasyon
  *   - [4.1] nextQuestion()
  *   - [4.2] previousQuestion()
  *   - [4.3] goToQuestion(index)
  * - [5] Cevap İşleme
  *   - [5.1] submitAnswer({ questionId, answer })
  *   - [5.2] removeAnswer({ questionId })
  *   - [5.3] checkAnswerLocally(questionId, userAnswer)
  *   - [5.4] getCorrectAnswer(questionId)
  *   - [5.5] handleWrongAnswer(data)
  * - [6] Tamamlama
  *   - [6.1] completeQuiz()
  */
 export class QuizEngine {
  /**
   * [1.1] constructor - Kaynakları ve event dinleyicilerini başlatır.
   * Kategori: [1] Kurulum
   */
  constructor() {
    this.apiService = new ApiService();
    this.initializeEventListeners();
  }

  /**
   * [1.2] initializeEventListeners - Quiz akışı için olay dinleyicilerini başlatır.
   * Kategori: [1] Kurulum
   */
  initializeEventListeners() {
    eventBus.subscribe('quiz:start', this.loadQuestions.bind(this));
    eventBus.subscribe('question:next', this.nextQuestion.bind(this));
    eventBus.subscribe('question:previous', this.previousQuestion.bind(this));
    eventBus.subscribe('question:goTo', ({ index }) => this.goToQuestion(index));
    
    // 'option:selected' kaldırıldı, doğrudan 'answer:submit' dinleniyor.
    eventBus.subscribe('answer:submit', this.submitAnswer.bind(this));
    
    // Cevap kaldırma olayını dinle
    eventBus.subscribe('answer:remove', this.removeAnswer.bind(this));
    
    // Yanlış cevap olayını dinle (şimdilik boş)
    eventBus.subscribe('answer:wrong', this.handleWrongAnswer.bind(this));
    
    eventBus.subscribe('quiz:complete', this.completeQuiz.bind(this));
    
    // Timer güncelleme için interval başlat
    this.startTimerUpdate();
  }

  /**
   * [2.1] startTimerUpdate - Timer'ı otomatik olarak günceller.
   * Kategori: [2] Zamanlayıcı (Timer)
   */
  startTimerUpdate() {
    let saveCounter = 0; // 10 saniyede bir kaydetmek için sayaç
    
    setInterval(() => {
      const timer = stateManager.getState('timer');
      
      if (timer.enabled && timer.remainingTimeSeconds > 0) {
        const newRemainingTime = timer.remainingTimeSeconds - 1;
        
        stateManager.setState({
          timer: {
            ...timer,
            remainingTimeSeconds: newRemainingTime
          }
        }, 'TIMER_TICK');
        
        // 10 saniyede bir veritabanına kaydet
        saveCounter++;
        if (saveCounter >= 10) {
          this.saveTimerToDatabase(newRemainingTime);
          saveCounter = 0;
        }
        
        // Süre bittiğinde quiz'i otomatik tamamla
        if (newRemainingTime <= 0) {
          eventBus.publish('quiz:complete');
        }
      }
    }, 1000);
  }
  
  /**
   * [2.2] saveTimerToDatabase - Timer'ı veritabanına kaydeder.
   * Kategori: [2] Zamanlayıcı (Timer)
   */
  async saveTimerToDatabase(remainingTimeSeconds) {
    try {
      const sessionId = stateManager.getState('sessionId');
      if (!sessionId) {
        return;
      }
      
      // Timer'ı veritabanına kaydetmek için API çağrısı
      await this.apiService.updateTimer({ sessionId, remainingTimeSeconds });
      
    } catch (error) {
      // Timer kaydedilirken hata oluştu
    }
  }

  /**
   * [3.1] loadQuestions - Quiz için soruları yükler.
   * Kategori: [3] Veri ve Oturum
   */
  async loadQuestions() {
    try {
      stateManager.setLoading(true);
      let sessionId = stateManager.getState('sessionId');
      
      // Session ID yoksa window'dan almayı dene
      if (!sessionId) {
        if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
          sessionId = window.QUIZ_CONFIG.sessionId;
          stateManager.setState({ sessionId });
        } else if (window.QUIZ_SESSION_ID) {
          sessionId = window.QUIZ_SESSION_ID;
          stateManager.setState({ sessionId });
        }
      }
      
      if (!sessionId) {
        throw new Error('Geçerli bir oturum ID bulunamadı. Lütfen sayfayı yenileyin.');
      }
      // Sorular ve oturum bilgisini aynı anda al
      const [questionsResp, sessionInfoResp] = await Promise.all([
        this.apiService.fetchQuestions({ sessionId }),
        this.apiService.getSessionInfo(sessionId).catch(() => ({ data: null }))
      ]);

      const response = questionsResp;

      if (!response.data || !Array.isArray(response.data.questions)) {
        throw new Error('API yanıtı geçersiz formatta.');
      }
      
      // API'den gelen soru formatını JavaScript'in beklediği formata dönüştür
      const questions = response.data.questions.map((q, index) => {
        return {
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
        };
      });
      
      stateManager.setQuestions(questions);
      // Türetilmiş map'leri oluştur (yerel doğrulama ve hızlı erişim için)
      stateManager.buildDerivedMaps();
      
      // Quiz modunu educational olarak ayarla
      stateManager.setState({ quizMode: 'educational' });
      
      // Session bilgilerini güncelle
      if (response.data.session_id) {
        stateManager.setState({ sessionId: response.data.session_id });
      }
      
      // Timer bilgilerini güncelle
      if (response.data.total_questions) {
        stateManager.setState({ totalQuestions: response.data.total_questions });
      }

      // Session meta bilgisini state'e işle (varsa)
      const sessionMetaWrapper = sessionInfoResp?.data || null;
      const sess = sessionMetaWrapper?.session || null;
      if (sess) {
        stateManager.setMetadata({
          grade: sess.grade || sess.grade_name || null,
          subject: sess.subject || sess.subject_name || null,
          unit: sess.unit || sess.unit_name || null,
          topic: sess.topic || sess.topic_name || null,
          difficulty: sess.difficulty || sess.difficulty_level || null
        });
        // Timer başlangıç bilgileri (varsa)
        if (typeof sess.remaining_time_seconds === 'number' || typeof sess.timer_duration === 'number') {
          stateManager.setState({
            timer: {
              ...stateManager.getState('timer'),
              enabled: !!sess.timer_enabled,
              remainingTimeSeconds: (typeof sess.remaining_time_seconds === 'number') ? sess.remaining_time_seconds : stateManager.getState('timer').remainingTimeSeconds,
              totalTime: (typeof sess.timer_duration === 'number') ? sess.timer_duration : stateManager.getState('timer').totalTime
            }
          }, 'INIT_TIMER_FROM_SESSION');
        }
      }
      
      // Session status'u al ve timer bilgilerini güncelle
      await this.updateSessionStatus(sessionId);
      
      // Sayfa ilk yüklendiğinde oluşan başlangıç durumunu tek bir info log ile kaydet
      const initialLog = {
        sessionId: stateManager.getState('sessionId'),
        totalQuestions: stateManager.getState('totalQuestions') ?? stateManager.getState('questions')?.length,
        quizMode: stateManager.getState('quizMode'),
        timer: stateManager.getState('timer'),
        metadata: stateManager.getState('metadata'),
        currentQuestionIndex: stateManager.getState('currentQuestionIndex') ?? 0,
        questionsCount: stateManager.getState('questions')?.length,
        questions: stateManager.getState('questions')
      };
      console.info('[QuizEducational] Initial load state', initialLog);

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
   * [4.1] nextQuestion - Sonraki soruya geçer.
   * Kategori: [4] Navigasyon
   */
  nextQuestion() {
    const { currentQuestionIndex, questions } = stateManager.getState();
    const nextIndex = currentQuestionIndex + 1;
    
    if (nextIndex < questions.length) {
      this.goToQuestion(nextIndex);
    } else {
      // Son sorudayken 'Sonraki Soru' butonu 'Quizi Bitir'e dönüşür ve bu olayı tetikler.
      eventBus.publish('quiz:complete');
    }
  }

  /**
   * [4.2] previousQuestion - Önceki soruya geçer.
   * Kategori: [4] Navigasyon
   */
  previousQuestion() {
    const { currentQuestionIndex } = stateManager.getState();
    const prevIndex = currentQuestionIndex - 1;
    if (prevIndex >= 0) {
      this.goToQuestion(prevIndex);
    }
  }

  /**
   * [4.3] goToQuestion - Belirtilen index'teki soruya gider.
   * Kategori: [4] Navigasyon
   * @param {number} index - Gidilecek sorunun index'i.
   */
  async goToQuestion(index) {
    const currentIndex = stateManager.getState('currentQuestionIndex');
    const navigationType = index > currentIndex ? 'forward' : 'backward';
    
    stateManager.setCurrentQuestionIndex(index);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Navigasyon event'ini yayınla
    eventBus.publish('question:navigated', {
      fromIndex: currentIndex,
      toIndex: index,
      type: navigationType
    });
    
    // Soru değiştiğinde session status'u güncelle (navbar bilgileri için)
    const sessionId = stateManager.getState('sessionId');
    if (sessionId) {
      await this.updateSessionStatus(sessionId);
    }
  }

  /**
   * [5.1] submitAnswer - Bir cevabı sunucuya gönderir.
   * Kategori: [5] Cevap İşleme
   * @param {Object} answerData - { questionId, answer }
   */
  async submitAnswer({ questionId, answer }) {
    // Eğer zaten bir gönderme işlemi varsa, tekrar göndermeyi engelle.
    if (stateManager.getState('isSubmitting')) {
      return;
    }
    
    try {
      // Gönderme başladığında state'i güncelle (UI'ı kilitlemek için).
      stateManager.setState({ isSubmitting: true }, 'SUBMIT_ANSWER_START');
      
      const sessionId = stateManager.getState('sessionId');
      if (sessionId == null || questionId == null || answer == null) {
        throw new Error('Cevap göndermek için gerekli bilgiler eksik.');
      }
      
      // Cevabı anında state'e kaydet (UI'ın hızlı güncellenmesi için).
      stateManager.setAnswer(questionId, answer);
      
      // Sunucuya gönder ve yanıta göre doğruluk belirle (sunucu yoksa yerel kontrol)
      const response = await this.apiService.submitAnswer({ sessionId, questionId, answer });
      const serverIsCorrect = response?.data?.is_correct;
      const isCorrect = (typeof serverIsCorrect === 'boolean') ? serverIsCorrect : this.checkAnswerLocally(questionId, answer);
      
      // Cevabı gönderdikten hemen sonra isSubmitting'i false yap
      stateManager.setState({ isSubmitting: false }, 'SUBMIT_ANSWER_END');
      
      // Educational modda yanlış cevap verilirse farklı event tetikle
      const isEducationalMode = stateManager.getState('quizMode') === 'educational';
      
      if (isEducationalMode && !isCorrect) {
        // Yanlış cevap - yeni event tetikle
        eventBus.publish('answer:wrong', {
          questionId: questionId,
          userAnswer: answer,
          correctAnswer: this.getCorrectAnswer(questionId)
        });
        return;
      }
      
      // Doğru cevap veya normal mod - kısa bir bekleme sonrası sonraki soruya geç
      setTimeout(() => this.nextQuestion(), 300);
      
    } catch (error) {
      console.error('Cevap gönderilirken hata oluştu:', error);
      stateManager.setError({
        message: 'Cevap gönderilirken bir hata oluştu.',
        details: error.message
      });
      // Hata durumunda da isSubmitting'i false yap
      stateManager.setState({ isSubmitting: false }, 'SUBMIT_ANSWER_ERROR');
    }
  }

  /**
   * [5.3] checkAnswerLocally - JavaScript tarafında cevap kontrolü yapar.
   * Kategori: [5] Cevap İşleme
   * @param {number} questionId - Soru ID'si
   * @param {string} userAnswer - Kullanıcının cevabı
   * @returns {boolean} Cevap doğru mu?
   */
  checkAnswerLocally(questionId, userAnswer) {
    // Önce türetilmiş haritaları kullan
    const correctMap = stateManager.getState('correctOptionByQuestionId');
    const correctFromMap = correctMap?.get(Number(questionId)) || correctMap?.get(String(questionId));
    if (correctFromMap) {
      return String(correctFromMap.id) === String(userAnswer);
    }

    // Geriye dönük uyumluluk: doğrudan sorulardan tara
    const { questions } = stateManager.getState();
    const question = questions.find(q => q.question.id === parseInt(questionId, 10));
    if (!question || !question.question.options) return false;
    let correctOption = question.question.options.find(option => option.is_correct === true)
      || question.question.options.find(option => option.isCorrect === true)
      || question.question.options.find(option => option.correct === true)
      || question.question.options.find(option => option.is_correct === 1)
      || question.question.options.find(option => option.correct === 1);
    if (!correctOption) return false;
    return String(correctOption.id) === String(userAnswer);
  }

  /**
   * [5.4] getCorrectAnswer - Belirtilen sorunun doğru cevabını döndürür.
   * Kategori: [5] Cevap İşleme
   * @param {number} questionId - Soru ID'si
   * @returns {Object|null} Doğru cevap seçeneği
   */
  getCorrectAnswer(questionId) {
    const correctMap = stateManager.getState('correctOptionByQuestionId');
    const fromMap = correctMap?.get(Number(questionId)) || correctMap?.get(String(questionId));
    if (fromMap) return fromMap;
    const { questions } = stateManager.getState();
    const question = questions.find(q => q.question.id === parseInt(questionId, 10));
    if (!question || !question.question.options) return null;
    return (
      question.question.options.find(option => option.is_correct === true)
      || question.question.options.find(option => option.isCorrect === true)
      || question.question.options.find(option => option.correct === true)
      || question.question.options.find(option => option.is_correct === 1)
      || question.question.options.find(option => option.correct === 1)
    ) || null;
  }

  /**
   * [5.5] handleWrongAnswer - Yanlış cevap verildiğinde çalışacak fonksiyon (şimdilik boş).
   * Kategori: [5] Cevap İşleme
   * @param {Object} data - { questionId, userAnswer, correctAnswer }
   */
  handleWrongAnswer(data) {
    // Şimdilik boş - buraya yanlış cevap işlemleri eklenecek
    // info-level logs removed
    
    // TODO: Burada yanlış cevap için özel işlemler yapılacak
    // Örneğin: AI chat'e bilgi gönderme, UI güncelleme, vs.
  }

  /**
   * [5.2] removeAnswer - Bir cevabı kaldırır.
   * Kategori: [5] Cevap İşleme
   * @param {Object} answerData - { questionId }
   */
  async removeAnswer({ questionId }) {
    // Eğer zaten bir gönderme işlemi varsa, tekrar göndermeyi engelle.
    if (stateManager.getState('isSubmitting')) {
      return;
    }
    
    try {
      const sessionId = stateManager.getState('sessionId');
      if (!sessionId || !questionId) {
        throw new Error('Cevap kaldırmak için gerekli bilgiler eksik.');
      }
      
      // Cevabı anında state'den kaldır (UI'ın hızlı güncellenmesi için).
      stateManager.removeAnswer(questionId);
      
      // API'ye cevabı kaldırma isteği gönder (null değer)
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
   * [3.2] updateSessionStatus - Session status'unu günceller ve timer bilgilerini alır.
   * Kategori: [3] Veri ve Oturum
   */
  async updateSessionStatus(sessionId) {
    try {
      const response = await this.apiService.getSessionStatus(sessionId);
      if (response.data) {
        const statusData = response.data;
        
        // Sadece timer bilgilerini güncelle (navbar bilgileri artık aktif sorudan alınıyor)
        stateManager.setState({
          timer: {
            enabled: statusData.timer_enabled || false,
            remainingTimeSeconds: statusData.remaining_time_seconds || 0,
            totalTime: statusData.timer_duration || 0
          }
        }, 'UPDATE_SESSION_STATUS');
      }
    } catch (error) {
      // Session status güncellenirken hata oluştu
    }
  }

  /**
   * [6.1] completeQuiz - Quizi tamamlar ve sonuçları gösterir.
   * Kategori: [6] Tamamlama
   */
  async completeQuiz() {
    if (stateManager.getState('isSubmitting')) return;
    
    try {
      stateManager.setState({ isLoading: true, isSubmitting: true }, 'QUIZ_COMPLETE_START');
      
      const sessionId = stateManager.getState('sessionId');
      const answers = stateManager.getState('answers');
      
      const results = await this.apiService.completeQuiz({ sessionId, answers });
      
      stateManager.setState({ quizCompleted: true, results }, 'QUIZ_COMPLETED');
      eventBus.publish('quiz:completed', { results });
      
      // Sonuç sayfasına yönlendir
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
