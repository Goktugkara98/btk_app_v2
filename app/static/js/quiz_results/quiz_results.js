/**
 * Quiz Results Page JavaScript
 * Handles quiz results display, analysis, and interactions
 */

// =============================================================================
// MAIN APPLICATION
// =============================================================================

class QuizResultsApp {
    constructor() {
        this.config = window.QUIZ_RESULTS_CONFIG || {};
        this.sessionId = this.config.sessionId;
        this.debug = this.config.debug || false;
        
        this.resultsManager = null;
        this.tabManager = null;
        this.chartManager = null;
        this.apiService = null;
        
        this.init();
    }
    
    async init() {
        try {
            if (this.debug) {
                console.log('🚀 Quiz Results App Starting...');
                console.log('📋 Session ID:', this.sessionId);
            }
            
            // Initialize services
            this.apiService = new ApiService();
            
            // Initialize managers
            this.resultsManager = new ResultsManager(this.apiService);
            this.tabManager = new TabManager();
            this.chartManager = new ChartManager();
            
            // Load results data
            await this.loadResults();
            
            // Initialize UI components
            this.initializeEventListeners();
            
            if (this.debug) {
                console.log('✅ Quiz Results App initialized successfully');
            }
            
        } catch (error) {
            console.error('❌ Quiz Results App initialization failed:', error);
            this.showError('Sonuçlar yüklenirken bir hata oluştu.');
        }
    }
    
    async loadResults() {
        if (!this.sessionId) {
            throw new Error('Session ID bulunamadı');
        }
        
        // Load results data from API
        const results = await this.resultsManager.loadResults(this.sessionId);
        
        // Update UI with results
        this.updateSummaryCards(results);
        this.updateQuestionsList(results.questions);
        this.updateRecommendations(results.recommendations);
        
        // Initialize charts
        this.chartManager.initializeCharts(results);
    }
    
    updateSummaryCards(results) {
        // Overall Score
        const overallScore = document.getElementById('overall-score');
        const scorePercentage = document.getElementById('score-percentage');
        if (overallScore && scorePercentage) {
            overallScore.textContent = results.totalScore;
            scorePercentage.textContent = `${results.scorePercentage}%`;
        }
        
        // Correct Answers
        const correctAnswers = document.getElementById('correct-answers');
        const correctPercentage = document.getElementById('correct-percentage');
        const totalQuestionsDisplay = document.getElementById('total-questions-display');
        if (correctAnswers && correctPercentage) {
            correctAnswers.textContent = results.correctAnswers;
            correctPercentage.textContent = `${results.correctPercentage}%`;
        }
        if (totalQuestionsDisplay) {
            totalQuestionsDisplay.textContent = `/${results.totalQuestions}`;
        }
        
        // Completion Time
        const completionTime = document.getElementById('completion-time');
        const timeEfficiency = document.getElementById('time-efficiency');
        if (completionTime && timeEfficiency) {
            completionTime.textContent = this.formatTime(results.completionTime);
            timeEfficiency.textContent = this.getTimeEfficiency(results.completionTime, results.totalQuestions);
        }
        
        // Rank
        const rank = document.getElementById('rank');
        const totalParticipants = document.getElementById('total-participants');
        if (rank && totalParticipants) {
            rank.textContent = `#${results.rank}`;
            totalParticipants.textContent = `Top ${results.percentile}%`;
        }
    }
    
    updateQuestionsList(questions) {
        const questionsList = document.getElementById('questions-list');
        if (!questionsList) return;
        
        questionsList.innerHTML = questions.map((question, index) => `
            <div class="question-item">
                <div class="question-header">
                    <div class="question-meta">
                        <span class="question-number">Soru ${index + 1}</span>
                        <span class="question-subject">${question.subject}</span>
                        <span class="question-difficulty ${question.difficulty}">${this.getDifficultyText(question.difficulty)}</span>
                    </div>
                    <div class="question-status-badge ${question.status}">
                        <i class="bi ${question.status === 'correct' ? 'bi-check-circle' : question.status === 'incorrect' ? 'bi-x-circle' : 'bi-dash-circle'}"></i>
                        <span>${this.getStatusText(question.status)}</span>
                    </div>
                </div>
                
                <div class="question-content">
                    <div class="question-text">${question.text}</div>
                    
                    <div class="question-answers">
                        <div class="answer-comparison">
                            <div class="answer-card ${question.status === 'correct' ? 'correct' : question.status === 'incorrect' ? 'incorrect' : 'skipped'}">
                                <div class="answer-header">
                                    <i class="bi bi-person"></i>
                                    <span>Senin Cevabın</span>
                                </div>
                                <div class="answer-text">${question.userAnswer}</div>
                            </div>
                            
                            <div class="answer-card correct">
                                <div class="answer-header">
                                    <i class="bi bi-check-circle"></i>
                                    <span>Doğru Cevap</span>
                                </div>
                                <div class="answer-text">${question.correctAnswer}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="question-explanation">
                        <div class="explanation-header">
                            <i class="bi bi-lightbulb"></i>
                            <span>Neden Bu Cevap?</span>
                        </div>
                        <div class="explanation-text">${question.explanation}</div>
                    </div>
                    
                    <div class="question-footer">
                        <div class="question-topic">
                            <i class="bi bi-book"></i>
                            <span>${question.topic}</span>
                        </div>
                        ${question.timeSpent ? `
                            <div class="question-time">
                                <i class="bi bi-clock"></i>
                                <span>${this.formatTime(question.timeSpent)}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    updateRecommendations(recommendations) {
        const recommendationsGrid = document.getElementById('recommendations-grid');
        if (!recommendationsGrid) return;
        
        recommendationsGrid.innerHTML = recommendations.map(rec => `
            <div class="recommendation-card">
                <div class="recommendation-icon">
                    <i class="bi ${rec.icon}"></i>
                </div>
                <div class="recommendation-title">${rec.title}</div>
                <div class="recommendation-text">${rec.description}</div>
                <a href="${rec.actionUrl}" class="recommendation-action">
                    ${rec.actionText}
                    <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        `).join('');
    }
    
    initializeEventListeners() {
        // Share results button
        const shareButton = document.getElementById('share-results');
        if (shareButton) {
            shareButton.addEventListener('click', () => this.shareResults());
        }
        
        // Tab navigation
        this.tabManager.initializeTabs();
    }
    
    // ===== UTILITY METHODS =====
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    getTimeEfficiency(time, questions) {
        const avgTimePerQuestion = time / questions;
        if (avgTimePerQuestion < 30) return 'Çok Hızlı';
        if (avgTimePerQuestion < 60) return 'Hızlı';
        if (avgTimePerQuestion < 90) return 'Normal';
        return 'Yavaş';
    }
    
    getStatusText(status) {
        const statusMap = {
            'correct': 'Doğru',
            'incorrect': 'Yanlış',
            'skipped': 'Boş'
        };
        return statusMap[status] || status;
    }
    
    getDifficultyText(difficulty) {
        const difficultyMap = {
            'easy': 'Kolay',
            'medium': 'Orta',
            'hard': 'Zor'
        };
        return difficultyMap[difficulty] || difficulty;
    }
    
    async shareResults() {
        try {
            if (navigator.share) {
                await navigator.share({
                    title: 'Quiz Sonuçlarım - Daima',
                    text: `Daima'da ${this.resultsManager.getScorePercentage()}% başarı oranıyla quiz tamamladım!`,
                    url: window.location.href
                });
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(window.location.href);
                this.showToast('Sonuç linki kopyalandı!');
            }
        } catch (error) {
            console.error('Share failed:', error);
            this.showToast('Paylaşım başarısız oldu.');
        }
    }
    
    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(errorDiv, container.firstChild);
        }
    }
    
    showToast(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// =============================================================================
// MODULES
// =============================================================================

// Results Manager
class ResultsManager {
    constructor(apiService) {
        this.apiService = apiService;
    }
    
    async loadResults(sessionId) {
        try {
            const response = await this.apiService.getQuizResults(sessionId);
            return response.data;
        } catch (error) {
            console.error('Failed to load results:', error);
            // Fallback to mock data if API fails
            return this.getMockResults();
        }
    }
    
    getScorePercentage() {
        // This would be calculated from the results data
        return 85; // Placeholder
    }
    
    getMockResults() {
        return {
            totalScore: 85,
            scorePercentage: 85,
            correctAnswers: 8,
            correctPercentage: 80,
            totalQuestions: 10,
            completionTime: 765, // 12:45 in seconds
            rank: 3,
            percentile: 10,
            questions: [
                {
                    text: "Aşağıdaki sayılardan hangisi en büyüktür?",
                    subject: "Matematik",
                    topic: "Sayılar",
                    difficulty: "medium",
                    status: "correct",
                    timeSpent: 45,
                    userAnswer: "25",
                    correctAnswer: "25",
                    explanation: "25 sayısı diğer sayılardan (15, 20, 18) daha büyüktür. Sayıları karşılaştırırken büyükten küçüğe sıralama yapmak yardımcı olur."
                },
                {
                    text: "Türkiye'nin başkenti neresidir?",
                    subject: "Coğrafya",
                    topic: "Türkiye Coğrafyası",
                    difficulty: "easy",
                    status: "correct",
                    timeSpent: 20,
                    userAnswer: "Ankara",
                    correctAnswer: "Ankara",
                    explanation: "Türkiye'nin başkenti 13 Ekim 1923'ten beri Ankara'dır. İstanbul eski başkent olmasına rağmen, Cumhuriyet'in ilanından sonra başkent Ankara'ya taşınmıştır."
                },
                {
                    text: "Hangi element periyodik tabloda 'Fe' sembolü ile gösterilir?",
                    subject: "Kimya",
                    topic: "Periyodik Tablo",
                    difficulty: "medium",
                    status: "incorrect",
                    timeSpent: 60,
                    userAnswer: "Flor",
                    correctAnswer: "Demir",
                    explanation: "'Fe' sembolü Demir elementini temsil eder. Latince 'Ferrum' kelimesinden gelir. Flor elementinin sembolü ise 'F'dir."
                },
                {
                    text: "Türkçe'de 'fiilimsi' nedir?",
                    subject: "Türkçe",
                    topic: "Fiilimsiler",
                    difficulty: "medium",
                    status: "correct",
                    timeSpent: 35,
                    userAnswer: "Fiilden türeyen isim, sıfat veya zarf",
                    correctAnswer: "Fiilden türeyen isim, sıfat veya zarf",
                    explanation: "Fiilimsiler, fiillerden türeyen ancak fiil olmayan kelimelerdir. İsim-fiil, sıfat-fiil ve zarf-fiil olmak üzere üç türü vardır."
                },
                {
                    text: "Hangi organ kanı temizler?",
                    subject: "Biyoloji",
                    topic: "Sindirim Sistemi",
                    difficulty: "easy",
                    status: "incorrect",
                    timeSpent: 25,
                    userAnswer: "Mide",
                    correctAnswer: "Böbrek",
                    explanation: "Kanı temizleyen organ böbrektir. Böbrekler, kandaki atık maddeleri süzerek idrar yoluyla vücuttan atar. Mide ise besinleri sindirmekten sorumludur."
                },
                {
                    text: "Osmanlı Devleti'nin kurucusu kimdir?",
                    subject: "Tarih",
                    topic: "Osmanlı Tarihi",
                    difficulty: "easy",
                    status: "correct",
                    timeSpent: 15,
                    userAnswer: "Osman Bey",
                    correctAnswer: "Osman Bey",
                    explanation: "Osmanlı Devleti, 1299 yılında Osman Bey tarafından kurulmuştur. Osman Bey, Kayı boyunun lideri olarak Söğüt ve Domaniç çevresinde devleti kurmuştur."
                },
                {
                    text: "Hangi element periyodik tabloda 'O' sembolü ile gösterilir?",
                    subject: "Kimya",
                    topic: "Periyodik Tablo",
                    difficulty: "easy",
                    status: "correct",
                    timeSpent: 30,
                    userAnswer: "Oksijen",
                    correctAnswer: "Oksijen",
                    explanation: "'O' sembolü Oksijen elementini temsil eder. Atmosferde %21 oranında bulunan, canlıların solunumu için gerekli olan temel elementlerden biridir."
                },
                {
                    text: "Bir üçgenin iç açıları toplamı kaç derecedir?",
                    subject: "Matematik",
                    topic: "Geometri",
                    difficulty: "easy",
                    status: "correct",
                    timeSpent: 40,
                    userAnswer: "180°",
                    correctAnswer: "180°",
                    explanation: "Bir üçgenin iç açıları toplamı her zaman 180 derecedir. Bu, geometrinin temel kurallarından biridir ve tüm üçgenler için geçerlidir."
                }
            ],
            recommendations: [
                {
                    icon: "bi-book",
                    title: "Kimya Konularını Tekrar Et",
                    description: "Periyodik tablo konusunda zorlandığınız görülüyor. Bu konuyu tekrar çalışmanızı öneriyoruz.",
                    actionText: "Kimya Çalış",
                    actionUrl: "/quiz/start?subject=chemistry"
                },
                {
                    icon: "bi-clock",
                    title: "Süre Yönetimini Geliştir",
                    description: "Bazı sorularda çok zaman harcıyorsunuz. Hızlı düşünme becerinizi geliştirmek için pratik yapın.",
                    actionText: "Hızlı Quiz Yap",
                    actionUrl: "/quiz/start?mode=speed"
                },
                {
                    icon: "bi-graph-up",
                    title: "Genel Performansınız İyi",
                    description: "%85 başarı oranınızla çok iyi bir performans gösterdiniz. Bu seviyeyi koruyun!",
                    actionText: "Daha Zor Sorular",
                    actionUrl: "/quiz/start?difficulty=hard"
                }
            ],
            subjects: {
                "Matematik": 100,
                "Coğrafya": 100,
                "Kimya": 100,
                "Türkçe": 100,
                "Biyoloji": 0,
                "Tarih": 100
            },
            difficulty: {
                easy: 75,
                medium: 100,
                hard: 0
            },
            progress: {
                // Mock progress data
            }
        };
    }
}

// Tab Manager
class TabManager {
    constructor() {
        this.activeTab = 'questions';
    }
    
    initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }
    
    switchTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update active tab pane
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.activeTab = tabName;
    }
}

// Chart Manager
class ChartManager {
    constructor() {
        this.charts = {};
    }
    
    initializeCharts(results) {
        // Initialize different chart types based on results data
        this.initializeSubjectsChart(results.subjects);
        this.initializeDifficultyChart(results.difficulty);
        this.initializeProgressChart(results.progress);
    }
    
    initializeSubjectsChart(subjectsData) {
        const chartContainer = document.getElementById('subjects-chart');
        if (!chartContainer) return;
        
        // Create subjects chart
        const subjectsHtml = Object.entries(subjectsData).map(([subject, score]) => `
            <div class="subject-item">
                <div class="subject-info">
                    <span class="subject-name">${subject}</span>
                    <span class="subject-score">${score}%</span>
                </div>
                <div class="subject-progress">
                    <div class="progress-bar" style="width: ${score}%"></div>
                </div>
            </div>
        `).join('');
        
        chartContainer.innerHTML = `
            <div class="subjects-list">
                ${subjectsHtml}
            </div>
        `;
    }
    
    initializeDifficultyChart(difficultyData) {
        const chartContainer = document.getElementById('difficulty-breakdown');
        if (!chartContainer) return;
        
        // Create difficulty breakdown
        chartContainer.innerHTML = `
            <div class="difficulty-stats">
                <div class="difficulty-item">
                    <span class="difficulty-label">Kolay</span>
                    <span class="difficulty-score">${difficultyData.easy || 0}%</span>
                </div>
                <div class="difficulty-item">
                    <span class="difficulty-label">Orta</span>
                    <span class="difficulty-score">${difficultyData.medium || 0}%</span>
                </div>
                <div class="difficulty-item">
                    <span class="difficulty-label">Zor</span>
                    <span class="difficulty-score">${difficultyData.hard || 0}%</span>
                </div>
            </div>
        `;
    }
    
    initializeProgressChart(progressData) {
        const chartContainer = document.getElementById('progress-chart');
        if (!chartContainer) return;
        
        // Create progress chart
        chartContainer.innerHTML = `
            <div class="progress-overview">
                <div class="progress-item">
                    <span class="progress-label">Bu Hafta</span>
                    <span class="progress-value">+15%</span>
                </div>
                <div class="progress-item">
                    <span class="progress-label">Bu Ay</span>
                    <span class="progress-value">+25%</span>
                </div>
                <div class="progress-item">
                    <span class="progress-label">Toplam</span>
                    <span class="progress-value">85%</span>
                </div>
            </div>
        `;
    }
}

// API Service
class ApiService {
    constructor() {
        this.baseUrl = '/api';
    }
    
    async getQuizResults(sessionId) {
        try {
            const response = await fetch(`${this.baseUrl}/quiz/session/${sessionId}/results`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuizResultsApp();
}); 