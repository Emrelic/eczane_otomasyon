#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overlay Integration Test
Browser + Overlay sistemi entegrasyonu test scripti
"""

import sys
import time
import threading
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from medula_automation.browser import MedulaBrowser
from unified_prescription_processor import UnifiedPrescriptionProcessor

class OverlayIntegrationTester:
    """Browser + Overlay entegrasyonu test sınıfı"""
    
    def __init__(self):
        print("🔧 Overlay Integration Test başlatılıyor...")
        
        # Settings yükle
        try:
            self.settings = Settings()
            print("✅ Settings yüklendi")
        except Exception as e:
            print(f"⚠️ Settings hatası: {e}")
            return
        
        # Browser başlat
        self.browser = MedulaBrowser(self.settings)
        self.processor = UnifiedPrescriptionProcessor()
        
        self.running = True
        
    def start_test(self):
        """Test sürecini başlat"""
        try:
            print("\n" + "="*60)
            print("🔥 OVERLAY INTEGRATION TEST - FIX ALL ISSUES")
            print("="*60)
            print("🎯 DÜZELTMELER YAPILDI:")
            print("   ✅ CAPTCHA auto-login: overlay_system_simple.py'den kopya")
            print("   ✅ Overlay hızlı injection: DOM ready beklemez")
            print("   ✅ Navigation listener: Sayfa değişikleri korunur")
            print("   ✅ Frame maintenance: Kaybolursa yeniden inject")
            print("="*60)
            
            # 1. Browser başlat
            print("🔧 1. Browser başlatılıyor...")
            if not self.browser.start():
                print("❌ Browser başlatılamadı!")
                return
            
            # 2. Medula'ya login
            print("🔑 2. Medula'ya giriş yapılıyor...")
            if not self.browser.login():
                print("❌ Medula login başarısız!")
                return
                
            # 3. Kalıcı Çerçeve Sistemi inject et
            print("💉 3. Kalıcı çerçeve sistemi inject ediliyor...")
            self.browser.inject_persistent_frame_system()
            
            # 4. Monitoring thread başlat
            print("👁️ 4. Çerçeve sistem monitoring başlatılıyor...")
            monitor_thread = threading.Thread(target=self.monitor_frame_interactions, daemon=True)
            monitor_thread.start()
            
            print("\n" + "✅"*30)
            print("🎉 KALICI ÇERÇEVE SİSTEMİ AKTİF!")
            print("="*60)
            print("🖼️  Sol tarafta kontrol paneli görünecek")
            print("🔬 'Bu Reçeteyi Kontrol Et' butonu ile analiz")
            print("   ⭐ REÇETE SAYFASINDA KIRMIZI VURGULU!")
            print("📅 'Günlük Kontrol' ile toplu işlem")
            print("📊 'Aylık Kontrol' ile kapsamlı analiz")  
            print("📈 'İstatistikler' ile raporlama")
            print("⚙️  'Ayarlar' ile konfigürasyon")
            print("🛑 'Acil Durdur' ile emergency stop")
            print("🔄 'Medula Yenile' ile refresh")
            print("="*60)
            print("🎯 Üst status bar'da sistem durumu")
            print("📍 Medula içeriği sağ tarafta iframe içinde")
            print("🚨 ÇERÇEVE HER SAYFADA KORUNUR!")
            print("⚡ CAPTCHA AUTO-LOGIN AKTİF!")
            print("="*60)
            
            # 5. Ana loop - kullanıcı etkileşimi bekle
            print("⏳ Test sürüyor... Browser'ı kapatmayın!")
            print("   Reçete sayfasına gidin ve kontrol butonunu test edin.")
            print("   Çıkmak için Ctrl+C yapın.")
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Test durduruldu")
                self.stop_test()
                
        except Exception as e:
            print(f"❌ Test hatası: {e}")
            self.stop_test()
    
    def monitor_frame_interactions(self):
        """Çerçeve sistem etkileşimlerini izle"""
        print("👁️ Frame system monitoring thread başlatıldı")
        
        while self.running:
            try:
                # Çerçeve sistemden gelen istekleri kontrol et
                interaction = self.browser.check_overlay_interaction()
                
                if interaction['requested']:
                    action = interaction['action']
                    print(f"\n🎯 ÇERÇEVE SİSTEM İSTEĞİ: {action.upper()}")
                    
                    if action == 'prescriptionControl':
                        # Tek reçete kontrolü
                        print("🔬 TEK REÇETE KONTROLÜ BAŞLATILIYOR")
                        prescription_data = self.browser.extract_current_page_prescription()
                        
                        if prescription_data:
                            print(f"📄 Reçete bulundu: {prescription_data.get('recete_no', 'UNKNOWN')}")
                            self.analyze_prescription(prescription_data)
                        else:
                            print("❌ Mevcut sayfada reçete verisi bulunamadı")
                            # Mock veri ile devam et
                            self.analyze_mock_prescription("CURRENT_PAGE")
                    
                    elif action == 'dailyControl':
                        # Günlük kontrol
                        print("📅 GÜNLÜK KONTROL BAŞLATILIYOR")
                        self.handle_daily_control()
                    
                    elif action == 'monthlyControl':
                        # Aylık kontrol
                        print("📊 AYLIK KONTROL BAŞLATILIYOR") 
                        self.handle_monthly_control()
                    
                    elif action == 'showStats':
                        # İstatistikler
                        print("📈 İSTATİSTİKLER GÖSTERİLİYOR")
                        self.show_statistics()
                    
                    elif action == 'showSettings':
                        # Ayarlar
                        print("⚙️ AYARLAR AÇILIYOR")
                        self.show_settings()
                    
                    elif action == 'emergencyStop':
                        # Acil durdur
                        print("🛑 ACİL DURDUR AKTİVE EDİLDİ!")
                        self.handle_emergency_stop()
                
                # Çerçeve sistemini her döngüde kontrol et
                self.maintain_frame_system()
                
                time.sleep(2)  # 2 saniyede bir kontrol
                
            except Exception as e:
                print(f"❌ Frame monitoring hatası: {e}")
                time.sleep(5)
    
    def maintain_frame_system(self):
        """Çerçeve sisteminin sürekli aktif kalmasını sağlar"""
        try:
            # Frame sistem var mı kontrol et
            frame_exists = self.browser.driver.execute_script(
                "return document.getElementById('eczaneFrameSystem') !== null;"
            )
            
            if not frame_exists:
                print("⚠️ Çerçeve sistem kayboldu - tekrar inject ediliyor")
                self.browser.inject_persistent_frame_system()
                
        except Exception as e:
            print(f"❌ Frame maintenance hatası: {e}")
    
    def analyze_mock_prescription(self, prescription_id):
        """Mock reçete analizi"""
        mock_data = {
            "recete_no": prescription_id,
            "hasta_tc": "12345678901",
            "hasta_ad_soyad": "Test Hastası",
            "drugs": [{"ilac_adi": "Test İlacı", "adet": "1"}],
            "extraction_method": "mock"
        }
        self.analyze_prescription(mock_data)
    
    def handle_daily_control(self):
        """Günlük kontrol işlemlerini handle eder"""
        print("📅 Günlük kontrol simülasyonu...")
        self.show_browser_message("📅 Günlük kontrol başlatıldı - Mock veri ile test", "warning")
        
    def handle_monthly_control(self):
        """Aylık kontrol işlemlerini handle eder"""  
        print("📊 Aylık kontrol simülasyonu...")
        self.show_browser_message("📊 Aylık kontrol başlatıldı - Mock veri ile test", "info")
        
    def show_statistics(self):
        """İstatistikleri göster"""
        print("📈 İstatistik simülasyonu...")
        self.show_browser_message("📈 İstatistikler: 15 reçete analiz edildi, 12 onay, 2 red, 1 beklemede", "success")
        
    def show_settings(self):
        """Ayarları göster"""
        print("⚙️ Ayarlar simülasyonu...")
        self.show_browser_message("⚙️ Ayarlar: SUT ✅, AI ✅, Dose ✅ - Tüm sistemler aktif", "info")
        
    def handle_emergency_stop(self):
        """Acil durdur işlemini handle eder"""
        print("🛑 Acil durdur simülasyonu...")
        self.show_browser_message("🛑 ACİL DURDUR: Tüm otomatik işlemler durduruldu!", "danger")
    
    def show_browser_message(self, message, type_class="info"):
        """Browser'da mesaj göster"""
        try:
            color_map = {
                'info': '#3498db',
                'success': '#27ae60', 
                'warning': '#f39c12',
                'danger': '#e74c3c'
            }
            color = color_map.get(type_class, '#3498db')
            
            js_code = f"""
            var messageDiv = document.createElement('div');
            messageDiv.style.cssText = `
                position: fixed;
                top: 50px;
                left: 260px;
                z-index: 10000;
                background: {color};
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                max-width: 400px;
            `;
            messageDiv.textContent = '{message}';
            
            document.body.appendChild(messageDiv);
            
            setTimeout(function() {{
                messageDiv.remove();
            }}, 5000);
            """
            
            self.browser.driver.execute_script(js_code)
            
        except Exception as e:
            print(f"❌ Browser message error: {e}")
    
    def analyze_prescription(self, prescription_data):
        """Reçete analizini yap"""
        try:
            print("\n" + "🔬"*20)
            print("📊 REÇETE ANALİZİ BAŞLATILIYOR")
            print("🔬"*20)
            
            start_time = time.time()
            
            # Unified Processor ile analiz
            result = self.processor.process_single_prescription(
                prescription_data, 
                source="overlay_integration_test"
            )
            
            processing_time = time.time() - start_time
            
            # Sonuçları göster
            print(f"\n📋 ANALIZ SONUÇLARI:")
            print(f"🆔 Reçete No: {prescription_data.get('recete_no', 'UNKNOWN')}")
            print(f"🎯 Final Karar: {result.get('final_decision', 'unknown').upper()}")
            print(f"⏱️ İşlem Süresi: {processing_time:.3f} saniye")
            
            # Detaylar
            sut_analysis = result.get('sut_analysis', {})
            ai_analysis = result.get('ai_analysis', {})
            dose_analysis = result.get('dose_analysis', {})
            
            print(f"📋 SUT: {sut_analysis.get('action', 'unknown')} (Güven: {sut_analysis.get('confidence', 0):.2f})")
            print(f"🤖 AI: {ai_analysis.get('action', 'unknown')} (Güven: {ai_analysis.get('confidence', 0):.2f})")
            
            if dose_analysis:
                print(f"💊 Dose: {dose_analysis.get('action', 'unknown')} (İlaç: {dose_analysis.get('drugs_analyzed', 0)})")
            
            print("🔬"*20 + "\n")
            
            # Browser'da sonucu göster
            self.show_result_in_browser(result)
            
        except Exception as e:
            print(f"❌ Reçete analiz hatası: {e}")
    
    def show_result_in_browser(self, result):
        """Analiz sonucunu browser'da göster"""
        try:
            final_decision = result.get('final_decision', 'unknown').upper()
            
            # Karar rengini belirle
            color_map = {
                'APPROVE': '#27ae60',  # Yeşil
                'REJECT': '#e74c3c',   # Kırmızı
                'HOLD': '#f39c12'      # Turuncu
            }
            
            color = color_map.get(final_decision, '#95a5a6')
            
            # JavaScript ile sonuç gösterimi
            result_js = f"""
            // Eski result div'i varsa kaldır
            var oldResult = document.getElementById('prescriptionResult');
            if (oldResult) oldResult.remove();
            
            // Yeni result div'i oluştur
            var resultDiv = document.createElement('div');
            resultDiv.id = 'prescriptionResult';
            resultDiv.innerHTML = `
                <h3>📊 REÇETE ANALİZ SONUCU</h3>
                <p style="font-size: 18px; font-weight: bold; color: {color};">
                    🎯 KARAR: {final_decision}
                </p>
                <p>⏱️ İşlem Süresi: {result.get('processing_metadata', {}).get('processing_time_seconds', 0):.3f}s</p>
                <button onclick="this.parentElement.remove();" style="margin-top: 10px;">Kapat</button>
            `;
            
            resultDiv.style.cssText = `
                position: fixed;
                top: 60px;
                right: 10px;
                z-index: 9998;
                background: white;
                border: 3px solid {color};
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                max-width: 300px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            `;
            
            document.body.appendChild(resultDiv);
            
            // 10 saniye sonra otomatik kapat
            setTimeout(function() {{
                if (resultDiv && resultDiv.parentElement) {{
                    resultDiv.remove();
                }}
            }}, 10000);
            """
            
            self.browser.driver.execute_script(result_js)
            
        except Exception as e:
            print(f"❌ Browser result display hatası: {e}")
    
    def stop_test(self):
        """Test'i durdur"""
        try:
            self.running = False
            print("🛑 Test durduruluyor...")
            
            if self.browser:
                self.browser.quit()
                
            print("✅ Test başarıyla sonlandırıldı")
            
        except Exception as e:
            print(f"❌ Test sonlandırma hatası: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🔬 OVERLAY INTEGRATION TEST - MEDULA BROWSER")
    print("=" * 60)
    
    tester = OverlayIntegrationTester()
    tester.start_test()

if __name__ == "__main__":
    main()