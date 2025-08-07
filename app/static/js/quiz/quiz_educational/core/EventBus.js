/**
 * EventBus - Merkezi olay (event) yönetim sistemi.
 * Bileşenler arasında gevşek bağlı (loosely-coupled) iletişim için
 * yayınla-abone ol (publish-subscribe) desenini uygular.
 */
class EventBus {
  constructor() {
    // Olayları ve onlara abone olan callback fonksiyonlarını saklar.
    // Map<string, Set<Function>>
    this.events = new Map();
  }

  /**
   * Bir olaya abone olur.
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
   * Bir olay yayınlar ve tüm aboneleri bilgilendirir.
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
   * Tüm abonelikleri temizler.
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
export const eventBus = new EventBus();
