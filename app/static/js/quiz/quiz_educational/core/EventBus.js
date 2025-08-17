/**
 * =============================================================================
 * EventBus – Olay Otobüsü | Event Bus
 * =============================================================================
 * Uygulama bileşenleri arasında gevşek bağlı iletişim için yayınla-abone ol (pub/sub)
 * desenini uygular. Modülerlik ve bakım kolaylığı sağlar.
 *
 * İÇİNDEKİLER | TABLE OF CONTENTS
 * 1) Yapı ve Depolama | Structure & Storage
 *    - constructor() - Olay deposunu (Map) başlatır.
 * 2) Temel İşlemler | Core Operations
 *    - subscribe(eventName, callback) - Abone ekler, `unsubscribe` döndürür.
 *    - publish(eventName, data) - Olayı tüm abonelere güvenli şekilde yayınlar.
 * 3) Yönetim ve Temizlik | Management & Cleanup
 *    - clear(eventName) - Belirli olayı veya tüm olayları temizler.
 * 4) Tekil Örnek | Singleton Export
 *    - eventBus - Uygulama genelinde paylaşılan tek örnek.
 * =============================================================================
 */
class EventBus {

  /* =========================================================================
   * 1) Yapı ve Depolama | Structure & Storage
   * ========================================================================= */

  /**
   * Olay (event) deposunu başlatır.
   * Olayları ve onlara abone olan callback fonksiyonlarını saklamak için bir Map kullanılır.
   * Veri yapısı: `Map<string, Set<Function>>`
   * - Key (string): Olayın adı (örn. 'quiz:start').
   * - Value (Set<Function>): Olay tetiklendiğinde çalıştırılacak callback fonksiyonları kümesi.
   * `Set` kullanılması, aynı callback fonksiyonunun bir olaya yanlışlıkla birden fazla kez
   * eklenmesini otomatik olarak engeller ve performansı artırır.
   */
  constructor() {
    this.events = new Map();
  }

  /* =========================================================================
   * 2) Temel İşlemler | Core Operations
   * ========================================================================= */

  /**
   * Bir olaya abone olmak için kullanılır.
   * @param {string} eventName - Abone olunacak olayın adı.
   * @param {Function} callback - Olay yayınlandığında çağrılacak fonksiyon.
   * @returns {{unsubscribe: Function}} Aboneliği sonlandırmak için kullanılabilecek 
   * bir `unsubscribe` fonksiyonu içeren nesne.
   */
  subscribe(eventName, callback) {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }
    
    const subscribers = this.events.get(eventName);
    subscribers.add(callback);

    // Abone olan bileşenin, yaşam döngüsü sona erdiğinde (örn. bir React bileşeni unmount olduğunda)
    // kolayca abonelikten çıkabilmesi için bir fonksiyon döndürülür.
    // Bu, "memory leak" (hafıza sızıntısı) riskini ortadan kaldırır.
    const unsubscribe = () => {
      subscribers.delete(callback);
      // Eğer bir olayın hiç abonesi kalmazsa, hafızayı verimli kullanmak
      // için olay Map'ten tamamen silinir.
      if (subscribers.size === 0) {
        this.events.delete(eventName);
      }
    };
    
    return { unsubscribe };
  }

  /**
   * Belirtilen bir olayı, tüm abonelerine veri göndererek yayınlar.
   * @param {string} eventName - Yayınlanacak olayın adı.
   * @param {*} [data] - Abonelere gönderilecek isteğe bağlı veri.
   */
  publish(eventName, data) {
    if (!this.events.has(eventName)) {
      return;
    }
    
    const subscribers = this.events.get(eventName);
    
    subscribers.forEach((callback) => {
      try {
        callback(data);
      } catch (error) {
        console.error(`[EventBus] '${eventName}' olayı için bir abonede hata oluştu:`, error);
      }
    });
  }

  /* =========================================================================
   * 3) Yönetim ve Temizlik | Management & Cleanup
   * ========================================================================= */

  /**
   * Abonelikleri temizler. Belirtilen olay için veya tümünü.
   * Test ortamlarında veya bileşenler arası geçişlerde temiz bir başlangıç yapmak için kullanışlıdır.
   * @param {string} [eventName] - Belirtilirse sadece o olayın aboneleri,
   * belirtilmezse tüm olaylar temizlenir.
   */
  clear(eventName) {
    if (eventName) {
      this.events.delete(eventName);
      console.log(`[EventBus] '${eventName}' olayına ait tüm abonelikler temizlendi.`);
    } else {
      this.events.clear();
      console.log(`[EventBus] Tüm olay abonelikleri temizlendi.`);
    }
  }
}

/* =========================================================================
 * 4) Tekil Örnek | Singleton Export
 * ========================================================================= */
// Uygulama genelinde tek bir EventBus örneği dışa aktarılır.
export const eventBus = new EventBus();