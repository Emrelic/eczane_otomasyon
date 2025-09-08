"""Quick test without input"""
from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

try:
    print("Browser testi başlıyor...")
    browser = MedulaBrowser(Settings())
    success = browser.start()
    
    if success:
        print("BASARILI: Browser başarıyla açıldı!")
        time.sleep(3)
        print("Browser 3 saniye sonra kapatılacak...")
        browser.quit()
        print("BASARILI: Test tamamlandı!")
    else:
        print("HATA: Browser açılamadı")
        
except Exception as e:
    print(f"HATA: {e}")