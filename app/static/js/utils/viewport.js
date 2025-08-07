/* =============================================================================
 * VIEWPORT UTILITIES
 * Scrollbar genişliği hesaplama ve CSS custom property ayarlama
 * ============================================================================= */

/**
 * Scrollbar genişliğini hesaplar
 * @returns {number} Scrollbar genişliği (pixel)
 */
function getScrollbarWidth() {
    // Geçici div oluştur
    const outer = document.createElement('div');
    outer.style.visibility = 'hidden';
    outer.style.overflow = 'scroll';
    document.body.appendChild(outer);

    // İç div oluştur
    const inner = document.createElement('div');
    outer.appendChild(inner);

    // Genişlik farkını hesapla
    const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;

    // Geçici elementleri temizle
    outer.parentNode.removeChild(outer);

    return scrollbarWidth;
}

/**
 * Viewport genişliğini scrollbar olmadan hesaplar
 * @returns {number} Scrollbar olmayan viewport genişliği
 */
function getViewportWidthWithoutScrollbar() {
    return window.innerWidth - getScrollbarWidth();
}

/**
 * CSS custom property'leri ayarlar
 */
function setViewportProperties() {
    const scrollbarWidth = getScrollbarWidth();
    const viewportWidthWithoutScrollbar = getViewportWidthWithoutScrollbar();
    
    // CSS custom property'leri ayarla
    document.documentElement.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`);
    document.documentElement.style.setProperty('--viewport-width', `${viewportWidthWithoutScrollbar}px`);
    document.documentElement.style.setProperty('--full-width', `${viewportWidthWithoutScrollbar}px`);
}

/**
 * Viewport utilities'yi başlat
 */
function initViewportUtils() {
    // İlk yükleme
    setViewportProperties();
    
    // Pencere boyutu değiştiğinde güncelle
    window.addEventListener('resize', setViewportProperties);
    
    // Orientation değiştiğinde güncelle (mobil için)
    window.addEventListener('orientationchange', () => {
        setTimeout(setViewportProperties, 100);
    });
}

// Export functions
export {
    getScrollbarWidth,
    getViewportWidthWithoutScrollbar,
    setViewportProperties,
    initViewportUtils
}; 