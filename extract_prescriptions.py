from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import json
from datetime import datetime
import sys
import os

# Windows konsol için UTF-8 encoding ayarla
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')

class PrescriptionExtractor:
    def __init__(self):
        self.browser = MedulaBrowser(Settings())
        self.prescriptions = []
    
    def start(self):
        """Browser'ı başlat ve giriş yap"""
        print('[BAŞLAT] Reçete çıkarma sistemi başlatılıyor...')
        self.browser.start()
        
        # Giriş yap
        if self.browser.login():
            print('[BAŞARILI] Medula girişi başarılı!')
            return True
        else:
            print('[HATA] Medula girişi başarısız!')
            return False
    
    def navigate_to_prescriptions(self):
        """Reçete listesi sayfasına git"""
        try:
            print('[NAVİGASYON] Reçete Listesi sayfasına gidiliyor...')
            
            # "Reçete Listesi" linkini bul ve tıkla
            recete_link = self.browser.driver.find_element(By.XPATH, "//*[text()='Reçete Listesi']")
            recete_link.click()
            time.sleep(3)
            
            print('[BAŞARILI] Reçete Listesi sayfası açıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Reçete listesi sayfasına gidilemedi: {e}')
            return False
    
    def set_filters_and_search(self, group='A'):
        """Filtreleri ayarla ve arama yap"""
        try:
            print(f'[FİLTRE] {group} Grubu için filtreler ayarlanıyor...')
            
            # Fatura türü seç
            fatura_dropdown = Select(self.browser.driver.find_element(By.NAME, "faturaTuru"))
            fatura_dropdown.select_by_visible_text(f"{group} Grubu")
            print(f'[BAŞARILI] {group} Grubu seçildi')
            
            # Sorgula butonuna bas
            sorgula_button = self.browser.driver.find_element(By.XPATH, "//input[@value='Sorgula']")
            sorgula_button.click()
            time.sleep(5)
            
            print(f'[SORGU] {group} Grubu reçeteler sorgulandı')
            return True
            
        except Exception as e:
            print(f'[HATA] Filtreleme hatası: {e}')
            return False
    
    def extract_prescription_data(self):
        """Reçete verilerini çıkar"""
        try:
            print('[ÇIKARMA] Reçete verileri çıkarılıyor...')
            
            # Ana reçete tablosunu bul
            table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Reçete No')]]")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Başlık satırını atla, veri satırlarını işle
            for row_index, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 7:  # En az 7 sütun olmalı
                        prescription_data = {
                            'id': row_index,
                            'recete_no': cells[0].text.strip(),
                            'son_guncelleme': cells[1].text.strip(),
                            'recete_tarihi': cells[2].text.strip(),
                            'hasta_ad': cells[3].text.strip(),
                            'hasta_soyad': cells[4].text.strip(),
                            'kapsam': cells[5].text.strip(),
                            'sonlandirildi': cells[6].text.strip(),
                            'barkod_rapor': cells[7].text.strip() if len(cells) > 7 else '',
                            'dokuman': cells[8].text.strip() if len(cells) > 8 else '',
                            'extraction_time': datetime.now().isoformat(),
                            'hasta_tc': '',  # Bu veri tabloda yok, detaydan alınacak
                            'ilac_listesi': [],  # Bu veri tabloda yok, detaydan alınacak
                            'toplam_tutar': '',  # Bu veri tabloda yok, detaydan alınacak
                            'ai_decision': None,  # AI kararı için
                            'confidence_score': 0.0  # Güven skoru için
                        }
                        
                        self.prescriptions.append(prescription_data)
                        
                        if row_index <= 5:  # İlk 5 reçeteyi göster
                            print(f'[VERİ] Reçete {row_index}: {prescription_data["recete_no"]} - {prescription_data["hasta_ad"]} {prescription_data["hasta_soyad"]}')
                
                except Exception as e:
                    print(f'[UYARI] Satır {row_index} işlenirken hata: {e}')
            
            print(f'[BAŞARILI] Toplam {len(self.prescriptions)} reçete çıkarıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Reçete verisi çıkarma hatası: {e}')
            return False
    
    def save_prescriptions(self, filename='prescriptions.json'):
        """Reçete verilerini dosyaya kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.prescriptions, f, ensure_ascii=False, indent=2)
            
            print(f'[KAYDET] {len(self.prescriptions)} reçete {filename} dosyasına kaydedildi')
            return True
            
        except Exception as e:
            print(f'[HATA] Dosya kaydetme hatası: {e}')
            return False
    
    def get_prescription_summary(self):
        """Reçete özetini döndür"""
        if not self.prescriptions:
            return "Hiç reçete bulunamadı"
        
        summary = {
            'toplam_recete': len(self.prescriptions),
            'kapsam_dagilimi': {},
            'sonlandirma_durumu': {},
            'ornek_receteler': self.prescriptions[:3]  # İlk 3 reçete örnek olarak
        }
        
        # Kapsam dağılımı
        for prescription in self.prescriptions:
            kapsam = prescription['kapsam']
            summary['kapsam_dagilimi'][kapsam] = summary['kapsam_dagilimi'].get(kapsam, 0) + 1
        
        # Sonlandırma durumu
        for prescription in self.prescriptions:
            durum = prescription['sonlandirildi']
            summary['sonlandirma_durumu'][durum] = summary['sonlandirma_durumu'].get(durum, 0) + 1
        
        return summary
    
    def close(self):
        """Browser'ı kapat"""
        self.browser.quit()
        print('[KAPAT] Browser kapatıldı')

# Test fonksiyonu
def main():
    extractor = PrescriptionExtractor()
    
    try:
        # Başlat ve giriş yap
        if not extractor.start():
            return
        
        # Reçete listesine git
        if not extractor.navigate_to_prescriptions():
            return
        
        # A Grubu reçeteler için filtrele ve ara
        if not extractor.set_filters_and_search('A'):
            return
        
        # Reçete verilerini çıkar
        if extractor.extract_prescription_data():
            # Verileri kaydet
            extractor.save_prescriptions('a_grubu_receteler.json')
            
            # Özet göster
            summary = extractor.get_prescription_summary()
            print(f'\n[ÖZET] REÇETE ÖZETİ:')
            print(f'Toplam: {summary["toplam_recete"]} reçete')
            print(f'Kapsam Dağılımı: {summary["kapsam_dagilimi"]}')
            print(f'Sonlandırma Durumu: {summary["sonlandirma_durumu"]}')
    
    finally:
        extractor.close()

if __name__ == "__main__":
    main()