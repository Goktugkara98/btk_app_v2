/**
 * Quiz Preloader Manager
 * Handles showing/hiding preloader and ensures smooth page transitions
 */

class QuizPreloader {
    constructor() {
        this.preloader = document.getElementById('quiz-preloader');
        this.progressFill = this.preloader?.querySelector('.progress-fill');
        this.loadingText = this.preloader?.querySelector('.preloader-text');
        
        this.loadingSteps = [
            'Quiz yükleniyor...',
            'Sorular hazırlanıyor...',
            'Arayüz düzenleniyor...',
            'Hazır!'
        ];
        
        this.currentStep = 0;
        this.isLoaded = false;
        this.minLoadingTime = 2000; // Minimum 2 seconds
        this.startTime = Date.now();
        
        this.init();
    }
    
    init() {
        if (!this.preloader) return;
        
        // Start loading animation
        this.startLoadingAnimation();
        
        // Check if page is already loaded
        if (document.readyState === 'complete') {
            this.handlePageLoad();
        } else {
            // Wait for page load
            window.addEventListener('load', () => this.handlePageLoad());
        }
        
        // Fallback - hide preloader after max time
        setTimeout(() => {
            if (!this.isLoaded) {
                this.hidePreloader();
            }
        }, 8000);
    }
    
    startLoadingAnimation() {
        // Update loading text
        this.updateLoadingText();
        
        // Simulate progress
        this.simulateProgress();
    }
    
    updateLoadingText() {
        if (!this.loadingText) return;
        
        const interval = setInterval(() => {
            if (this.currentStep < this.loadingSteps.length - 1) {
                this.currentStep++;
                this.loadingText.textContent = this.loadingSteps[this.currentStep];
            } else {
                clearInterval(interval);
            }
        }, 800);
    }
    
    simulateProgress() {
        if (!this.progressFill) return;
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            this.progressFill.style.width = `${progress}%`;
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
    }
    
    handlePageLoad() {
        const elapsedTime = Date.now() - this.startTime;
        const remainingTime = Math.max(0, this.minLoadingTime - elapsedTime);
        
        // Complete progress bar
        if (this.progressFill) {
            this.progressFill.style.width = '100%';
        }
        
        // Update text to final step
        if (this.loadingText) {
            this.loadingText.textContent = this.loadingSteps[this.loadingSteps.length - 1];
        }
        
        // Wait for minimum time then hide
        setTimeout(() => {
            this.hidePreloader();
        }, remainingTime + 500);
    }
    
    hidePreloader() {
        if (!this.preloader || this.isLoaded) return;
        
        this.isLoaded = true;
        
        // Add hidden class for transition
        this.preloader.classList.add('hidden');
        
        // Remove from DOM after transition
        setTimeout(() => {
            if (this.preloader.parentNode) {
                this.preloader.parentNode.removeChild(this.preloader);
            }
        }, 500);
        
        // Trigger custom event
        window.dispatchEvent(new CustomEvent('preloaderHidden'));
    }
    
    // Public method to force hide (for debugging)
    forceHide() {
        this.hidePreloader();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quizPreloader = new QuizPreloader();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuizPreloader;
}
