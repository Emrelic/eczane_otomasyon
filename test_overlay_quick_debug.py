#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Overlay Debug Test
Overlay sisteminin düzgün çalışıp çalışmadığını hızlıca test eder
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from medula_automation.browser import MedulaBrowser

def test_overlay_quick():
    """Hızlı overlay test"""
    print("🔥 HIZLI OVERLAY DEBUG TEST BAŞLIYOR")
    print("="*60)
    print("🎯 TEST EDECEKLER:")
    print("   1. CAPTCHA auto-login çalışıyor mu?")
    print("   2. Overlay sistem hemen açılıyor mu?") 
    print("   3. Reçete sayfasında buton görünüyor mu?")
    print("="*60)
    
    try:
        # Settings yükle
        print("📋 1. Settings yükleniyor...")
        settings = Settings()
        print("   ✅ Settings yüklendi")
        
        # Browser başlat
        print("🌐 2. Browser başlatılıyor...")
        browser = MedulaBrowser(settings)
        
        if not browser.start():
            print("   ❌ Browser başlatılamadı!")
            return False
        print("   ✅ Browser başlatıldı")
        
        # Medula'ya git
        print("🔐 3. Medula'ya gidiyor...")
        browser.driver.get("https://medeczane.sgk.gov.tr/")
        time.sleep(2)
        print("   ✅ Medula sayfası açıldı")
        
        # Overlay sistemini hemen inject et
        print("💉 4. Overlay sistem inject ediliyor...")
        browser.inject_persistent_frame_system()
        time.sleep(1)  # 1 saniye bekle
        
        # Overlay var mı kontrol et
        overlay_exists = browser.driver.execute_script(
            "return document.getElementById('eczaneOverlaySystem') !== null;"
        )
        
        if overlay_exists:
            print("   ✅ OVERLAY SİSTEM BAŞARILI - SOL PANELDE GÖRÜNMELİ!")
        else:
            print("   ❌ OVERLAY SİSTEM YOK - SORUN VAR!")
            
        # CAPTCHA monitoring kontrol et
        print("🔍 5. CAPTCHA monitoring kontrol ediliyor...")
        captcha_monitor_active = browser.driver.execute_script(
            "return typeof startCaptchaMonitoring === 'function';"
        )
        
        if captcha_monitor_active:
            print("   ✅ CAPTCHA MONITORING AKTİF")
        else:
            print("   ❌ CAPTCHA MONITORING YOK")
            
        print("\n" + "🎯"*30)
        print("TEST SONUÇLARI:")
        print(f"📊 Overlay sistem: {'✅ BAŞARILI' if overlay_exists else '❌ BAŞARISIZ'}")
        print(f"🔍 CAPTCHA monitor: {'✅ AKTİF' if captcha_monitor_active else '❌ BAŞARISIZ'}")
        print("🎯"*30)
        
        if overlay_exists:
            print("\n🎉 BAŞARILI! Sol tarafta yeşil panel görünmeli")
            print("   - 'Bu Reçeteyi Kontrol Et' butonu olmalı")
            print("   - Üst tarafta mavi status bar olmalı")
            print("   - CAPTCHA alanına 6 rakam girin - otomatik login")
        
        # Kullanıcıdan devam etmek isteyip istemediğini sor
        print("\n⏳ Test devam ediyor... Overlay'i test edin!")
        print("   CAPTCHA girin ve login test edin")
        print("   Reçete sayfasına gidin ve buton test edin")
        print("   Çıkmak için Ctrl+C yapın")
        
        try:
            while True:
                time.sleep(5)
                # Her 5 saniyede bir overlay'in varlığını kontrol et
                still_exists = browser.driver.execute_script(
                    "return document.getElementById('eczaneOverlaySystem') !== null;"
                )
                if not still_exists:
                    print("⚠️ Overlay kayboldu - yeniden inject ediliyor")
                    browser.inject_persistent_frame_system()
                    
        except KeyboardInterrupt:
            print("\n🛑 Test durduruldu")
            
        browser.quit()
        return overlay_exists
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

if __name__ == "__main__":
    success = test_overlay_quick()
    sys.exit(0 if success else 1)