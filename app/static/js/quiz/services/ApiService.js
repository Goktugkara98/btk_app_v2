/**
 * ApiService - Tüm API iletişimlerini yönetir.
 */
export class ApiService {
  constructor() {
    this.baseUrl = '/api';  // /api/quiz yerine /api kullanıyoruz
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /**
   * Gelişmiş hata yönetimi ve loglama ile bir API isteği yapar.
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
   * Quiz için soruları getirir.
   */
  async fetchQuestions({ sessionId }) {
    return await this._fetch({
      endpoint: `/quiz/session/${sessionId}/questions`,
      method: 'GET'
    });
  }

  /**
   * Bir cevabı sunucuya gönderir.
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
   * Quizi tamamlar.
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
   * Oturum durumunu alır.
   */
  async getSessionStatus(sessionId) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/status`,
      method: 'GET'
    });
  }
  
  /**
   * Timer'ı günceller.
   */
  async updateTimer({ sessionId, remainingTimeSeconds }) {
    return this._fetch({
      endpoint: `/quiz/session/${sessionId}/timer`,
      method: 'PUT',
      data: { remaining_time_seconds: remainingTimeSeconds }
    });
  }
}
