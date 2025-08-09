/**
 * =============================================================================
 * ApiService – API Servisi | API Service
 * =============================================================================
 * Uygulamanın sunucu ile olan tüm API iletişimlerini merkezi bir noktadan yönetir.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Kurulum ve Yapılandırma | Setup & Configuration
 *    - constructor() - Temel URL ve varsayılan başlıkları ayarlar.
 * 2) Özel Yardımcı Metot | Private Helper
 *    - _fetch(options) - Tüm HTTP istekleri için standartlaştırılmış fetch işleyicisi.
 * 3) Quiz Uç Noktaları | Quiz API Endpoints
 *    - fetchQuestions({ sessionId }) - Oturum için soru listesini getirir.
 *    - getSessionInfo(sessionId) - Oturum meta verilerini getirir.
 *    - getSessionStatus(sessionId) - Oturum durumunu getirir.
 *    - submitAnswer({ sessionId, questionId, answer }) - Cevabı gönderir.
 *    - updateTimer({ sessionId, remainingTimeSeconds }) - Zamanlayıcıyı günceller.
 *    - completeQuiz({ sessionId, answers }) - Quiz’i sonlandırır ve cevapları gönderir.
 * 4) Dışa Aktarım | Export
 * =============================================================================
 */
export class ApiService {

  /* =========================================================================
   * 1) Kurulum ve Yapılandırma | Setup & Configuration
   * ========================================================================= */

  /**
   * Servisi başlatır, temel API yolunu ve varsayılan HTTP başlıklarını ayarlar.
   */
  constructor() {
    this.baseUrl = '/api';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /* =========================================================================
   * 2) Özel Yardımcı Metot | Private Helper
   * ========================================================================= */

  /**
   * Tüm API istekleri için merkezi bir istek (fetch) işleyici.
   * Hata yönetimini, kimlik bilgilerini ve veri formatlamasını standartlaştırır.
   * @private
   * @param {object} options - İstek seçenekleri
   * @param {string} options.endpoint - İstek yapılacak uç nokta (örn: '/quiz/session/123')
   * @param {string} [options.method='GET'] - HTTP metodu
   * @param {object} [options.data=null] - Gönderilecek veri (POST, PUT için)
   * @returns {Promise<any>} API'den dönen işlenmiş veri
   * @throws {Error} API isteği başarısız olduğunda zenginleştirilmiş hata nesnesi fırlatır.
   */
  async _fetch({ endpoint, method = 'GET', data = null }) {
    const url = `${this.baseUrl}${endpoint}`;
    const options = {
      method,
      headers: this.defaultHeaders,
      credentials: 'same-origin', // Cookie tabanlı oturumlar için gereklidir
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      const responseData = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        const error = new Error(responseData.message || `HTTP Error! Status: ${response.status}`);
        error.status = response.status;
        error.response = responseData;
        throw error;
      }
      return responseData;
    } catch (error) {
      const enhancedError = new Error(`API Request Failed: ${error.message}`);
      enhancedError.originalError = error;
      enhancedError.request = { url, method, data };
      throw enhancedError;
    }
  }

  /* =========================================================================
   * 3) Quiz Uç Noktaları | Quiz API Endpoints
   * ========================================================================= */

  /**
   * Belirtilen oturum ID'si için quiz sorularını sunucudan alır.
   * @param {Object} params - Parametreler
   * @param {string|number} params.sessionId - Oturum ID'si.
   * @returns {Promise<any>} Soru listesini ve oturum bilgilerini içeren yanıt.
   */
  async fetchQuestions({ sessionId }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/questions` //
    });
  }

  /**
   * Oturumun meta verilerini (ders, konu vb.) alır.
   * @param {string|number} sessionId - Oturum ID'si.
   * @returns {Promise<any>} Oturum detaylarını içeren yanıt.
   */
  async getSessionInfo(sessionId) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}` //
    });
  }

  /**
   * Oturumun güncel durumunu (zamanlayıcı vb.) alır.
   * @param {string|number} sessionId - Oturum ID'si.
   * @returns {Promise<any>} Oturum durumunu içeren yanıt.
   */
  async getSessionStatus(sessionId) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/status` //
    });
  }

  /**
   * Kullanıcının bir soruya verdiği cevabı sunucuya gönderir.
   * @param {Object} params - Parametreler
   * @param {string|number} params.sessionId - Oturum ID'si.
   * @param {string|number} params.questionId - Soru ID'si.
   * @param {string|number|null} params.answer - Seçilen şık ID'si veya cevabı geri almak için null.
   * @returns {Promise<any>} İşlem sonucunu içeren yanıt.
   */
  async submitAnswer({ sessionId, questionId, answer }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/answer`, //
      method: 'POST', //
      data: { 
        question_id: questionId, //
        user_answer_option_id: answer //
      }
    });
  }

  /**
   * Kalan zamanlayıcı süresini sunucuya kaydederek günceller.
   * @param {Object} params - Parametreler
   * @param {string|number} params.sessionId - Oturum ID'si.
   * @param {number} params.remainingTimeSeconds - Kalan süre (saniye cinsinden).
   * @returns {Promise<any>} İşlem sonucunu içeren yanıt.
   */
  async updateTimer({ sessionId, remainingTimeSeconds }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/timer`, //
      method: 'PUT', //
      data: { remaining_time_seconds: remainingTimeSeconds } //
    });
  }

  /**
   * Quizi sonlandırır ve tüm cevapları toplu olarak sunucuya gönderir.
   * @param {Object} params - Parametreler
   * @param {string|number} params.sessionId - Oturum ID'si.
   * @param {Map<string|number, string|number|null>} params.answers - Cevapları içeren Map nesnesi.
   * @returns {Promise<any>} Quiz sonuçlarını içeren yanıt.
   */
  async completeQuiz({ sessionId, answers }) {
    const formattedAnswers = Array.from(answers.entries()); //
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/complete`, //
      method: 'POST', //
      data: { answers: formattedAnswers } //
    });
  }
}

/* =========================================================================
 * 4) Dışa Aktarım | Export
 * ========================================================================= */
// ES6 modül sistemi için adlandırılmış dışa aktarım (named export)
// `export class ApiService` ifadesi ile sağlanır.

// Node.js gibi CommonJS ortamlarıyla uyumluluk için ek dışa aktarım.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ApiService }; //
}