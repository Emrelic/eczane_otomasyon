#!/usr/bin/env python3
"""
Eczane Reçete Kontrol Otomasyonu
Ana dosya - proje giriş noktası
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from medula_automation.browser import MedulaBrowser
from ai_analyzer.decision_engine import DecisionEngine


def main():
    """Ana fonksiyon - otomasyon işlemlerini başlatır"""
    try:
        # Ayarları yükle
        settings = Settings()
        
        # Bileşenleri başlat
        browser = MedulaBrowser(settings)
        ai_engine = DecisionEngine(settings)
        
        print("Eczane Reçete Kontrol Otomasyonu başlatıldı...")
        
        # Ana işlem döngüsü
        while True:
            try:
                # Kullanıcıdan işlem seçimi
                print("\n1. Reçete kontrolü başlat")
                print("2. Ayarları görüntüle")
                print("3. Çıkış")
                
                choice = input("Seçiminizi yapın (1-3): ").strip()
                
                if choice == "1":
                    start_prescription_check(browser, ai_engine)
                elif choice == "2":
                    display_settings(settings)
                elif choice == "3":
                    print("Program sonlandırılıyor...")
                    break
                else:
                    print("Geçersiz seçim! Lütfen 1-3 arasında bir sayı girin.")
                    
            except KeyboardInterrupt:
                print("\n\nProgram kullanıcı tarafından durduruldu.")
                break
            except Exception as e:
                print(f"İşlem sırasında hata oluştu: {e}")
                
    except Exception as e:
        print(f"Program başlatılırken hata oluştu: {e}")
        return 1
    
    finally:
        # Kaynakları temizle
        if 'browser' in locals():
            browser.quit()
    
    return 0


def start_prescription_check(browser, ai_engine):
    """Reçete kontrol işlemini başlatır"""
    print("Reçete kontrolü başlatılıyor...")
    
    try:
        # Browser'ı başlat
        browser.start()
        
        # Medula'ya giriş yap
        if browser.login():
            print("Medula'ya başarıyla giriş yapıldı.")
            
            # Reçete kontrol işlemlerini gerçekleştir
            prescriptions = browser.get_pending_prescriptions()
            
            if prescriptions:
                print(f"{len(prescriptions)} adet bekleyen reçete bulundu.")
                
                for prescription in prescriptions:
                    # AI ile karar ver
                    decision = ai_engine.analyze_prescription(prescription)
                    
                    # Kararı uygula
                    browser.apply_decision(prescription, decision)
                    
            else:
                print("Bekleyen reçete bulunamadı.")
                
        else:
            print("Medula'ya giriş yapılamadı!")
            
    except Exception as e:
        print(f"Reçete kontrol sırasında hata: {e}")


def display_settings(settings):
    """Mevcut ayarları görüntüler"""
    print("\n=== MEVCUT AYARLAR ===")
    print(f"Medula URL: {settings.medula_url}")
    print(f"Tarayıcı: {settings.browser_type}")
    print(f"Headless mod: {settings.headless}")
    print(f"OpenAI Model: {settings.openai_model}")
    print("========================")


if __name__ == "__main__":
    sys.exit(main())