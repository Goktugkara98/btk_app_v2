import { eventBus } from './EventBus.js';

/**
 * StateManager - Merkezi durum (state) yönetimi.
 * Değişiklik bildirimleri olan basit bir state container'ı uygular.
 */
 /*
  * İÇİNDEKİLER (Table of Contents)
  * - [1] Kurulum
  *   - [1.1] constructor()
  * - [2] Okuma
  *   - [2.1] getState(path)
  * - [3] Yazma (Temel)
  *   - [3.1] setState(newState, action)
  * - [4] Quiz Durumu
  *   - [4.1] setQuestions(questions)
  *   - [4.2] setCurrentQuestionIndex(index)
  * - [5] Cevap Yönetimi
  *   - [5.1] setAnswer(questionId, answer)
  *   - [5.2] removeAnswer(questionId)
  * - [6] Zamanlayıcı
  *   - [6.1] setTimer(remainingTime, totalTime)
  * - [7] UI Durumu
  *   - [7.1] setLoading(isLoading)
  *   - [7.2] setError(error)
  * - [8] Meta Bilgiler
  *   - [8.1] setMetadata({...})
  * - [9] Türetilmiş Veri
  *   - [9.1] buildDerivedMaps()
  * - [10] Dışa Aktarım
  *   - [10.1] stateManager singleton
  */
 class StateManager {
  /**
   * [1.1] constructor - Başlangıç state'ini yükler ve sessionId tespit eder.
   * Kategori: [1] Kurulum
   */
  constructor(initialState = {}) {
    this.state = {
      // Quiz durumu
      questions: [],
      currentQuestion: null,
      currentQuestionIndex: 0,
      answers: new Map(), // Soru ID'lerini ve verilen cevapları tutar.
      visitedQuestions: new Set(), // Ziyaret edilen soruları takip eder
      totalQuestions: 0,
      // Hızlı erişim için türetilmiş yapılar
      questionById: new Map(),
      optionsByQuestionId: new Map(),
      correctOptionByQuestionId: new Map(),
      
      // Oturum durumu
      sessionId: null,
      quizMode: 'practice', // 'practice' veya 'exam'
      timer: {
        enabled: false,
        remainingTime: 0,
        totalTime: 0,
        remainingTimeSeconds: 0
      },
      
      // Quiz meta bilgileri (ders, ünite, konu, zorluk vb.)
      grade: null,
      subject: null,
      unit: null,
      topic: null,
      difficulty: null,
      
      // Arayüz (UI) durumu
      isLoading: false,
      isSubmitting: false, // Cevap gönderilirken çift tıklamayı önlemek için.
      error: null,
      
      // Başlangıçta verilen state ile birleştirilir.
      ...initialState
    };
    
    // Eğer window nesnesinde session ID varsa, state'i başlat.
    if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
      this.state.sessionId = window.QUIZ_CONFIG.sessionId;
    } else if (window.QUIZ_SESSION_ID) {
      // Eski format için geriye dönük uyumluluk
      this.state.sessionId = window.QUIZ_SESSION_ID;
    }
  }

  /**
   * [2.1] getState - Mevcut state'i veya state içindeki belirli bir değeri alır.
   * Kategori: [2] Okuma
   * @param {string} [path] - State özelliğine giden nokta notasyonlu yol (örn: 'timer.remainingTime').
   * @returns {*} State veya state özelliği.
   */
  getState(path) {
    if (!path) return this.state;
    
    return path.split('.').reduce((obj, key) => {
      return obj && obj[key] !== undefined ? obj[key] : undefined;
    }, this.state);
  }

  /**
   * [3.1] setState - State'i günceller ve aboneleri bilgilendirir.
   * Kategori: [3] Yazma (Temel)
   * @param {Object} newState - Birleştirilecek yeni state parçası.
   * @param {string} [action] - Hata ayıklama için eylemin türünü belirten opsiyonel string.
   */
  setState(newState, action = 'STATE_UPDATE') {
    const prevState = { ...this.state };
    
    // Yeni state'i mevcut state ile birleştir.
    this.state = { ...this.state, ...newState };

    // State değişikliğini 'state:changed' olayı ile yayınla.
    eventBus.publish('state:changed', {
      action,
      prevState,
      currentState: this.state
    });
  }

  // Sık kullanılan state güncellemeleri için yardımcı metotlar
  
  /**
   * [4.1] setQuestions - Soruları ve başlangıç indeksini ayarlar; ziyaret edilenleri başlatır.
   * Kategori: [4] Quiz Durumu
   */
  setQuestions(questions) {
    // İlk soruyu ziyaret edilmiş olarak işaretle
    const initialVisitedQuestions = new Set();
    if (questions.length > 0) {
      initialVisitedQuestions.add(0);
    }
    
    this.setState({ 
      questions,
      currentQuestion: questions[0] || null,
      currentQuestionIndex: 0,
      answers: new Map(), // Yeni sorular geldiğinde eski cevapları temizle
      visitedQuestions: initialVisitedQuestions // İlk soruyu ziyaret edilmiş olarak işaretle
    }, 'SET_QUESTIONS');
  }

  /**
   * [4.2] setCurrentQuestionIndex - Aktif soruyu ve ziyaret edilenleri günceller.
   * Kategori: [4] Quiz Durumu
   */
  setCurrentQuestionIndex(index) {
    if (index >= 0 && index < this.state.questions.length) {
      // Ziyaret edilen soruları takip et
      const newVisitedQuestions = new Set(this.state.visitedQuestions);
      newVisitedQuestions.add(index);
      
      const newCurrentQuestion = this.state.questions[index];
      
      this.setState({
        currentQuestionIndex: index,
        currentQuestion: newCurrentQuestion,
        visitedQuestions: newVisitedQuestions
      }, 'SET_CURRENT_QUESTION');
    }
  }

  /**
   * [5.1] setAnswer - Kullanıcı cevabını state içinde saklar.
   * Kategori: [5] Cevap Yönetimi
   */
  setAnswer(questionId, answer) {
    // questionId'yi her zaman number olarak sakla
    const numericQuestionId = parseInt(questionId, 10);
    
    const newAnswers = new Map(this.state.answers);
    newAnswers.set(numericQuestionId, answer);
    
    this.setState({ answers: newAnswers }, 'SET_ANSWER');
  }

  /**
   * [5.2] removeAnswer - Kullanıcının cevabını kaldırır.
   * Kategori: [5] Cevap Yönetimi
   */
  removeAnswer(questionId) {
    // questionId'yi her zaman number olarak sakla
    const numericQuestionId = parseInt(questionId, 10);
    
    const newAnswers = new Map(this.state.answers);
    newAnswers.delete(numericQuestionId);
    
    this.setState({ answers: newAnswers }, 'REMOVE_ANSWER');
  }

  /**
   * [6.1] setTimer - Zamanlayıcı durumunu günceller.
   * Kategori: [6] Zamanlayıcı
   */
  setTimer(remainingTime, totalTime) {
    // remainingTimeSeconds kanonik alan; remainingTime geriye dönük uyumluluk için korunur.
    const remainingTimeSeconds = typeof remainingTime === 'number' ? remainingTime : this.state.timer.remainingTimeSeconds;
    this.setState({
      timer: {
        ...this.state.timer,
        enabled: true,
        remainingTime: remainingTimeSeconds, // backward compatibility
        remainingTimeSeconds,
        totalTime: (typeof totalTime === 'number') ? totalTime : this.state.timer.totalTime
      }
    }, 'SET_TIMER');
  }

  /**
   * [7.1] setLoading - Yükleniyor durumunu ayarlar.
   * Kategori: [7] UI Durumu
   */
  setLoading(isLoading) {
    this.setState({ isLoading }, 'SET_LOADING');
  }

  /**
   * [7.2] setError - Hata durumunu ayarlar.
   * Kategori: [7] UI Durumu
   */
  setError(error) {
    this.setState({ error }, 'SET_ERROR');
  }

  /**
   * [8.1] setMetadata - Quiz meta bilgilerini ayarlar (ders, konu, zorluk vb.)
   * Kategori: [8] Meta Bilgiler
   */
  setMetadata({ grade = null, subject = null, unit = null, topic = null, difficulty = null } = {}) {
    this.setState({ grade, subject, unit, topic, difficulty }, 'SET_METADATA');
  }

  /**
   * [9.1] buildDerivedMaps - Sorulardan hızlı erişim için yardımcı map'ler üretir.
   * Kategori: [9] Türetilmiş Veri
   */
  buildDerivedMaps() {
    const questionById = new Map();
    const optionsByQuestionId = new Map();
    const correctOptionByQuestionId = new Map();

    for (const q of this.state.questions) {
      const qid = q?.question?.id;
      if (!qid) continue;
      questionById.set(qid, q);

      const options = Array.isArray(q?.question?.options) ? q.question.options : [];
      optionsByQuestionId.set(qid, options);

      const correct = options.find(o => o?.is_correct === true || o?.isCorrect === true || o?.correct === true || o?.is_correct === 1 || o?.correct === 1) || null;
      if (correct) correctOptionByQuestionId.set(qid, correct);
    }

    this.setState({ questionById, optionsByQuestionId, correctOptionByQuestionId }, 'BUILD_DERIVED_MAPS');
  }
}

// Uygulama genelinde tek bir örnek (singleton) olarak ihraç edilir.
/**
 * [10.1] stateManager - Singleton örneği.
 * Kategori: [10] Dışa Aktarım
 */
export const stateManager = new StateManager();
