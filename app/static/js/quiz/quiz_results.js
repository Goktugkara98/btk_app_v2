/**
 * Quiz Results Page JavaScript
 * Handles the quiz results page functionality
 */

class QuizResultsManager {
    constructor() {
        this.sessionId = null;
        this.results = null;
        this.init();
    }

    init() {
        console.log('[QuizResultsManager] Initializing...');
        
        // Get session ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        this.sessionId = urlParams.get('session_id');
        
        if (!this.sessionId) {
            this.showError('Session ID bulunamadı');
            return;
        }
        
        // Load results data
        this.loadResults();
        
        // Initialize event listeners
        this.initializeEventListeners();
    }

    async loadResults() {
        try {
            console.log('[QuizResultsManager] Loading results for session:', this.sessionId);
            
            const response = await fetch(`/api/quiz/session/${this.sessionId}/results`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.results = data.data;
                this.displayResults();
            } else {
                this.showError('Sonuçlar yüklenirken hata oluştu');
            }
            
        } catch (error) {
            console.error('[QuizResultsManager] Error loading results:', error);
            this.showError('Sonuçlar yüklenirken hata oluştu');
        }
    }

    displayResults() {
        if (!this.results) return;
        
        console.log('[QuizResultsManager] Displaying results:', this.results);
        
        // Update score percentage
        const scorePercentage = document.getElementById('score-percentage');
        if (scorePercentage) {
            scorePercentage.textContent = `${this.results.percentage}%`;
        }
        
        // Update statistics
        const totalQuestions = document.getElementById('total-questions');
        const correctAnswers = document.getElementById('correct-answers');
        const incorrectAnswers = document.getElementById('incorrect-answers');
        const skippedAnswers = document.getElementById('skipped-answers');
        
        if (totalQuestions) totalQuestions.textContent = this.results.total_questions;
        if (correctAnswers) correctAnswers.textContent = this.results.correct_answers;
        if (incorrectAnswers) incorrectAnswers.textContent = this.results.answered_questions - this.results.correct_answers;
        if (skippedAnswers) skippedAnswers.textContent = this.results.total_questions - this.results.answered_questions;
        
        // Update score details
        const totalScore = document.getElementById('total-score');
        const maxScore = document.getElementById('max-score');
        const completionTime = document.getElementById('completion-time');
        
        if (totalScore) totalScore.textContent = this.results.total_score;
        if (maxScore) maxScore.textContent = this.results.max_possible_score;
        if (completionTime) {
            const minutes = Math.floor(this.results.completion_time_seconds / 60);
            const seconds = this.results.completion_time_seconds % 60;
            completionTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Update session ID display
        const sessionIdElement = document.getElementById('session-id');
        if (sessionIdElement) {
            sessionIdElement.textContent = `Session: ${this.sessionId}`;
        }
    }

    initializeEventListeners() {
        // New quiz button
        const newQuizBtn = document.getElementById('new-quiz-btn');
        if (newQuizBtn) {
            newQuizBtn.addEventListener('click', () => {
                window.location.href = '/quiz/auto-start';
            });
        }
        
        // Review answers button
        const reviewAnswersBtn = document.getElementById('review-answers-btn');
        if (reviewAnswersBtn) {
            reviewAnswersBtn.addEventListener('click', () => {
                // For now, just show a message
                alert('Cevapları inceleme özelliği yakında eklenecek!');
            });
        }
        
        // Back to home button
        const backToHomeBtn = document.getElementById('back-to-home-btn');
        if (backToHomeBtn) {
            backToHomeBtn.addEventListener('click', () => {
                window.location.href = '/';
            });
        }
    }

    showError(message) {
        console.error('[QuizResultsManager] Error:', message);
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 300px;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuizResultsManager();
}); 