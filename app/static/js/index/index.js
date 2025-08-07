/**
 * INDEX PAGE - MAIN JAVASCRIPT FILE
 * Sadece import'ları içerir
 * =============================================================================
 */

// Import Sections
import { initHeroQuiz } from './sections/hero.js';
import { initIndexDemoSimulation } from './sections/demo-simulation.js';

// Initialize all sections
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Index sayfası yüklendi');
    
    // Hero quiz başlat
    console.log('🎯 Hero quiz başlatılıyor...');
    initHeroQuiz();
    
    // Index demo simülasyon başlat
    console.log('🎮 Index demo simülasyon başlatılıyor...');
    initIndexDemoSimulation();
});

// Import Components (eğer gelecekte ortak JS component'leri olursa)
// import '../components/shared.js'; 