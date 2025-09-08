"""
Focused Navigation Test - Core 4 Screens
Tests the most critical navigation path for data extraction
"""

from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time
import json
from datetime import datetime

class FocusedNavigationTest:
    def __init__(self):
        self.browser = MedulaBrowser(Settings())
        self.results = {}
        
    def start(self):
        """Test sistemini başlat"""
        print('[BASLAT] Focused Navigation Test başlatılıyor...')
        
        if not self.browser.start():
            print('[HATA] Browser başlatılamadı')
            return False
            
        if not self.browser.login():
            print('[HATA] Medula girişi başarısız')
            return False
            
        print('[BASARILI] Medula girişi başarılı')
        return True
    
    def test_core_navigation(self):
        """Core 4 ekranı test et: Ana Sayfa → Sorgulama → Tablo → Detay"""
        
        # 1. Ana Sayfa Test
        print('\\n[TEST 1] Ana Sayfa elementleri kontrol ediliyor...')
        ana_sayfa_result = self.test_ana_sayfa()
        self.results['ana_sayfa'] = ana_sayfa_result
        print(f'[SONUC] Ana sayfa: {ana_sayfa_result["success"]}')
        
        # 2. Reçete Listesi Navigasyonu
        print('\\n[TEST 2] Reçete Listesi navigasyonu test ediliyor...')
        if self.navigate_to_recete_listesi():
            print('[BASARILI] Reçete Listesi sayfasına geçildi')
            time.sleep(3)
            
            # 3. Sorgulama Sayfası Test  
            sorgulama_result = self.test_sorgulama_sayfasi()
            self.results['sorgulama'] = sorgulama_result
            print(f'[SONUC] Sorgulama sayfası: {sorgulama_result["success"]}')
            
            # 4. Sorgula butonuna tıklayıp tablo sayfasına geç
            if self.click_sorgula_button():
                print('[BASARILI] Sorgula butonuna tıklandı')
                time.sleep(5)
                
                # 5. Tablo sayfası test
                tablo_result = self.test_tablo_sayfasi()
                self.results['tablo'] = tablo_result
                print(f'[SONUC] Tablo sayfası: {tablo_result["success"]}')
                
                # 6. İlk reçeteye tıklayıp detay sayfasına geç
                if self.click_first_prescription():
                    print('[BASARILI] İlk reçeteye tıklandı')
                    time.sleep(3)
                    
                    # 7. Detay sayfası test
                    detay_result = self.test_detay_sayfasi()
                    self.results['detay'] = detay_result
                    print(f'[SONUC] Detay sayfası: {detay_result["success"]}')
        
        return self.results
    
    def test_ana_sayfa(self):
        """Ana sayfa elementlerini test et"""
        try:
            elements = []
            selectors = [
                "//a[contains(text(), 'Reçete Listesi')]",
                "//span[contains(text(), 'Reçete Listesi')]", 
                "//div[contains(text(), 'Reçete')]",
            ]
            
            for selector in selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        elements.append(selector)
                except:
                    continue
                    
            return {
                'success': len(elements) > 0,
                'found_elements': elements,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def navigate_to_recete_listesi(self):
        """Reçete Listesi navigasyonu"""
        selectors = [
            "//a[contains(text(), 'Reçete Listesi')]",
            "//span[contains(text(), 'Reçete Listesi')]", 
            "//div[contains(text(), 'Reçete Listesi')]",
        ]
        
        for selector in selectors:
            try:
                element = self.browser.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    self.browser.driver.execute_script("arguments[0].click();", element)
                    return True
            except:
                continue
        return False
    
    def test_sorgulama_sayfasi(self):
        """Sorgulama sayfası elementlerini test et"""
        try:
            elements = []
            # Dropdown'ları bul
            selects = self.browser.driver.find_elements(By.TAG_NAME, "select")
            if selects:
                elements.append(f"Dropdown sayısı: {len(selects)}")
                
            # Sorgula butonunu bul
            sorgula_buttons = self.browser.driver.find_elements(By.XPATH, "//input[@value='Sorgula']")
            if sorgula_buttons:
                elements.append("Sorgula butonu bulundu")
                
            return {
                'success': len(elements) > 0,
                'found_elements': elements,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def click_sorgula_button(self):
        """Sorgula butonuna tıkla"""
        try:
            sorgula_button = self.browser.driver.find_element(By.XPATH, "//input[@value='Sorgula']")
            sorgula_button.click()
            return True
        except:
            return False
    
    def test_tablo_sayfasi(self):
        """Tablo sayfası elementlerini test et"""
        try:
            elements = []
            # Tablo kontrolü
            tables = self.browser.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                elements.append(f"Tablo sayısı: {len(tables)}")
                
                # Satır kontrolü
                rows = self.browser.driver.find_elements(By.XPATH, "//table//tr")
                if len(rows) > 1:  # Header + data rows
                    elements.append(f"Satır sayısı: {len(rows)}")
                    
            return {
                'success': len(elements) > 0,
                'found_elements': elements,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def click_first_prescription(self):
        """İlk reçete satırına tıkla"""
        try:
            rows = self.browser.driver.find_elements(By.XPATH, "//table//tr")
            if len(rows) > 1:  # Header haricinde
                rows[1].click()  # İlk data satırı
                return True
            return False
        except:
            return False
    
    def test_detay_sayfasi(self):
        """Detay sayfası butonlarını test et"""
        try:
            buttons = []
            button_selectors = [
                "//input[@value='İlaç']",
                "//input[@value='Rapor']",
                "//input[contains(@value, 'End')]",
                "//input[contains(@value, 'Bilgi')]"
            ]
            
            for selector in button_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        value = element.get_attribute('value')
                        buttons.append(value)
                except:
                    continue
                    
            return {
                'success': len(buttons) > 0,
                'found_buttons': buttons,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_results(self):
        """Sonuçları kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"focused_navigation_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f'\\n[DOSYA] Sonuçlar kaydedildi: {filename}')
        return filename
    
    def close(self):
        """Test sistemini kapat"""
        if self.browser:
            self.browser.quit()
        print('[KAPANDI] Test sistemi kapatıldı')

def main():
    tester = FocusedNavigationTest()
    
    try:
        if not tester.start():
            print('[HATA] Test sistemi başlatılamadı')
            return
        
        # Core navigation test
        results = tester.test_core_navigation()
        
        # Sonuçları göster
        print('\\n[SONUCLAR] Test Sonuçları:')
        print('=' * 40)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r.get('success', False))
        
        for test_name, result in results.items():
            status = '[BASARILI]' if result.get('success', False) else '[BASARISIZ]'
            print(f'{status} {test_name}')
        
        print('=' * 40)
        print(f'[OZET] Başarı Oranı: {successful_tests}/{total_tests}')
        
        # Sonuçları kaydet
        tester.save_results()
        
    except Exception as e:
        print(f'[GENEL HATA] {e}')
    
    finally:
        tester.close()

if __name__ == "__main__":
    main()