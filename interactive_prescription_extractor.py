"""
İnteraktif Reçete Detay Çıkarma Sistemi
Her adımda kullanıcıdan onay alır
"""

from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import sys
import os

# Windows konsol için UTF-8 encoding ayarla
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')

class InteractivePrescriptionExtractor:
    def __init__(self):
        self.browser = MedulaBrowser(Settings())
        self.wait = None
        self.prescriptions_with_details = []
    
    def start(self):
        """Browser'ı başlat ve giriş yap"""
        print('[BAŞLAT] İnteraktif reçete çıkarma sistemi başlatılıyor...')
        print('Bu sistemde her adımda manuel kontrol yapabilirsiniz.')
        input('Devam etmek için ENTER basın...')
        
        success = self.browser.start()
        
        if success:
            self.wait = WebDriverWait(self.browser.driver, 30)
            print('[BİLGİ] Browser açıldı. Şimdi giriş yapılacak...')
            
            if self.browser.login():
                print('[BAŞARILI] Medula girişi başarılı!')
                print('[BİLGİ] Ana sayfa yüklendi. Sol menüyü kontrol edin.')
                input('Ana sayfada olduğunuzdan emin olduktan sonra ENTER basın...')
                return True
            else:
                print('[HATA] Medula girişi başarısız!')
                return False
        return False
    
    def navigate_to_prescriptions_interactive(self):
        """İnteraktif reçete listesine gitme"""
        print('\n[ADIM 1] REÇETE LİSTESİNE GİTME')
        print('=' * 50)
        print('Sol menüden "Reçete Listesi" linkini bulup tıklayın.')
        print('Eğer bulamıyorsanız, "Reçete" altındaki alt menülere bakın.')
        
        choice = input('Manuel tıkladınız mı? (e/h): ').lower()
        
        if choice == 'e':
            print('[BAŞARILI] Reçete Listesi sayfasına gittiğiniz kabul edildi')
            print('Sayfa yüklenene kadar bekleyin...')
            time.sleep(3)
            return True
        else:
            print('[İPTAL] Reçete listesine gidilmedi')
            return False
    
    def set_filters_interactive(self):
        """İnteraktif filtre ayarlama"""
        print('\n[ADIM 2] FİLTRE AYARLAMA')
        print('=' * 50)
        print('Reçete Listesi sayfasında:')
        print('1. "Fatura Türü" dropdown\'ını bulun')
        print('2. "A Grubu" seçin')
        print('3. "Sorgula" butonuna basın')
        print('4. Reçete tablosu yüklenene kadar bekleyin')
        
        choice = input('A Grubu filtresi uyguladınız mı? (e/h): ').lower()
        
        if choice == 'e':
            print('[BAŞARILI] A Grubu filtresi uygulandı')
            print('Tablo yüklenene kadar bekleyin...')
            time.sleep(5)
            return True
        else:
            print('[İPTAL] Filtre uygulanmadı')
            return False
    
    def get_prescription_count_interactive(self):
        """Kaç reçete olduğunu kullanıcıdan sor"""
        print('\n[ADIM 3] REÇETE SAYISI KONTROLÜ')
        print('=' * 50)
        print('Ekranda kaç reçete görüyorsunuz?')
        
        try:
            count = int(input('Reçete sayısını girin: '))
            print(f'[BİLGİ] {count} reçete bulundu')
            return max(1, min(count, 5))  # En az 1, en fazla 5
        except:
            print('[VARSAYILAN] 3 reçete kabul edildi')
            return 3
    
    def extract_prescription_manually(self, index, total):
        """Tek bir reçetenin detaylarını manuel yönlendirme ile çıkar"""
        print(f'\n[ADIM 4.{index}] REÇETE {index}/{total} DETAY ÇIKARMASI')
        print('=' * 50)
        
        # Reçete temel bilgilerini al
        print(f'Reçete {index} için temel bilgileri girelim:')
        
        recete_no = input('Reçete No: ').strip()
        hasta_ad = input('Hasta Adı: ').strip()
        hasta_soyad = input('Hasta Soyadı: ').strip()
        
        prescription_data = {
            'index': index,
            'recete_no': recete_no,
            'hasta_ad': hasta_ad,
            'hasta_soyad': hasta_soyad,
            'extraction_time': datetime.now().isoformat()
        }
        
        print(f'\\n[DETAY ÇIKARMAYA BAŞLA]')
        print('Şimdi bu reçetenin detaylarını çıkaracağız.')
        
        choice = input('Devam etmek istiyor musunuz? (e/h): ').lower()
        if choice != 'e':
            print('[ATLANDI] Bu reçete atlandı')
            return None
        
        # Reçete detayına gir
        print('\\n1. Reçete tablosunda bu reçetenin hasta isminin üzerine TIKLAYIN')
        input('Reçete detay sayfası açıldıktan sonra ENTER basın...')
        
        # Temel detayları manuel sor
        print('\\n2. HASTA BİLGİLERİ')
        hasta_tc = input('TC Kimlik No (ekrandan okuyun): ').strip()
        dogum_tarihi = input('Doğum Tarihi: ').strip()
        
        prescription_data.update({
            'hasta_tc': hasta_tc,
            'dogum_tarihi': dogum_tarihi
        })
        
        # İlaç listesi
        print('\\n3. İLAÇ LİSTESİ')
        print('Kaç ilaç var?')
        
        try:
            ilac_sayisi = int(input('İlaç sayısı: '))
        except:
            ilac_sayisi = 1
        
        drugs = []
        for i in range(ilac_sayisi):
            print(f'\\n İlaç {i+1}:')
            ilac_adi = input(f'  İlaç Adı {i+1}: ').strip()
            barkod = input(f'  Barkod {i+1}: ').strip()
            adet = input(f'  Adet {i+1}: ').strip()
            
            drugs.append({
                'ilac_adi': ilac_adi,
                'barkod': barkod,
                'adet': adet
            })
        
        prescription_data['drugs'] = drugs
        
        # İlaç Bilgileri sayfası
        print('\\n4. İLAÇ BİLGİLERİ')
        print('"İlaç Bilgi" butonuna tıklayın')
        
        choice = input('İlaç Bilgi sayfasını açtınız mı? (e/h): ').lower()
        if choice == 'e':
            print('İlaç mesajları var mı?')
            mesajlar = input('Mesajları yazın (yoksa boş bırakın): ').strip()
            prescription_data['ilac_mesajlari'] = mesajlar
            
            print('"Geri Dön" butonuna basın')
            input('Ana reçete detayına döndükten sonra ENTER basın...')
        
        # Rapor bilgileri  
        print('\\n5. RAPOR BİLGİLERİ')
        print('"Rapor" butonuna tıklayın')
        
        choice = input('Rapor sayfasını açtınız mı? (e/h): ').lower()
        if choice == 'e':
            rapor_no = input('Rapor Numarası: ').strip()
            rapor_tarihi = input('Rapor Tarihi: ').strip()
            
            prescription_data.update({
                'rapor_no': rapor_no,
                'rapor_tarihi': rapor_tarihi
            })
            
            print('"Geri Dön" butonuna basın')
            input('Ana reçete detayına döndükten sonra ENTER basın...')
        
        # Ana listeye dön
        print('\\n6. ANA LİSTEYE DÖNÜŞ')
        print('"Geri Dön" butonuna basın (ana reçete listesine dönmek için)')
        input('Reçete listesinde olduğunuzdan emin olduktan sonra ENTER basın...')
        
        print(f'[TAMAMLANDI] Reçete {index} detayları kaydedildi')
        return prescription_data
    
    def save_manual_prescriptions(self, filename='manual_detailed_prescriptions.json'):
        """Manuel toplanan verileri kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.prescriptions_with_details, f, ensure_ascii=False, indent=2)
            
            print(f'[KAYDET] {len(self.prescriptions_with_details)} reçete detayı {filename} dosyasına kaydedildi')
            return True
            
        except Exception as e:
            print(f'[HATA] Dosya kaydetme hatası: {e}')
            return False
    
    def close(self):
        """Browser'ı kapat"""
        choice = input('\\nBrowser kapatılsın mı? (e/h): ').lower()
        if choice == 'e':
            self.browser.quit()
            print('[KAPAT] Browser kapatıldı')
        else:
            print('[AÇIK] Browser açık bırakıldı - manuel olarak kapatabilirsiniz')

def main():
    print('REÇeTE DETAY ÇIKARMA SİSTEMİ - İNTERAKTİF SÜRÜM')
    print('=' * 60)
    print('Bu versiyon sizinle adım adım çalışır.')
    print('Her aşamada ne yapacağınızı söyler ve onayınızı bekler.')
    print()
    
    extractor = InteractivePrescriptionExtractor()
    
    try:
        # Başlat ve giriş yap
        if not extractor.start():
            return
        
        # Reçete listesine git
        if not extractor.navigate_to_prescriptions_interactive():
            return
        
        # Filtreleri ayarla
        if not extractor.set_filters_interactive():
            return
        
        # Reçete sayısını öğren
        prescription_count = extractor.get_prescription_count_interactive()
        
        # Her reçetin detayını çıkar
        print(f'\\n[BAŞLAT] {prescription_count} reçetenin detayları çıkarılacak')
        
        for i in range(1, prescription_count + 1):
            prescription_data = extractor.extract_prescription_manually(i, prescription_count)
            
            if prescription_data:
                extractor.prescriptions_with_details.append(prescription_data)
                
                print(f'\\n[DURUM] {i}/{prescription_count} reçete tamamlandı')
                
                if i < prescription_count:
                    choice = input('Sonraki reçeteye geçelim mi? (e/h): ').lower()
                    if choice != 'e':
                        break
        
        # Verileri kaydet
        if extractor.prescriptions_with_details:
            extractor.save_manual_prescriptions()
            
            print(f'\\n[ÖZET] İşlem tamamlandı!')
            print(f'- Toplam reçete: {len(extractor.prescriptions_with_details)}')
            print(f'- Kayıt dosyası: manual_detailed_prescriptions.json')
        else:
            print('\\n[BİLGİ] Hiç reçete detayı kaydedilmedi')
    
    finally:
        extractor.close()

if __name__ == "__main__":
    main()