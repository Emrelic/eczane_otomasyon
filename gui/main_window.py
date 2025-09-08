"""
Ana GUI Penceresi
CustomTkinter kullanarak modern arayüz
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import sys
from pathlib import Path

# Proje root dizinini path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import Settings
from medula_automation.browser import MedulaBrowser
from ai_analyzer.decision_engine import DecisionEngine
from database.models import get_db_manager


class EczaneOtomasyonGUI:
    """Ana GUI sınıfı"""
    
    def __init__(self):
        # CustomTkinter temayı ayarla
        ctk.set_appearance_mode("system")  # system, light, dark
        ctk.set_default_color_theme("blue")  # blue, green, dark-blue
        
        # Ana pencereyi oluştur
        self.root = ctk.CTk()
        self.root.title("Eczane Reçete Kontrol Otomasyonu")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Ayarları yükle
        try:
            self.settings = Settings()
        except ValueError as e:
            messagebox.showerror("Ayar Hatası", str(e))
            self.root.destroy()
            return
        
        # Bileşenleri başlat
        self.browser = None
        self.ai_engine = None
        self.db_manager = get_db_manager()
        
        # GUI durumu
        self.automation_running = False
        self.automation_thread = None
        
        # GUI bileşenlerini oluştur
        self.create_widgets()
        self.update_statistics()
    
    def create_widgets(self):
        """GUI bileşenlerini oluşturur"""
        
        # Ana başlık
        self.title_label = ctk.CTkLabel(
            self.root,
            text="🏥 Eczane Reçete Kontrol Otomasyonu",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # Ana container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sol panel - Kontroller
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)
        
        # Sağ panel - İçerik
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.create_control_panel()
        self.create_content_panel()
    
    def create_control_panel(self):
        """Sol kontrol panelini oluşturur"""
        
        # Panel başlığı
        panel_title = ctk.CTkLabel(
            self.left_panel,
            text="Kontrol Paneli",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        panel_title.pack(pady=(10, 20))
        
        # Otomasyon kontrolleri
        automation_frame = ctk.CTkFrame(self.left_panel)
        automation_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            automation_frame,
            text="🤖 Otomasyon",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Başlat/Durdur butonu
        self.start_stop_btn = ctk.CTkButton(
            automation_frame,
            text="▶️ Başlat",
            command=self.toggle_automation,
            width=150
        )
        self.start_stop_btn.pack(pady=5)
        
        # Durum göstergesi
        self.status_label = ctk.CTkLabel(
            automation_frame,
            text="⏹️ Durduruldu",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # Test butonu
        self.test_btn = ctk.CTkButton(
            automation_frame,
            text="🧪 Test Et",
            command=self.run_tests,
            width=150
        )
        self.test_btn.pack(pady=5)
        
        # Veritabanı kontrolleri
        db_frame = ctk.CTkFrame(self.left_panel)
        db_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            db_frame,
            text="💾 Veritabanı",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.db_test_btn = ctk.CTkButton(
            db_frame,
            text="🔧 DB Test",
            command=self.test_database,
            width=150
        )
        self.db_test_btn.pack(pady=5)
        
        self.stats_btn = ctk.CTkButton(
            db_frame,
            text="📊 İstatistikler",
            command=self.show_statistics,
            width=150
        )
        self.stats_btn.pack(pady=5)
        
        # Ayarlar kontrolleri
        settings_frame = ctk.CTkFrame(self.left_panel)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Ayarlar",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.settings_btn = ctk.CTkButton(
            settings_frame,
            text="🔧 Ayarları Göster",
            command=self.show_settings,
            width=150
        )
        self.settings_btn.pack(pady=5)
        
        # Headless mode toggle
        self.headless_var = ctk.BooleanVar(value=self.settings.headless)
        self.headless_check = ctk.CTkCheckBox(
            settings_frame,
            text="Headless Mode",
            variable=self.headless_var,
            command=self.toggle_headless
        )
        self.headless_check.pack(pady=5)
    
    def create_content_panel(self):
        """Sağ içerik panelini oluşturur"""
        
        # Sekme sistemi oluştur
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dashboard sekmesi
        self.dashboard_tab = self.tabview.add("📊 Dashboard")
        self.create_dashboard_tab()
        
        # Reçeteler sekmesi
        self.prescriptions_tab = self.tabview.add("📋 Reçeteler")
        self.create_prescriptions_tab()
        
        # Loglar sekmesi
        self.logs_tab = self.tabview.add("📝 Loglar")
        self.create_logs_tab()
        
        # Ayarlar sekmesi
        self.config_tab = self.tabview.add("⚙️ Ayarlar")
        self.create_config_tab()
    
    def create_dashboard_tab(self):
        """Dashboard sekmesini oluşturur"""
        
        # İstatistik kartları
        stats_frame = ctk.CTkFrame(self.dashboard_tab)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="Sistem İstatistikleri",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # İstatistik grid
        self.stats_grid = ctk.CTkFrame(stats_frame)
        self.stats_grid.pack(fill="x", padx=10, pady=5)
        
        # İstatistik labelları
        self.total_prescriptions_label = ctk.CTkLabel(
            self.stats_grid,
            text="Toplam Reçete: 0",
            font=ctk.CTkFont(size=14)
        )
        self.total_prescriptions_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.pending_prescriptions_label = ctk.CTkLabel(
            self.stats_grid,
            text="Bekleyen: 0",
            font=ctk.CTkFont(size=14)
        )
        self.pending_prescriptions_label.grid(row=0, column=1, padx=10, pady=5)
        
        self.approved_prescriptions_label = ctk.CTkLabel(
            self.stats_grid,
            text="Onaylanan: 0",
            font=ctk.CTkFont(size=14)
        )
        self.approved_prescriptions_label.grid(row=0, column=2, padx=10, pady=5)
        
        # Son işlemler
        recent_frame = ctk.CTkFrame(self.dashboard_tab)
        recent_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            recent_frame,
            text="Son İşlemler",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Son işlemler text area
        self.recent_text = ctk.CTkTextbox(
            recent_frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.recent_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_prescriptions_tab(self):
        """Reçeteler sekmesini oluşturur"""
        
        # Filtreler
        filter_frame = ctk.CTkFrame(self.prescriptions_tab)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(filter_frame, text="Filtreler:").pack(side="left", padx=5)
        
        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Tümü", "Bekleyen", "Onaylanan", "Reddedilen"],
            command=self.filter_prescriptions
        )
        self.status_filter.pack(side="left", padx=5)
        
        # Reçete listesi (basit text area - gelecekte TreeView olabilir)
        self.prescriptions_text = ctk.CTkTextbox(
            self.prescriptions_tab,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.prescriptions_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_logs_tab(self):
        """Loglar sekmesini oluşturur"""
        
        # Log kontrolleri
        log_controls = ctk.CTkFrame(self.logs_tab)
        log_controls.pack(fill="x", padx=10, pady=5)
        
        self.clear_logs_btn = ctk.CTkButton(
            log_controls,
            text="🗑️ Temizle",
            command=self.clear_logs,
            width=100
        )
        self.clear_logs_btn.pack(side="left", padx=5)
        
        self.refresh_logs_btn = ctk.CTkButton(
            log_controls,
            text="🔄 Yenile",
            command=self.refresh_logs,
            width=100
        )
        self.refresh_logs_btn.pack(side="left", padx=5)
        
        # Log area
        self.logs_text = ctk.CTkTextbox(
            self.logs_tab,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_config_tab(self):
        """Ayarlar sekmesini oluşturur"""
        
        # Ayarlar formu
        config_frame = ctk.CTkScrollableFrame(self.config_tab)
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Medula ayarları
        medula_frame = ctk.CTkFrame(config_frame)
        medula_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            medula_frame,
            text="Medula Ayarları",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # URL
        ctk.CTkLabel(medula_frame, text="URL:").pack(anchor="w", padx=10)
        self.url_entry = ctk.CTkEntry(medula_frame, width=400)
        self.url_entry.insert(0, self.settings.medula_url)
        self.url_entry.pack(fill="x", padx=10, pady=2)
        
        # Kullanıcı adı
        ctk.CTkLabel(medula_frame, text="Kullanıcı Adı:").pack(anchor="w", padx=10)
        self.username_entry = ctk.CTkEntry(medula_frame, width=400)
        self.username_entry.insert(0, self.settings.medula_username)
        self.username_entry.pack(fill="x", padx=10, pady=2)
        
        # Claude AI ayarları
        claude_frame = ctk.CTkFrame(config_frame)
        claude_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            claude_frame,
            text="Claude AI Ayarları",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # AI Provider
        ctk.CTkLabel(claude_frame, text="AI Provider:").pack(anchor="w", padx=10)
        self.provider_combo = ctk.CTkComboBox(
            claude_frame,
            values=["claude", "openai"]
        )
        self.provider_combo.set(self.settings.ai_provider)
        self.provider_combo.pack(fill="x", padx=10, pady=2)
        
        # Model
        ctk.CTkLabel(claude_frame, text="Model:").pack(anchor="w", padx=10)
        self.model_combo = ctk.CTkComboBox(
            claude_frame,
            values=["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "gpt-4"]
        )
        self.model_combo.set(self.settings.ai_model)
        self.model_combo.pack(fill="x", padx=10, pady=2)
        
        # Auto Approve Threshold
        ctk.CTkLabel(claude_frame, text="Auto Approve Threshold:").pack(anchor="w", padx=10)
        self.threshold_slider = ctk.CTkSlider(
            claude_frame,
            from_=0.5,
            to=1.0,
            number_of_steps=10
        )
        self.threshold_slider.set(self.settings.auto_approve_threshold)
        self.threshold_slider.pack(fill="x", padx=10, pady=2)
        
        # Kaydet butonu
        self.save_config_btn = ctk.CTkButton(
            config_frame,
            text="💾 Ayarları Kaydet",
            command=self.save_config
        )
        self.save_config_btn.pack(pady=20)
    
    # Event handlers
    def toggle_automation(self):
        """Otomasyonu başlat/durdur"""
        if not self.automation_running:
            self.start_automation()
        else:
            self.stop_automation()
    
    def start_automation(self):
        """Otomasyonu başlat"""
        # Önceki thread'i kontrol et
        if self.automation_thread and self.automation_thread.is_alive():
            self.log_message("⚠️ Otomasyon zaten çalışıyor")
            return
            
        self.automation_running = True
        self.start_stop_btn.configure(text="⏹️ Durdur")
        self.status_label.configure(text="▶️ Çalışıyor")
        
        # Thread'de çalıştır
        self.automation_thread = threading.Thread(target=self.automation_worker, daemon=True)
        self.automation_thread.start()
        
        self.log_message("Otomasyon başlatıldı")
    
    def stop_automation(self):
        """Otomasyonu durdur"""
        self.automation_running = False
        self.start_stop_btn.configure(text="▶️ Başlat")
        self.status_label.configure(text="⏹️ Durduruldu")
        
        # Browser'ı kapat
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
            self.browser = None
        
        # AI engine'i temizle
        if self.ai_engine:
            self.ai_engine = None
            
        # Thread'i temizle
        if self.automation_thread:
            self.automation_thread = None
        
        self.log_message("Otomasyon durduruldu")
    
    def automation_worker(self):
        """Otomasyon iş thread'i"""
        try:
            # Browser'ı başlat
            self.browser = MedulaBrowser(self.settings)
            self.ai_engine = DecisionEngine(self.settings)
            
            if not self.browser.start():
                self.log_message("❌ Browser başlatılamadı")
                self.automation_running = False
                return
            
            # Giriş yap
            if not self.browser.login():
                self.log_message("❌ Medula'ya giriş yapılamadı")
                self.automation_running = False
                return
            
            self.log_message("✅ Medula'ya başarıyla giriş yapıldı")
            
            # Ana döngü
            while self.automation_running:
                try:
                    # Bekleyen reçeteleri getir
                    prescriptions = self.browser.get_pending_prescriptions()
                    
                    if prescriptions:
                        self.log_message(f"📋 {len(prescriptions)} adet bekleyen reçete bulundu")
                        
                        for prescription in prescriptions:
                            if not self.automation_running:
                                break
                                
                            # AI ile analiz et
                            decision = self.ai_engine.analyze_prescription(prescription)
                            
                            # Kararı uygula
                            self.browser.apply_decision(prescription, decision)
                            
                            # Veritabanına kaydet
                            self.save_prescription_to_db(prescription, decision)
                            
                            self.log_message(f"✅ Reçete işlendi: {prescription['id']} -> {decision['action']}")
                    
                    else:
                        self.log_message("📋 Bekleyen reçete bulunamadı")
                    
                    # Biraz bekle
                    import time
                    time.sleep(self.settings.check_interval)
                    
                except Exception as e:
                    self.log_message(f"❌ İşlem hatası: {e}")
                    break
                    
        except Exception as e:
            self.log_message(f"❌ Otomasyon hatası: {e}")
        finally:
            self.stop_automation()
    
    def run_tests(self):
        """Test işlemlerini çalıştır"""
        def test_worker():
            self.log_message("🧪 Testler başlatılıyor...")
            
            # Browser testi
            try:
                from test_automation import SeleniumTester
                tester = SeleniumTester()
                
                if tester.setup_browser(headless=self.settings.headless):
                    self.log_message("✅ Browser testi başarılı")
                    tester.close_browser()
                else:
                    self.log_message("❌ Browser testi başarısız")
                    
            except Exception as e:
                self.log_message(f"❌ Browser test hatası: {e}")
        
        # Thread'de çalıştır
        threading.Thread(target=test_worker, daemon=True).start()
    
    def test_database(self):
        """Veritabanı testini çalıştır"""
        def db_test_worker():
            try:
                from database.test_db import run_all_tests
                self.log_message("💾 Veritabanı testleri başlatılıyor...")
                results = run_all_tests()
                
                passed = sum(results.values())
                total = len(results)
                
                if passed == total:
                    self.log_message(f"✅ Tüm veritabanı testleri başarılı ({passed}/{total})")
                else:
                    self.log_message(f"⚠️ Bazı testler başarısız ({passed}/{total})")
                    
            except Exception as e:
                self.log_message(f"❌ Veritabanı test hatası: {e}")
        
        # Thread'de çalıştır
        threading.Thread(target=db_test_worker, daemon=True).start()
    
    def show_statistics(self):
        """İstatistikleri göster"""
        try:
            stats = self.db_manager.get_statistics()
            self.update_statistics_display(stats)
            self.log_message("📊 İstatistikler güncellendi")
        except Exception as e:
            self.log_message(f"❌ İstatistik hatası: {e}")
    
    def show_settings(self):
        """Ayarları göster"""
        settings_info = f"""
🔧 Mevcut Ayarlar:
- Medula URL: {self.settings.medula_url}
- Browser: {self.settings.browser_type}
- Headless: {self.settings.headless}
- AI Provider: {self.settings.ai_provider}
- AI Model: {self.settings.ai_model}
- Kontrol Aralığı: {self.settings.check_interval}s
- Auto Approve Threshold: {self.settings.auto_approve_threshold}
        """
        self.log_message(settings_info)
    
    def toggle_headless(self):
        """Headless mode'u değiştir"""
        self.settings.headless = self.headless_var.get()
        self.log_message(f"Headless mode: {self.settings.headless}")
    
    def filter_prescriptions(self, choice):
        """Reçeteleri filtrele"""
        self.log_message(f"Reçete filtresi: {choice}")
        # TODO: Reçete listesini filtrele
    
    def clear_logs(self):
        """Logları temizle"""
        self.logs_text.delete("0.0", "end")
        self.recent_text.delete("0.0", "end")
    
    def refresh_logs(self):
        """Logları yenile"""
        # TODO: Log dosyasından logları oku
        self.log_message("🔄 Loglar yenilendi")
    
    def save_config(self):
        """Ayarları kaydet"""
        # TODO: Ayarları .env dosyasına kaydet
        self.log_message("💾 Ayarlar kaydedildi")
        messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
    
    def save_prescription_to_db(self, prescription, decision):
        """Reçeteyi veritabanına kaydet"""
        try:
            # Reçeteyi kaydet
            self.db_manager.add_prescription(
                prescription_id=prescription['id'],
                patient_tc=prescription.get('patient_tc', ''),
                doctor_diploma_no=prescription.get('doctor_id', ''),
                hospital=prescription.get('hospital', ''),
                prescription_date=prescription.get('prescription_date', ''),
                total_amount=prescription.get('total_amount', 0)
            )
            
            # AI kararını kaydet
            self.db_manager.save_ai_decision(
                prescription_id=prescription['id'],
                decision=decision['action'],
                reason=decision['reason'],
                confidence=decision['confidence'],
                risk_factors=decision.get('risk_factors', []),
                recommendations=decision.get('recommendations', [])
            )
            
        except Exception as e:
            self.log_message(f"❌ Veritabanı kayıt hatası: {e}")
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            stats = self.db_manager.get_statistics()
            self.update_statistics_display(stats)
        except Exception as e:
            self.log_message(f"❌ İstatistik güncelleme hatası: {e}")
    
    def update_statistics_display(self, stats):
        """İstatistik görüntüsünü güncelle"""
        total = stats.get('total_prescriptions', 0)
        status_stats = stats.get('prescriptions_by_status', {})
        
        self.total_prescriptions_label.configure(text=f"Toplam Reçete: {total}")
        self.pending_prescriptions_label.configure(text=f"Bekleyen: {status_stats.get('pending', 0)}")
        self.approved_prescriptions_label.configure(text=f"Onaylanan: {status_stats.get('approved', 0)}")
    
    def log_message(self, message):
        """Log mesajı ekle"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Logs tab'ına ekle
        self.logs_text.insert("end", formatted_message)
        self.logs_text.see("end")
        
        # Recent tab'ına ekle (sadece son 10 mesaj)
        self.recent_text.insert("end", formatted_message)
        
        # Recent text'i sınırla
        lines = self.recent_text.get("1.0", "end").split("\n")
        if len(lines) > 15:
            self.recent_text.delete("1.0", "6.0")
        
        self.recent_text.see("end")
    
    def run(self):
        """GUI'yi başlat"""
        try:
            self.log_message("🚀 Eczane Reçete Kontrol Otomasyonu başlatıldı")
            self.log_message(f"📁 Çalışma dizini: {Path.cwd()}")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("⚠️ Program kullanıcı tarafından durduruldu")
        finally:
            if self.browser:
                self.browser.quit()


def main():
    """Ana fonksiyon"""
    app = EczaneOtomasyonGUI()
    app.run()


if __name__ == "__main__":
    main()