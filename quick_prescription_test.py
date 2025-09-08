"""Quick prescription test with shorter timeouts"""
from advanced_prescription_extractor import AdvancedPrescriptionExtractor
import time

try:
    print("Quick prescription test başlıyor...")
    
    extractor = AdvancedPrescriptionExtractor()
    
    print("1. Browser başlatılıyor...")
    if extractor.start():
        print("✓ Giriş başarılı!")
        
        print("2. Reçete listesine gidiliyor...")
        time.sleep(2)
        
        success = extractor.navigate_to_prescriptions_auto()
        if success:
            print("✓ Reçete listesi açıldı!")
            
            print("3. A Grubu filtrelemesi...")
            time.sleep(3)
            
            print("4. Browser kapatılıyor...")
        else:
            print("✗ Reçete listesine gidemedi")
    else:
        print("✗ Giriş başarısız")
    
    extractor.close()
    print("Test tamamlandı!")
    
except Exception as e:
    print(f"Hata: {e}")
    import traceback
    traceback.print_exc()