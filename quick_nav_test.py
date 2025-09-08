"""Quick Navigation Test - No Emojis"""
from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

def test_medula_navigation():
    print("MEDULA NAVIGATION TEST BAŞLIYOR...")
    
    browser = MedulaBrowser(Settings())
    
    try:
        # Browser başlat
        if not browser.start():
            print("HATA: Browser başlatılamadı")
            return
        
        print("BROWSER AÇILDI")
        
        # Login
        if not browser.login():
            print("HATA: Login başarısız")
            return
        
        print("LOGIN BAŞARILI")
        time.sleep(3)
        
        # Ana sayfa kontrol
        print("\n1. ANA SAYFA TEST:")
        elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'Reçete')]")
        print(f"   - Reçete elementleri bulundu: {len(elements)}")
        
        # Reçete Listesi linkini bul
        print("\n2. REÇETE LİSTESİ NAVİGASYON:")
        selectors = [
            "//span[contains(text(), 'Reçete Listesi')]",
            "//a[contains(text(), 'Reçete Listesi')]"
        ]
        
        for selector in selectors:
            try:
                element = browser.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    print(f"   - Element bulundu: {selector}")
                    browser.driver.execute_script("arguments[0].click();", element)
                    print("   - Tıklama başarılı")
                    time.sleep(5)
                    break
            except Exception as e:
                print(f"   - Selector başarısız {selector}: {e}")
        
        # Sorgulama sayfası kontrol
        print("\n3. SORGULAMA SAYFASI:")
        dropdowns = browser.driver.find_elements(By.TAG_NAME, "select")
        print(f"   - Dropdown sayısı: {len(dropdowns)}")
        
        buttons = browser.driver.find_elements(By.XPATH, "//input[@type='submit']")
        print(f"   - Submit button sayısı: {len(buttons)}")
        
        # Sorgula butonuna tıkla
        if buttons:
            try:
                buttons[0].click()
                print("   - Sorgula butonuna tıklandı")
                time.sleep(5)
            except Exception as e:
                print(f"   - Sorgula tıklama hatası: {e}")
        
        # Tablo kontrol
        print("\n4. TABLO KONTROL:")
        tables = browser.driver.find_elements(By.TAG_NAME, "table")
        print(f"   - Tablo sayısı: {len(tables)}")
        
        if tables:
            rows = browser.driver.find_elements(By.XPATH, "//table//tr")
            print(f"   - Satır sayısı: {len(rows)}")
            
            # İlk data satırına tıkla (header haricinde)
            if len(rows) > 1:
                try:
                    rows[1].click()
                    print("   - İlk data satırına tıklandı")
                    time.sleep(5)
                    
                    # Reçete detay sayfası kontrol
                    print("\n5. REÇETE DETAY KONTROL:")
                    detail_buttons = browser.driver.find_elements(By.XPATH, "//input[@type='submit']")
                    print(f"   - Detay buton sayısı: {len(detail_buttons)}")
                    
                    for i, button in enumerate(detail_buttons[:3]):  # İlk 3 butonu test et
                        try:
                            value = button.get_attribute('value')
                            print(f"   - Buton {i+1}: {value}")
                        except:
                            print(f"   - Buton {i+1}: value alınamadı")
                            
                except Exception as e:
                    print(f"   - Satır tıklama hatası: {e}")
        
        print("\nTEST TAMAMLANDI")
        
    except Exception as e:
        print(f"GENEL HATA: {e}")
    
    finally:
        browser.quit()
        print("BROWSER KAPATILDI")

if __name__ == "__main__":
    test_medula_navigation()