/**
 * ApiService - Tüm API iletişimlerini yönetir.
 *
 * İÇİNDEKİLER (Table of Contents)
 * - [1] Kurulum
 *   - [1.1] constructor()
 * - [2] İç (Private)
 *   - [2.1] _fetch(options)
 * - [3] Quiz Uç Noktaları
 *   - [3.1] fetchQuestions({ sessionId })
 *   - [3.2] getSessionInfo(sessionId)
 *   - [3.3] submitAnswer({ sessionId, questionId, answer })
 *   - [3.4] completeQuiz({ sessionId, answers })
 *   - [3.5] getSessionStatus(sessionId)
 *   - [3.6] updateTimer({ sessionId, remainingTimeSeconds })
 * - [4] Dışa Aktarım
 *   - [4.1] Named export
 *   - [4.2] CommonJS export
 */
export class ApiService {
  /**
   * [1.1] constructor - Baz URL ve varsayılan header'ları ayarlar.
   * Kategori: [1] Kurulum
   */
  constructor() {
    this.baseUrl = '/api';  // /api/quiz yerine /api kullanıyoruz
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /**
   * [2.1] _fetch - Gelişmiş hata yönetimi ile API isteği yapar.
   * Kategori: [2] İç (Private)
   * @private
   * @param {object} options - İstek seçenekleri
   * @param {string} options.endpoint - İstek yapılacak endpoint (örn: '/session/123')
   * @param {string} [options.method='GET'] - HTTP metodu
   * @param {object} [options.data=null] - Gönderilecek veri (POST, PUT için)
   * @returns {Promise<any>} API'den dönen veri
   */
  async _fetch({ endpoint, method = 'GET', data = null }) {
    const url = `${this.baseUrl}${endpoint}`;

    const options = {
      method,
      headers: this.defaultHeaders,
      credentials: 'same-origin', // Cookie'lerin gönderilmesini sağlar
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      const responseData = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        const error = new Error(responseData.message || `HTTP hatası! Durum: ${response.status}`);
        error.status = response.status;
        error.response = responseData;
        throw error;
      }

      return responseData;
      
    } catch (error) {
      // Hata nesnesini daha fazla bağlamla zenginleştir
      const enhancedError = new Error(`API isteği başarısız oldu: ${error.message}`);
      enhancedError.originalError = error;
      enhancedError.request = { url, method, data };
      
      throw enhancedError;
    }
  }

  /**
   * [3.1] fetchQuestions - Quiz için soruları getirir.
   * Kategori: [3] Quiz Uç Noktaları
   * @param {Object} params
   * @param {string|number} params.sessionId - Oturum ID
   * @returns {Promise<any>} Soru listesi
   */
  async fetchQuestions({ sessionId }) {
    return await this._fetch({
      endpoint: `/quiz/session/${sessionId}/questions`,
      method: 'GET'
    });
  }

  /**
   * [3.2] getSessionInfo - Oturum detay bilgisini getirir (meta için).
   * Kategori: [3] Quiz Uç Noktaları
   * @param {string|number} sessionId - Oturum ID
   * @returns {Promise<any>} Oturum bilgisi
   */
  async getSessionInfo(sessionId) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}`,
      method: 'GET'
    });
  }

  /**
   * [3.3] submitAnswer - Bir cevabı sunucuya gönderir.
   * Kategori: [3] Quiz Uç Noktaları
   * @param {Object} params
   * @param {string|number} params.sessionId - Oturum ID
   * @param {string|number} params.questionId - Soru ID
   * @param {string|number|null} params.answer - Seçilen şık ID (veya null)
   * @returns {Promise<any>} Sunucu yanıtı
   */
  async submitAnswer({ sessionId, questionId, answer }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/answer`,
      method: 'POST',
      data: { 
        question_id: questionId, 
        user_answer_option_id: answer 
      }
    });
  }

  /**
   * [3.4] completeQuiz - Quizi tamamlar.
   * Kategori: [3] Quiz Uç Noktaları
   * @param {Object} params
   * @param {string|number} params.sessionId - Oturum ID
   * @param {Map<string|number, string|number|null>} params.answers - Cevaplar Map'i
   * @returns {Promise<any>} Sonuç verisi
   */
  async completeQuiz({ sessionId, answers }) {
    // Map'i sunucuya göndermeden önce [key, value] dizisine dönüştür
    const formattedAnswers = Array.from(answers.entries());
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/complete`,
      method: 'POST',
      data: { answers: formattedAnswers }
    });
  }

  /**
   * [3.5] getSessionStatus - Oturum durumunu alır.
   * Kategori: [3] Quiz Uç Noktaları
   * @param {string|number} sessionId - Oturum ID
   * @returns {Promise<any>} Oturum durumu
   */
  async getSessionStatus(sessionId) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/status`,
      method: 'GET'
    });
  }
  
  /**
   * [3.6] updateTimer - Kalan süreyi günceller.
   * Kategori: [3] Quiz Uç Noktaları
   * @param {Object} params
   * @param {string|number} params.sessionId - Oturum ID
   * @param {number} params.remainingTimeSeconds - Kalan süre (saniye)
   * @returns {Promise<any>} Sunucu yanıtı
   */
  async updateTimer({ sessionId, remainingTimeSeconds }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/timer`,
      method: 'PUT',
      data: { remaining_time_seconds: remainingTimeSeconds }
    });
  }
}

// Exportlar
/**
 * [4.1] Named export - ES6 adlandırılmış export.
 * Kategori: [4] Dışa Aktarım
 */
// export class ApiService { ... } satırındaki named export kullanılır

/**
 * [4.2] CommonJS export - Node.js uyumluluğu için.
 * Kategori: [4] Dışa Aktarım
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ApiService };
}
