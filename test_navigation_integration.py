"""
Test Navigation Integration
Test real navigation to prescription list
"""

from unified_prescription_processor import UnifiedPrescriptionProcessor
from selenium.webdriver.common.by import By
import time

def test_navigation_only():
    print("[BASLAT] Testing Navigation Integration")
    
    processor = UnifiedPrescriptionProcessor()
    
    try:
        # Browser başlat
        if not processor._initialize_browser():
            print("[HATA] Browser initialization failed")
            return False
        
        # Login
        if not processor._medula_login():
            print("[HATA] Medula login failed") 
            return False
        
        print("[BASARILI] Medula login successful")
        
        # Advanced extractor'ı init et
        from advanced_prescription_extractor import AdvancedPrescriptionExtractor
        from selenium.webdriver.support.ui import WebDriverWait
        
        processor.extractor = AdvancedPrescriptionExtractor()
        processor.extractor.browser = processor.browser
        processor.extractor.wait = WebDriverWait(processor.browser.driver, 30)
        
        print("[TEST] Attempting navigation to prescription list...")
        
        # Navigation test
        if processor.extractor.navigate_to_prescriptions_auto():
            print("[BASARILI] Navigation to prescription list successful!")
            
            # Sayfada ne var bakalım
            print("[INFO] Current page elements:")
            try:
                # Dropdown'ları say
                dropdowns = processor.browser.driver.find_elements(By.TAG_NAME, "select")
                print(f"  - Dropdowns found: {len(dropdowns)}")
                
                # Butonları say  
                buttons = processor.browser.driver.find_elements(By.XPATH, "//input[@type='submit']")
                print(f"  - Submit buttons found: {len(buttons)}")
                
                # Tabloları say
                tables = processor.browser.driver.find_elements(By.TAG_NAME, "table")
                print(f"  - Tables found: {len(tables)}")
                
                return True
                
            except Exception as e:
                print(f"[HATA] Page analysis error: {e}")
                return False
        else:
            print("[HATA] Navigation failed")
            return False
            
    except Exception as e:
        print(f"[HATA] Test failed: {e}")
        return False
    
    finally:
        if processor.browser:
            print("[TEMIZLIK] Closing browser...")
            processor._cleanup_browser()

if __name__ == "__main__":
    success = test_navigation_only()
    print(f"[SONUC] Navigation test: {'SUCCESS' if success else 'FAILED'}")