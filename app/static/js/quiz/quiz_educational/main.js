// Quiz uygulamasının ana giriş noktası (entry point)

import { QuizEngine } from './core/QuizEngine.js';
import { UIManager } from './ui/UIManager.js';
import { stateManager } from './core/StateManager.js';
import { eventBus } from './core/EventBus.js';
import AIChatService from './services/AIChatService.js';
import AIChatManager from './ui/AIChatManager.js';

// Global hata yakalayıcı
window.onerror = function(message, source, lineno, colno, error) {
  console.error('Yakalanmayan Global Hata:', { message, source, lineno, colno, error });
  
  // Mümkünse hatayı arayüzde göster.
  const errorContainer = document.getElementById('error-container') || document.body;
  errorContainer.innerHTML = `
    <div style="color: red; padding: 20px; border: 2px solid red; margin: 10px; background: #fff;">
      <h3>Uygulamada Beklenmedik Bir Hata Oluştu</h3>
      <p><strong>Mesaj:</strong> ${message}</p>
      <p><strong>Kaynak:</strong> ${source}, Satır: ${lineno}</p>
      <button onclick="window.location.reload()" style="padding: 8px 16px; margin-top: 10px; cursor: pointer;">
        Sayfayı Yenile
      </button>
    </div>
  `;
  
  return true; // Tarayıcının varsayılan hata yönetimini engelle.
};

// Uygulamayı başlatan ana fonksiyon
function initApp() {
  try {
    // Session ID'yi state'e ayarla
    if (window.QUIZ_CONFIG && window.QUIZ_CONFIG.sessionId) {
      stateManager.setState({ sessionId: window.QUIZ_CONFIG.sessionId });
    }
    
    // Gerekli modüllerin varlığını kontrol et.
    if (!stateManager || !eventBus) {
      throw new Error('Çekirdek modüller (StateManager, EventBus) yüklenemedi.');
    }
    
    // AI Chat Service ve Manager'ı başlat
    const aiChatService = new AIChatService();
    const aiChatManager = new AIChatManager(eventBus, aiChatService);
    
    // UI Manager ve Quiz Engine'i başlat.
    const uiManager = new UIManager();
    const quizEngine = new QuizEngine();
    
    // Hata ayıklama (debugging) için global bir nesneye referansları ata.
    window.quizApp = {
      stateManager,
      eventBus,
      uiManager,
      quizEngine,
      aiChatService,
      aiChatManager
    };
    
    // Her şeyin yüklendiğinden emin olmak için küçük bir gecikmeyle quizi başlat.
    setTimeout(() => {
      eventBus.publish('quiz:start');
    }, 100);
    
  } catch (error) {
    stateManager?.setError({
      message: 'Uygulama başlatılamadı.',
      details: error.message
    });
  }
}

// DOM tamamen yüklendiğinde uygulamayı başlat.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  // DOM zaten yüklenmişse doğrudan başlat.
  initApp();
}
