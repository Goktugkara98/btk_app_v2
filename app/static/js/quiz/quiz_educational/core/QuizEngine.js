import { stateManager } from './StateManager.js';
import { eventBus } from './EventBus.js';
import { ApiService } from '../services/ApiService.js';

/**
 * QuizEngine - Çekirdek quiz mantığını ve akış kontrolünü yönetir.
 */
export class QuizEngine {
  constructor() {
    this.apiService = new ApiService();
    this.initializeEventListeners();
  }

  /**
   * Quiz akışı için olay dinleyicilerini başlatır.
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
   * Timer'ı otomatik olarak günceller.
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
   * Timer'ı veritabanına kaydeder.
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
   * Quiz için soruları yükler.
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
      
      const response = await this.apiService.fetchQuestions({ sessionId });

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
      
      // Session status'u al ve timer bilgilerini güncelle
      await this.updateSessionStatus(sessionId);
      
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
   * Sonraki soruya geçer.
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
   * Önceki soruya geçer.
   */
  previousQuestion() {
    const { currentQuestionIndex } = stateManager.getState();
    const prevIndex = currentQuestionIndex - 1;
    if (prevIndex >= 0) {
      this.goToQuestion(prevIndex);
    }
  }

  /**
   * Belirtilen index'teki soruya gider.
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
   * Bir cevabı sunucuya gönderir.
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
      if (!sessionId || !questionId || !answer) {
        throw new Error('Cevap göndermek için gerekli bilgiler eksik.');
      }
      
      // Cevabı anında state'e kaydet (UI'ın hızlı güncellenmesi için).
      stateManager.setAnswer(questionId, answer);
      
      // JavaScript tarafında cevap kontrolü yap
      const isCorrect = this.checkAnswerLocally(questionId, answer);
      
      const response = await this.apiService.submitAnswer({ sessionId, questionId, answer });
      
      // Cevabı gönderdikten hemen sonra isSubmitting'i false yap
      stateManager.setState({ isSubmitting: false }, 'SUBMIT_ANSWER_END');
      
      // Educational modda yanlış cevap verilirse farklı event tetikle
      const isEducationalMode = stateManager.getState('quizMode') === 'educational';
      
      // Debug log ekle
      console.log(`[QuizEngine] Cevap kontrolü: QuestionID=${questionId}, UserAnswer=${answer}, IsCorrect=${isCorrect}, Mode=${isEducationalMode}`);
      
      if (isEducationalMode && !isCorrect) {
        // Yanlış cevap - yeni event tetikle
        console.log(`[QuizEngine] Yanlış cevap tespit edildi! answer:wrong event'i tetikleniyor...`);
        eventBus.publish('answer:wrong', {
          questionId: questionId,
          userAnswer: answer,
          correctAnswer: this.getCorrectAnswer(questionId)
        });
        return;
      }
      
      // Doğru cevap veya normal mod - kısa bir bekleme sonrası sonraki soruya geç
      console.log(`[QuizEngine] Doğru cevap veya normal mod - sonraki soruya geçiliyor...`);
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
   * JavaScript tarafında cevap kontrolü yapar.
   * @param {number} questionId - Soru ID'si
   * @param {string} userAnswer - Kullanıcının cevabı
   * @returns {boolean} Cevap doğru mu?
   */
  checkAnswerLocally(questionId, userAnswer) {
    const { questions } = stateManager.getState();
    const question = questions.find(q => q.question.id === parseInt(questionId, 10));
    
    if (!question || !question.question.options) {
      console.log(`[QuizEngine] Soru bulunamadı veya seçenekler yok: QuestionID=${questionId}`);
      return false;
    }
    
    // Soru seçeneklerinin yapısını debug et
    console.log(`[QuizEngine] Soru seçenekleri yapısı:`, question.question.options);
    
    // Doğru cevabı bul - farklı alan adlarını dene
    let correctOption = question.question.options.find(option => option.is_correct === true);
    
    // Eğer is_correct bulunamazsa, diğer olası alan adlarını dene
    if (!correctOption) {
      correctOption = question.question.options.find(option => option.isCorrect === true);
    }
    if (!correctOption) {
      correctOption = question.question.options.find(option => option.correct === true);
    }
    if (!correctOption) {
      correctOption = question.question.options.find(option => option.is_correct === 1);
    }
    if (!correctOption) {
      correctOption = question.question.options.find(option => option.correct === 1);
    }
    
    if (!correctOption) {
      console.log(`[QuizEngine] Doğru cevap bulunamadı: QuestionID=${questionId}`);
      console.log(`[QuizEngine] Tüm seçenekler:`, question.question.options);
      return false;
    }
    
    // Kullanıcının cevabı ile doğru cevabı karşılaştır
    const isCorrect = String(correctOption.id) === String(userAnswer);
    
    console.log(`[QuizEngine] Cevap kontrolü detayları:`);
    console.log(`  - QuestionID: ${questionId}`);
    console.log(`  - UserAnswer: ${userAnswer} (${typeof userAnswer})`);
    console.log(`  - CorrectAnswer: ${correctOption.id} (${typeof correctOption.id})`);
    console.log(`  - IsCorrect: ${isCorrect}`);
    
    return isCorrect;
  }

  /**
   * Belirtilen sorunun doğru cevabını döndürür.
   * @param {number} questionId - Soru ID'si
   * @returns {Object|null} Doğru cevap seçeneği
   */
  getCorrectAnswer(questionId) {
    const { questions } = stateManager.getState();
    const question = questions.find(q => q.question.id === parseInt(questionId, 10));
    
    if (!question || !question.question.options) {
      return null;
    }
    
    return question.question.options.find(option => option.is_correct === true);
  }

  /**
   * Yanlış cevap verildiğinde çalışacak fonksiyon (şimdilik boş).
   * @param {Object} data - { questionId, userAnswer, correctAnswer }
   */
  handleWrongAnswer(data) {
    // Şimdilik boş - buraya yanlış cevap işlemleri eklenecek
    console.log('[QuizEngine] handleWrongAnswer çağrıldı!');
    console.log('[QuizEngine] Yanlış cevap verildi:', data);
    
    // TODO: Burada yanlış cevap için özel işlemler yapılacak
    // Örneğin: AI chat'e bilgi gönderme, UI güncelleme, vs.
  }

  /**
   * Bir cevabı kaldırır.
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
   * Session status'unu günceller ve timer bilgilerini alır.
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
   * Quizi tamamlar ve sonuçları gösterir.
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
