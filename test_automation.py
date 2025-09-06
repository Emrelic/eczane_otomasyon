#!/usr/bin/env python3
"""
Selenium Web Automation Test Script
Medula sistemine giriş testleri ve temel browser otomasyonu
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class SeleniumTester:
    """Selenium test sınıfı"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # Logger yapılandırması
        logger.add("logs/test_automation.log", rotation="1 day", level="INFO")
    
    def setup_browser(self, headless=False):
        """Browser'ı başlatır"""
        try:
            logger.info("Browser başlatılıyor...")
            
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.success("Browser başarıyla başlatıldı")
            return True
            
        except Exception as e:
            logger.error(f"Browser başlatılırken hata: {e}")
            return False
    
    def test_basic_navigation(self):
        """Temel navigasyon testi"""
        try:
            logger.info("Temel navigasyon testi başlatılıyor...")
            
            # Google'a git
            self.driver.get("https://www.google.com")
            
            # Sayfa başlığını kontrol et
            assert "Google" in self.driver.title
            
            # Arama kutusunu bul ve test et
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            search_box.send_keys("SGK Medula sistemi")
            search_box.submit()
            
            # Sonuçların yüklenmesini bekle
            self.wait.until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            logger.success("Temel navigasyon testi başarılı")
            return True
            
        except Exception as e:
            logger.error(f"Navigasyon testi hatası: {e}")
            return False
    
    def test_medula_access(self):
        """Medula sistemine erişim testi"""
        try:
            logger.info("Medula erişim testi başlatılıyor...")
            
            # Medula ana sayfasına git
            self.driver.get("https://medula.sgk.gov.tr")
            
            # Sayfa yüklenme kontrolü
            time.sleep(5)  # Sayfa yüklenmesi için bekle
            
            # Sayfa başlığını kontrol et
            page_title = self.driver.title
            logger.info(f"Medula sayfa başlığı: {page_title}")
            
            # Login formunu aramaya çalış
            login_elements = []
            
            # Farklı login element seçicilerini dene
            selectors = [
                "input[type='text'][name*='user']",
                "input[type='text'][name*='login']", 
                "input[id*='user']",
                "input[id*='login']",
                "#username",
                "#user",
                "#loginname",
                "input[placeholder*='kullanıcı']",
                "input[placeholder*='user']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        login_elements.extend(elements)
                        logger.info(f"Login elementi bulundu: {selector}")
                except:
                    continue
            
            if login_elements:
                logger.success("Medula login sayfasına erişim başarılı")
                logger.info(f"{len(login_elements)} adet login elementi bulundu")
                return True
            else:
                # Sayfa kaynağını kaydet (debug için)
                page_source = self.driver.page_source[:1000]
                logger.warning("Login elementi bulunamadı")
                logger.debug(f"Sayfa kaynağı örneği: {page_source}")
                return False
                
        except Exception as e:
            logger.error(f"Medula erişim testi hatası: {e}")
            return False
    
    def test_form_interaction(self):
        """Form etkileşim testi"""
        try:
            logger.info("Form etkileşim testi başlatılıyor...")
            
            # Test için basit bir form sayfasına git
            self.driver.get("https://httpbin.org/forms/post")
            
            # Form elementlerini bul ve test et
            customer_name = self.wait.until(
                EC.presence_of_element_located((By.NAME, "custname"))
            )
            
            customer_name.clear()
            customer_name.send_keys("Test Kullanıcısı")
            
            # Telefon numarası
            phone = self.driver.find_element(By.NAME, "custtel")
            phone.clear()
            phone.send_keys("05551234567")
            
            # Email
            email = self.driver.find_element(By.NAME, "custemail")
            email.clear()  
            email.send_keys("test@example.com")
            
            logger.success("Form etkileşim testi başarılı")
            return True
            
        except Exception as e:
            logger.error(f"Form etkileşim testi hatası: {e}")
            return False
    
    def take_screenshot(self, filename="test_screenshot"):
        """Ekran görüntüsü al"""
        try:
            os.makedirs("screenshots", exist_ok=True)
            filepath = f"screenshots/{filename}_{int(time.time())}.png"
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot kaydedildi: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Screenshot alınamadı: {e}")
            return None
    
    def close_browser(self):
        """Browser'ı kapat"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser kapatıldı")
        except Exception as e:
            logger.error(f"Browser kapatılırken hata: {e}")


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("🚀 Selenium Web Automation Test Başlatılıyor...")
    print("=" * 50)
    
    tester = SeleniumTester()
    test_results = {}
    
    try:
        # Browser başlatma testi
        print("\n1️⃣ Browser Başlatma Testi...")
        if tester.setup_browser(headless=False):
            print("✅ Browser başarıyla başlatıldı")
            test_results['browser_setup'] = True
        else:
            print("❌ Browser başlatılamadı")
            test_results['browser_setup'] = False
            return test_results
        
        # Temel navigasyon testi
        print("\n2️⃣ Temel Navigasyon Testi...")
        if tester.test_basic_navigation():
            print("✅ Navigasyon testi başarılı")
            test_results['navigation'] = True
        else:
            print("❌ Navigasyon testi başarısız")
            test_results['navigation'] = False
        
        # Screenshot al
        tester.take_screenshot("navigation_test")
        
        # Medula erişim testi
        print("\n3️⃣ Medula Erişim Testi...")
        if tester.test_medula_access():
            print("✅ Medula erişimi başarılı")
            test_results['medula_access'] = True
        else:
            print("⚠️ Medula erişiminde sorun (normal olabilir)")
            test_results['medula_access'] = False
        
        # Screenshot al
        tester.take_screenshot("medula_test")
        
        # Form etkileşim testi
        print("\n4️⃣ Form Etkileşim Testi...")
        if tester.test_form_interaction():
            print("✅ Form etkileşimi başarılı")
            test_results['form_interaction'] = True
        else:
            print("❌ Form etkileşimi başarısız")
            test_results['form_interaction'] = False
        
        # Screenshot al
        tester.take_screenshot("form_test")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Test sırasında beklenmeyen hata: {e}")
    finally:
        # Browser'ı kapat
        print("\n🔄 Browser kapatılıyor...")
        tester.close_browser()
    
    # Sonuçları özetle
    print("\n" + "=" * 50)
    print("📊 TEST SONUÇLARI:")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    print(f"\nTOPLAM: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Selenium automation hazır.")
    else:
        print("⚠️ Bazı testler başarısız. Logları kontrol edin.")
    
    return test_results


if __name__ == "__main__":
    # Test menüsü
    print("Selenium Web Automation Test")
    print("1. Tüm testleri çalıştır")
    print("2. Sadece browser testi")
    print("3. Sadece Medula testi")
    
    choice = input("Seçiminizi yapın (1-3): ").strip()
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        tester = SeleniumTester()
        if tester.setup_browser():
            print("✅ Browser testi başarılı")
            time.sleep(3)
            tester.close_browser()
    elif choice == "3":
        tester = SeleniumTester()
        if tester.setup_browser():
            tester.test_medula_access()
            time.sleep(5)
            tester.close_browser()
    else:
        print("Geçersiz seçim!")