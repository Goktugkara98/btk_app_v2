import { stateManager } from '../core/StateManager.js';
import { eventBus } from '../core/EventBus.js';

/**
 * UIManager - Tüm UI güncellemelerini ve kullanıcı etkileşimlerini yönetir.
 */
export class UIManager {
  constructor() {
    this.elements = {};
    this.initializeElements();
    this.initializeEventListeners();
    this.initializeStateSubscriptions();
  }

  /**
   * DOM eleman referanslarını başlatır.
   */
  initializeElements() {
    const $ = (selector) => document.querySelector(selector);
    
    this.elements = {
      quizContainer: $('.quiz-container'),
      questionText: $('#question-text'),
      optionsContainer: $('#options-container'),
      prevBtn: $('#prev-button'),
      nextBtn: $('#next-button'),
      questionNav: $('#question-nav-list'),
      subjectName: $('#subject-name'),
      topicName: $('#topic-name'),
      difficultyBadge: $('#difficulty-badge'),
      currentQuestionNumber: $('#current-question-number'),
      totalQuestionNumber: $('#total-question-number'),
      timerElement: $('#timer'),
      loadingState: $('#loading-state'),
      errorState: $('#error-state'),
      errorMessage: $('#error-message'),

    };

    // Hangi elementlerin bulunamadığını kontrol et ve uyar.
    Object.entries(this.elements).forEach(([key, value]) => {
      if (!value || (value.length !== undefined && value.length === 0)) {
        // Element bulunamadı
      }
    });
  }

  /**
   * UI etkileşimleri için olay dinleyicilerini başlatır.
   */
  initializeEventListeners() {
    // Sonraki Soru Butonu
    this.elements.nextBtn?.addEventListener('click', () => {
      eventBus.publish('question:next');
    });

    // Önceki Soru Butonu
    this.elements.prevBtn?.addEventListener('click', () => {
      eventBus.publish('question:previous');
    });

    // Soru Navigasyonu
    this.elements.questionNav?.addEventListener('click', (e) => {
      const navItem = e.target.closest('.question-nav-item');
      if (navItem?.dataset.index) {
        const index = parseInt(navItem.dataset.index, 10);
        eventBus.publish('question:goTo', { index });
      }
    });

    // Seçenek Seçimi (Event Delegation ile)
    this.elements.optionsContainer?.addEventListener('click', (e) => {
      const optionElement = e.target.closest('.option-item');
      if (optionElement?.dataset.questionId && optionElement?.dataset.optionId) {
        // Eğer bir cevap zaten gönderiliyorsa, yeni bir işlem yapma.
        if (stateManager.getState('isSubmitting')) {
          return;
        }
        
        const { questionId, optionId } = optionElement.dataset;
        const currentAnswers = stateManager.getState('answers');
        const currentAnswer = currentAnswers.get(parseInt(questionId, 10));
        const numericOptionId = parseInt(optionId, 10);
        
        // Eğer tıklanan seçenek zaten seçiliyse, seçimi kaldır
        if (String(currentAnswer) === String(numericOptionId)) {
          // State'den cevabı kaldır
          eventBus.publish('answer:remove', { questionId });
          
          // Event'i durdur - diğer işlemlerin çalışmasını engelle
          e.stopPropagation();
          e.preventDefault();
          return;
        }
        
        // Diğer seçeneklerden 'selected' class'ını kaldır.
        this.elements.optionsContainer.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
        // Tıklanan seçeneğe 'selected' class'ını ekle.
        optionElement.classList.add('selected');

        // Olay akışını basitleştir: doğrudan 'answer:submit' olayını yayınla.
        eventBus.publish('answer:submit', { questionId, answer: optionId });
      }
    });

    // Retry Button
    const retryButton = document.getElementById('retry-button');
    retryButton?.addEventListener('click', () => {
      eventBus.publish('quiz:start');
    });
  }

  /**
   * State değişikliklerine abone olur ve UI'ı günceller.
   */
  initializeStateSubscriptions() {
    eventBus.subscribe('state:changed', ({ currentState, prevState }) => {
      // Belirli state değişikliklerine göre UI güncelleme fonksiyonlarını çağır.
      if (prevState.isLoading !== currentState.isLoading) {
        this.toggleLoading(currentState.isLoading);
      }
      if (prevState.error !== currentState.error) {
        this.showError(currentState.error);
      }
      
      // Soru değiştiğinde render et ve navbar'ı güncelle
      if (prevState.currentQuestion !== currentState.currentQuestion) {
        this.renderQuestion(currentState.currentQuestion);
        this.updateNavbarFromQuestion(currentState.currentQuestion);
      }
      
      // Navigation, buttons ve question number güncellemeleri
      if (prevState.questions !== currentState.questions || 
          prevState.currentQuestionIndex !== currentState.currentQuestionIndex || 
          prevState.answers !== currentState.answers || 
          prevState.visitedQuestions !== currentState.visitedQuestions) {
        
        this.updateQuestionNavigation();
        this.updateNavButtons();
        this.updateQuestionNumber();
        
        // Sadece answers değiştiğinde ve currentQuestion varsa render et
        // currentQuestion değişikliği yukarıda zaten handle ediliyor
        if (prevState.answers !== currentState.answers && 
            currentState.currentQuestion && 
            prevState.currentQuestion === currentState.currentQuestion) {
          this.renderQuestion(currentState.currentQuestion);
        }
      }
      
      if (prevState.timer.remainingTimeSeconds !== currentState.timer.remainingTimeSeconds) {
        this.updateTimer(currentState.timer);
      }
      
      if (prevState.totalQuestions !== currentState.totalQuestions) {
        this.updateTotalQuestions(currentState.totalQuestions);
      }
    });
  }

  /**
   * Yükleniyor durumunu yönetir.
   */
  toggleLoading(isLoading) {
    if (this.elements.loadingState) {
        this.elements.loadingState.style.display = isLoading ? 'flex' : 'none';
    }
    if (this.elements.quizContainer) {
        this.elements.quizContainer.classList.toggle('loading', isLoading);
    }
  }

  /**
   * Hata mesajını gösterir.
   */
  showError(error) {
    if (!this.elements.errorState || !this.elements.errorMessage) return;
    
    if (error) {
      this.elements.errorMessage.textContent = error.message || 'Bilinmeyen bir hata oluştu.';
      this.elements.errorState.style.display = 'flex';
      // Hatayı 5 saniye sonra otomatik olarak gizle.
      setTimeout(() => {
        if (this.elements.errorState) this.elements.errorState.style.display = 'none';
      }, 5000);
    } else {
      this.elements.errorState.style.display = 'none';
    }
  }

  /**
   * Mevcut soruyu ve seçeneklerini ekrana çizer.
   * @param {Object} question - Soru nesnesi.
   */
  renderQuestion(question) {
    if (!question || !this.elements.questionText || !this.elements.optionsContainer) {
      return;
    }
    
    // Navbar bilgilerini güncelle
    this.updateNavbarFromQuestion(question);
    
    // Soru metnini güncelle.
    this.elements.questionText.innerHTML = question.question?.text || 'Soru metni yüklenemedi.';
    
    // Seçenekleri temizle ve yeniden oluştur.
    this.elements.optionsContainer.innerHTML = '';
    
    const options = question.question?.options || [];
    const questionId = question.question?.id;
    const answers = stateManager.getState('answers');
    const selectedAnswer = answers.get(questionId);

    options.forEach((option, index) => {
      const optionElement = document.createElement('div');
      // Tip uyumsuzluğunu çöz: her ikisini de string'e çevir
      const isSelected = String(selectedAnswer) === String(option.id);
      
      optionElement.className = 'option-item' + (isSelected ? ' selected' : '');
      optionElement.dataset.questionId = questionId;
      optionElement.dataset.optionId = option.id;
      
      optionElement.innerHTML = `
        <div class="option-content">
          <div class="option-letter">${String.fromCharCode(65 + index)}</div>
          <div class="option-text">${option.name || `Seçenek ${index + 1}`}</div>
        </div>
      `;
      // KRİTİK DÜZELTME: Burada artık event listener eklenmiyor.
      // Bu işi `initializeEventListeners`'daki tek bir listener (event delegation) yapıyor.
      this.elements.optionsContainer.appendChild(optionElement);
    });

    // Educational features'ları render et
    this.renderEducationalFeatures(question);
    
    // AI Chat Manager'a question render edildi event'i gönder
    eventBus.publish('question:rendered', {
      questionId: question.question_number,
      subject: question.question?.subject_name,
      topic: question.question?.topic_name,
      difficulty: question.question?.difficulty_level
    });
  }

  /**
   * Educational features'ları render eder.
   * @param {Object} question - Soru nesnesi.
   */
  renderEducationalFeatures(question) {
    // Educational features AI Chat panelinde sağlanıyor
  }

  /**
   * Soru navigasyonunu günceller.
   */
  updateQuestionNavigation() {
    const { questions, currentQuestionIndex, answers, visitedQuestions } = stateManager.getState();
    if (!this.elements.questionNav) return;
    
    this.elements.questionNav.innerHTML = questions.map((q, index) => {
      const isCurrent = index === currentQuestionIndex;
      const questionId = parseInt(q.question.id, 10);
      const isAnswered = answers.has(questionId);
      const isVisited = visitedQuestions.has(index);
      const isSkipped = isVisited && !isAnswered; // Ziyaret edilmiş ama cevaplanmamış
      
      // CSS'te 'current' class'ı kullanılıyor, 'active' değil
      // Class'ları öncelik sırasına göre uygula
      const classes = [
        'question-nav-item',
        isCurrent ? 'current' : '',
        isAnswered ? 'answered' : (isSkipped ? 'skipped' : '') // Cevap verilmişse answered, yoksa skipped
      ].filter(Boolean).join(' ');
      
      return `<div class="${classes}" data-index="${index}">${index + 1}</div>`;
    }).join('');
  }

  /**
   * İleri/Geri butonlarının durumunu günceller.
   */
  updateNavButtons() {
    const { currentQuestionIndex, questions, isSubmitting } = stateManager.getState();
    
    if (this.elements.prevBtn) {
      const prevDisabled = currentQuestionIndex === 0 || isSubmitting;
      this.elements.prevBtn.disabled = prevDisabled;
    }
    
    if (this.elements.nextBtn) {
      const nextDisabled = isSubmitting;
      this.elements.nextBtn.disabled = nextDisabled;
      const isLastQuestion = currentQuestionIndex === questions.length - 1;
      this.elements.nextBtn.textContent = isLastQuestion ? 'Quizi Bitir' : 'Sonraki Soru';
    }
  }

  /**
   * Soru numarasını günceller.
   */
  updateQuestionNumber() {
    const { questions, currentQuestionIndex } = stateManager.getState();
    if (this.elements.currentQuestionNumber) {
      this.elements.currentQuestionNumber.textContent = questions.length > 0 ? currentQuestionIndex + 1 : 0;
    }
    if (this.elements.totalQuestionNumber) {
      this.elements.totalQuestionNumber.textContent = questions.length;
    }
  }

  /**
   * Zamanlayıcıyı günceller.
   */
  updateTimer(timer) {
    if (!this.elements.timerElement) return;
    
    if (timer?.enabled && timer.remainingTimeSeconds > 0) {
      const minutes = Math.floor(timer.remainingTimeSeconds / 60);
      const seconds = timer.remainingTimeSeconds % 60;
      this.elements.timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
      this.elements.timerElement.classList.toggle('warning', timer.remainingTimeSeconds < 60);
    } else {
      this.elements.timerElement.textContent = '--:--';
      this.elements.timerElement.classList.remove('warning');
    }
  }



  /**
   * Zorluk seviyesini Türkçe metne çevirir.
   */
  getDifficultyText(difficulty) {
    const difficultyMap = {
      'easy': 'Kolay',
      'medium': 'Orta',
      'hard': 'Zor',
      'random': 'Karışık'
    };
    return difficultyMap[difficulty] || difficulty;
  }

  /**
   * Toplam soru sayısını günceller.
   */
  updateTotalQuestions(totalQuestions) {
    if (this.elements.totalQuestionNumber) {
      this.elements.totalQuestionNumber.textContent = totalQuestions;
    }
  }

  /**
   * Aktif sorudan navbar bilgilerini günceller.
   */
  updateNavbarFromQuestion(question) {
    if (!question || !question.question) {
      return;
    }
    
    const questionData = question.question;
    
    // Ders adını güncelle
    if (this.elements.subjectName && questionData.subject_name) {
      this.elements.subjectName.textContent = questionData.subject_name;
    }
    
    // Konu adını güncelle
    if (this.elements.topicName && questionData.topic_name) {
      this.elements.topicName.textContent = questionData.topic_name;
    }
    
    // Zorluk seviyesini güncelle
    if (this.elements.difficultyBadge && questionData.difficulty_level) {
      const difficultyText = this.getDifficultyText(questionData.difficulty_level);
      this.elements.difficultyBadge.textContent = difficultyText;
      
      // Zorluk seviyesi CSS sınıfını güncelle
      // Önce tüm zorluk seviyesi sınıflarını kaldır
      this.elements.difficultyBadge.classList.remove('easy', 'medium', 'hard', 'random');
      // Sonra yeni zorluk seviyesi sınıfını ekle
      this.elements.difficultyBadge.classList.add(questionData.difficulty_level);
    }
  }
}
