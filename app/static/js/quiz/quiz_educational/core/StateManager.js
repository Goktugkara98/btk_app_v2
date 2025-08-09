import { eventBus } from './EventBus.js';

/**
 * =============================================================================
 * StateManager – Durum Yöneticisi | State Manager
 * =============================================================================
 * Uygulamanın tüm durumunu tek bir merkezde tutar ve yönetir; değişiklikleri `eventBus` ile yayar.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Kurulum ve Çekirdek | Setup & Core
 *    - constructor(initialState) - Başlangıç durumunu kurar ve session ID'yi tespit eder.
 * 2) Temel Durum Erişimi | Core State Access
 *    - getState(path) - Tüm state'i veya bir yolu döndürür.
 *    - setState(newState, action) - State'i günceller ve olay yayınlar.
 * 3) Quiz Durum Yönetimi | Quiz Status Management
 *    - setQuestions(questions) - Soruları yükler ve başlangıcı ayarlar.
 *    - setCurrentQuestionIndex(index) - Aktif soruyu değiştirir ve ziyaret edilenlere ekler.
 * 4) Cevap Yönetimi | Answer Management
 *    - setAnswer(questionId, answer) - Cevabı kaydeder.
 *    - removeAnswer(questionId) - Cevabı siler.
 * 5) Zamanlayıcı Yönetimi | Timer Management
 *    - setTimer(remainingTime, totalTime) - Zamanlayıcı değerlerini günceller.
 * 6) Arayüz Durum Yönetimi | UI State Management
 *    - setLoading(isLoading) - Yükleniyor durumunu ayarlar.
 *    - setError(error) - Hata durumunu ayarlar.
 * 7) Meta Veri Yönetimi | Metadata Management
 *    - setMetadata({...}) - Meta verileri günceller.
 * 8) Türetilmiş Veri Yönetimi | Derived Data Management
 *    - buildDerivedMaps() - Hızlı erişim için haritalar oluşturur.
 * 9) Tekil Örnek | Singleton Export
 *    - stateManager - Uygulama genelinde paylaşılan örnek.
 * =============================================================================
 */
class StateManager {

  /* =========================================================================
   * 1) Kurulum ve Çekirdek | Setup & Core
   * ========================================================================= */

  /**
   * constructor - Başlangıç state'ini yükler ve mevcut oturum (session) ID'sini tespit eder.
   */
  constructor(initialState = {}) {
    this.state = {
      // Quiz durumu
      questions: [],
      currentQuestion: null,
      currentQuestionIndex: 0,
      answers: new Map(),
      visitedQuestions: new Set(),
      totalQuestions: 0,
      
      // Hızlı erişim için türetilmiş yapılar
      questionById: new Map(),
      optionsByQuestionId: new Map(),
      correctOptionByQuestionId: new Map(),
      
      // Oturum durumu
      sessionId: null,
      quizMode: 'practice',
      timer: {
        enabled: false,
        remainingTimeSeconds: 0,
        totalTime: 0
      },
      
      // Quiz meta bilgileri
      grade: null,
      subject: null,
      unit: null,
      topic: null,
      difficulty: null,
      
      // Arayüz (UI) durumu
      isLoading: false,
      isSubmitting: false,
      error: null,
      
      // Başlangıçta verilen state ile birleştirilir.
      ...initialState
    };
    
    // Global window nesnesinden session ID'yi alıp state'e yazar.
    if (window.QUIZ_CONFIG?.sessionId) {
      this.state.sessionId = window.QUIZ_CONFIG.sessionId;
    } else if (window.QUIZ_SESSION_ID) {
      this.state.sessionId = window.QUIZ_SESSION_ID; // Geriye dönük uyumluluk
    }
  }

  /* =========================================================================
   * 2) Temel Durum Erişimi | Core State Access
   * ========================================================================= */

  /**
   * Mevcut state'i veya state içindeki belirli bir değeri alır.
   * @param {string} [path] - State özelliğine giden nokta notasyonlu yol (örn: 'timer.remainingTimeSeconds').
   * @returns {*} İstenen state parçası veya tüm state nesnesi.
   */
  getState(path) {
    if (!path) return this.state;
    
    return path.split('.').reduce((obj, key) => {
      return obj && obj[key] !== undefined ? obj[key] : undefined;
    }, this.state);
  }

  /**
   * State'i günceller ve 'state:changed' olayını yayınlayarak aboneleri bilgilendirir.
   * @param {Object} newState - Mevcut state ile birleştirilecek yeni state parçası.
   * @param {string} [action='STATE_UPDATE'] - Hata ayıklama için eylemin türünü belirten opsiyonel etiket.
   */
  setState(newState, action = 'STATE_UPDATE') {
    const prevState = { ...this.state };
    this.state = { ...this.state, ...newState };

    eventBus.publish('state:changed', {
      action,
      prevState,
      currentState: this.state
    });
  }

  /* =========================================================================
   * 3) Quiz Durum Yönetimi | Quiz Status Management
   * ========================================================================= */

  /**
   * Soruları, başlangıç indeksini ayarlar ve ziyaret edilenler listesini sıfırlar.
   * @param {Array} questions - Yüklenecek soru listesi.
   */
  setQuestions(questions) {
    const initialVisitedQuestions = new Set();
    if (questions.length > 0) {
      initialVisitedQuestions.add(0); // İlk soruyu ziyaret edilmiş olarak işaretle
    }
    
    this.setState({ 
      questions,
      currentQuestion: questions[0] || null,
      currentQuestionIndex: 0,
      answers: new Map(), // Yeni sorular geldiğinde eski cevapları temizle
      visitedQuestions: initialVisitedQuestions
    }, 'SET_QUESTIONS');
  }

  /**
   * Aktif sorunun indeksini günceller ve bu indeksi ziyaret edilenler listesine ekler.
   * @param {number} index - Aktif hale getirilecek sorunun indeksi.
   */
  setCurrentQuestionIndex(index) {
    if (index >= 0 && index < this.state.questions.length) {
      const newVisitedQuestions = new Set(this.state.visitedQuestions);
      newVisitedQuestions.add(index);
      
      this.setState({
        currentQuestionIndex: index,
        currentQuestion: this.state.questions[index],
        visitedQuestions: newVisitedQuestions
      }, 'SET_CURRENT_QUESTION');
    }
  }

  /* =========================================================================
   * 4) Cevap Yönetimi | Answer Management
   * ========================================================================= */

  /**
   * Bir soru için kullanıcının cevabını state'e kaydeder.
   * @param {number|string} questionId - Cevabın ait olduğu soru ID'si.
   * @param {*} answer - Kullanıcının verdiği cevap.
   */
  setAnswer(questionId, answer) {
    const newAnswers = new Map(this.state.answers);
    newAnswers.set(parseInt(questionId, 10), answer);
    this.setState({ answers: newAnswers }, 'SET_ANSWER');
  }

  /**
   * Bir soruya verilen cevabı state'den kaldırır.
   * @param {number|string} questionId - Cevabı kaldırılacak soru ID'si.
   */
  removeAnswer(questionId) {
    const newAnswers = new Map(this.state.answers);
    newAnswers.delete(parseInt(questionId, 10));
    this.setState({ answers: newAnswers }, 'REMOVE_ANSWER');
  }

  /* =========================================================================
   * 5) Zamanlayıcı Yönetimi | Timer Management
   * ========================================================================= */

  /**
   * Zamanlayıcının durumunu (kalan süre, toplam süre) günceller.
   * @param {number} remainingTime - Saniye cinsinden kalan süre.
   * @param {number} totalTime - Saniye cinsinden toplam süre.
   */
  setTimer(remainingTime, totalTime) {
    const remainingTimeSeconds = typeof remainingTime === 'number' ? remainingTime : this.state.timer.remainingTimeSeconds;
    this.setState({
      timer: {
        ...this.state.timer,
        enabled: true,
        remainingTimeSeconds,
        totalTime: (typeof totalTime === 'number') ? totalTime : this.state.timer.totalTime
      }
    }, 'SET_TIMER');
  }

  /* =========================================================================
   * 6) Arayüz Durum Yönetimi | UI State Management
   * ========================================================================= */

  /**
   * API çağrıları gibi asenkron işlemler için yükleniyor durumunu ayarlar.
   * @param {boolean} isLoading - Yükleniyor durumunun aktif olup olmadığı.
   */
  setLoading(isLoading) {
    this.setState({ isLoading }, 'SET_LOADING');
  }

  /**
   * Uygulamada bir hata oluştuğunda hata durumunu ayarlar.
   * @param {Object|null} error - Hata nesnesi veya durumu temizlemek için null.
   */
  setError(error) {
    this.setState({ error }, 'SET_ERROR');
  }

  /* =========================================================================
   * 7) Meta Veri Yönetimi | Metadata Management
   * ========================================================================= */

  /**
   * Quiz'in meta verilerini (ders, konu, zorluk vb.) ayarlar.
   * @param {Object} metadata - Meta verileri içeren nesne.
   */
  setMetadata({ grade = null, subject = null, unit = null, topic = null, difficulty = null } = {}) {
    this.setState({ grade, subject, unit, topic, difficulty }, 'SET_METADATA');
  }

  /* =========================================================================
   * 8) Türetilmiş Veri Yönetimi | Derived Data Management
   * ========================================================================= */

  /**
   * Soru listesinden, verilere hızlı erişim sağlamak için yardımcı Map'ler oluşturur.
   * Bu işlem, soru ID'sine göre soru, seçenek ve doğru cevap bulmayı optimize eder.
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

      const correctOption = options.find(o => o.is_correct === true || o.isCorrect === true) || null;
      if (correctOption) {
        correctOptionByQuestionId.set(qid, correctOption);
      }
    }
    
    this.setState({ questionById, optionsByQuestionId, correctOptionByQuestionId }, 'BUILD_DERIVED_MAPS');
  }
}

/**
 * =========================================================================
 * 9) Tekil Örnek | Singleton Export
 * =========================================================================
 *
 * Uygulama genelinde kullanılacak tek StateManager örneği.
 */
export const stateManager = new StateManager();