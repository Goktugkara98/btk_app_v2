/**
 * EventBus - Merkezi olay (event) yönetim sistemi.
 * Bileşenler arasında gevşek bağlı (loosely-coupled) iletişim için
 * yayınla-abone ol (publish-subscribe) desenini uygular.
 */
 /*
  * İÇİNDEKİLER (Table of Contents)
  * - [1] Kurulum
  *   - [1.1] constructor()
  * - [2] Abonelik Yönetimi
  *   - [2.1] subscribe(event, callback)
  * - [3] Yayınlama
  *   - [3.1] publish(event, data)
  * - [4] Temizlik
  *   - [4.1] clear(event)
  * - [5] Dışa Aktarım
  *   - [5.1] eventBus singleton
  */
 class EventBus {
  /**
   * [1.1] constructor - Olay depolama yapısını başlatır.
   * Kategori: [1] Kurulum
   */
  constructor() {
    // Olayları ve onlara abone olan callback fonksiyonlarını saklar.
    // Map<string, Set<Function>>
    this.events = new Map();
  }

  /**
   * [2.1] subscribe - Bir olaya abone olur.
   * Kategori: [2] Abonelik Yönetimi
   * @param {string} event - Abone olunacak olayın adı.
   * @param {Function} callback - Olay yayınlandığında çağrılacak fonksiyon.
   * @returns {Function} Aboneliği iptal etmek için kullanılabilecek bir fonksiyon.
   */
  subscribe(event, callback) {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    
    const subscribers = this.events.get(event);
    subscribers.add(callback);

    // Abonelikten çıkma fonksiyonu döndürülür.
    return () => {
      subscribers.delete(callback);
      // Eğer bir olayın hiç abonesi kalmazsa, hafızadan temizlenir.
      if (subscribers.size === 0) {
        this.events.delete(event);
      }
    };
  }

  /**
   * [3.1] publish - Bir olay yayınlar ve tüm aboneleri bilgilendirir.
   * Kategori: [3] Yayınlama
   * @param {string} event - Yayınlanacak olayın adı.
   * @param {*} [data] - Abonelere gönderilecek veri.
   */
  publish(event, data) {
    if (!this.events.has(event)) {
      return;
    }
    
    const subscribers = this.events.get(event);
    subscribers.forEach(callback => {
      try {
        // Her bir abonenin callback fonksiyonu güvenli bir şekilde çağrılır.
        callback(data);
      } catch (error) {
        // Event callback hatası
      }
    });
  }

  /**
   * [4.1] clear - Tüm abonelikleri temizler.
   * Kategori: [4] Temizlik
   * @param {string} [event] - Belirtilirse sadece o olayın abonelerini,
   * belirtilmezse tüm aboneleri temizler.
   */
  clear(event) {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
  }
}

// Uygulama genelinde tek bir örnek (singleton) olarak ihraç edilir.
/**
 * [5.1] eventBus - Singleton örneği.
 * Kategori: [5] Dışa Aktarım
 */
export const eventBus = new EventBus();
