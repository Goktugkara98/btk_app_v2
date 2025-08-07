/**
 * NAVBAR COMPONENT JAVASCRIPT
 * 
 * Navbar için scroll efektleri ve etkileşimler
 * =============================================================================
 */

export function initNavbar() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;
    let ticking = false;

    // Scroll event handler
    function updateNavbar() {
        const currentScrollY = window.scrollY;
        
        // Sayfanın en üstünde mi kontrol et
        if (currentScrollY <= 50) {
            // En üstte - normal boyut
            navbar.classList.remove('navbar-scrolled', 'navbar-hidden');
        } else {
            // Aşağıda - küçük boyut
            navbar.classList.add('navbar-scrolled');
            navbar.classList.remove('navbar-hidden');
        }
        
        lastScrollY = currentScrollY;
        ticking = false;
    }

    // Throttled scroll event
    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    }

    // Event listeners
    window.addEventListener('scroll', onScroll, { passive: true });
    
    // Initial check
    updateNavbar();
} 