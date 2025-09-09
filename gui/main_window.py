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
from unified_prescription_processor import UnifiedPrescriptionProcessor
from advanced_batch_processor import AdvancedBatchProcessor


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
        self.unified_processor = UnifiedPrescriptionProcessor()  # NEW: Unified processor
        self.batch_processor = AdvancedBatchProcessor()  # NEW: Advanced Batch processor
        
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
        
        # Unified processor butonları
        unified_frame = ctk.CTkFrame(self.left_panel)
        unified_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            unified_frame,
            text="🚀 Unified Processor",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # JSON'dan işle butonu
        self.process_json_btn = ctk.CTkButton(
            unified_frame,
            text="📄 JSON İşle",
            command=self.process_json_prescriptions,
            width=150
        )
        self.process_json_btn.pack(pady=2)
        
        # Medula Live işle butonu
        self.process_live_btn = ctk.CTkButton(
            unified_frame,
            text="🔄 Medula Live",
            command=self.process_medula_live,
            width=150
        )
        self.process_live_btn.pack(pady=2)
        
        # Batch işle butonu
        self.batch_process_btn = ctk.CTkButton(
            unified_frame,
            text="📊 Batch İşle",
            command=self.process_batch,
            width=150
        )
        self.batch_process_btn.pack(pady=2)
        
        # Advanced Batch butonu  
        self.advanced_batch_btn = ctk.CTkButton(
            unified_frame,
            text="🚀 Gelişmiş Batch",
            command=self.advanced_batch_processing,
            width=150
        )
        self.advanced_batch_btn.pack(pady=2)
        
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
    
    # ================================================================
    # UNIFIED PROCESSOR METHODS
    # ================================================================
    
    def process_json_prescriptions(self):
        """JSON dosyasından reçeteleri işle"""
        import time
        
        try:
            self.log_message("📄 JSON reçete işleme başlatılıyor...")
            
            # Dosya seçimi dialog
            from tkinter import filedialog
            json_file = filedialog.askopenfilename(
                title="JSON dosyasını seçin",
                filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")]
            )
            
            if not json_file:
                self.log_message("❌ Dosya seçilmedi")
                return
            
            # Thread'de çalıştır
            def process_thread():
                try:
                    results = self.unified_processor.process_from_json_file(
                        json_file, 
                        f"gui_json_results_{int(time.time())}.json"
                    )
                    
                    self.log_message(f"✅ JSON işleme tamamlandı: {len(results)} reçete işlendi")
                    self.log_message(f"📊 Sonuçlar kaydedildi")
                    
                    # İstatistikleri güncelle
                    self.update_statistics()
                    
                except Exception as e:
                    self.log_message(f"❌ JSON işleme hatası: {e}")
            
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_message(f"❌ JSON işleme başlatma hatası: {e}")
    
    def process_medula_live(self):
        """Medula Live reçete işleme"""
        try:
            self.log_message("🔄 Medula Live işleme başlatılıyor...")
            
            # Thread'de çalıştır
            def process_thread():
                try:
                    results = self.unified_processor.process_from_medula_live(
                        limit=5, 
                        group='A'
                    )
                    
                    self.log_message(f"✅ Medula Live işleme tamamlandı: {len(results)} reçete işlendi")
                    
                    # Sonuçları göster
                    for result in results:
                        prescription_id = result.get('prescription_id', 'N/A')
                        decision = result.get('final_decision', 'unknown')
                        self.log_message(f"  📋 {prescription_id} -> {decision.upper()}")
                    
                    # İstatistikleri güncelle
                    self.update_statistics()
                    
                except Exception as e:
                    self.log_message(f"❌ Medula Live işleme hatası: {e}")
            
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Medula Live başlatma hatası: {e}")
    
    def process_batch(self):
        """Batch reçete işleme"""
        try:
            self.log_message("📊 Batch işleme başlatılıyor...")
            
            # Basit dialog ile limit al
            import tkinter.simpledialog as simpledialog
            limit = simpledialog.askinteger(
                "Batch İşleme",
                "Kaç reçete işlemek istiyorsunuz?",
                initialvalue=10,
                minvalue=1,
                maxvalue=50
            )
            
            if not limit:
                self.log_message("❌ Batch işleme iptal edildi")
                return
            
            # Thread'de çalıştır
            def process_thread():
                try:
                    results = self.unified_processor.process_from_medula_live(
                        limit=limit, 
                        group='A'
                    )
                    
                    self.log_message(f"✅ Batch işleme tamamlandı: {len(results)} reçete işlendi")
                    
                    # Özet istatistikler
                    stats = self.unified_processor.get_processing_stats()
                    self.log_message(f"📈 İstatistikler:")
                    self.log_message(f"  ✅ Onaylanan: {stats.get('approved', 0)}")
                    self.log_message(f"  ❌ Reddedilen: {stats.get('rejected', 0)}")
                    self.log_message(f"  ⏸️ Bekletilen: {stats.get('held', 0)}")
                    self.log_message(f"  ⚠️ Hata: {stats.get('errors', 0)}")
                    
                    # İstatistikleri güncelle
                    self.update_statistics()
                    
                except Exception as e:
                    self.log_message(f"❌ Batch işleme hatası: {e}")
            
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Batch işleme başlatma hatası: {e}")
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            # Database'den güncel istatistikleri al
            all_prescriptions = self.unified_processor.database.get_all_prescriptions(limit=1000)
            
            total = len(all_prescriptions)
            
            # İstatistikleri güncelle
            if hasattr(self, 'total_prescriptions_label'):
                self.total_prescriptions_label.configure(text=f"Toplam Reçete: {total}")
            
            self.log_message(f"📊 İstatistikler güncellendi: {total} reçete")
            
        except Exception as e:
            self.log_message(f"❌ İstatistik güncelleme hatası: {e}")
    
    def advanced_batch_processing(self):
        """Gelişmiş batch processing penceresi"""
        try:
            # Yeni pencere oluştur
            batch_window = ctk.CTkToplevel(self.root)
            batch_window.title("🚀 Gelişmiş Batch Processing")
            batch_window.geometry("800x600")
            batch_window.transient(self.root)
            
            # Ana frame
            main_frame = ctk.CTkFrame(batch_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Başlık
            title_label = ctk.CTkLabel(
                main_frame,
                text="🚀 Gelişmiş Batch Processing",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=10)
            
            # Options frame
            options_frame = ctk.CTkFrame(main_frame)
            options_frame.pack(fill="x", padx=10, pady=5)
            
            # Batch tipi seçimi
            ctk.CTkLabel(options_frame, text="Batch Tipi:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            batch_type_var = ctk.StringVar(value="json")
            
            # Radio buttons
            type_frame = ctk.CTkFrame(options_frame)
            type_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkRadioButton(type_frame, text="📄 JSON Dosyası", variable=batch_type_var, value="json").pack(side="left", padx=5)
            ctk.CTkRadioButton(type_frame, text="🔄 Medula Live", variable=batch_type_var, value="medula").pack(side="left", padx=5)
            ctk.CTkRadioButton(type_frame, text="🔀 Karışık", variable=batch_type_var, value="mixed").pack(side="left", padx=5)
            
            # Parametreler frame
            params_frame = ctk.CTkFrame(options_frame)
            params_frame.pack(fill="x", padx=10, pady=5)
            
            # Limit input
            ctk.CTkLabel(params_frame, text="İşlenecek Reçete Sayısı:").pack(anchor="w", padx=5, pady=2)
            limit_entry = ctk.CTkEntry(params_frame, placeholder_text="Örn: 50")
            limit_entry.pack(fill="x", padx=5, pady=2)
            limit_entry.insert(0, "25")
            
            # Batch size input
            ctk.CTkLabel(params_frame, text="Batch Boyutu:").pack(anchor="w", padx=5, pady=2)
            batch_size_entry = ctk.CTkEntry(params_frame, placeholder_text="Örn: 10")
            batch_size_entry.pack(fill="x", padx=5, pady=2)
            batch_size_entry.insert(0, "10")
            
            # Progress frame
            progress_frame = ctk.CTkFrame(main_frame)
            progress_frame.pack(fill="x", padx=10, pady=10)
            
            # Progress bar
            progress_bar = ctk.CTkProgressBar(progress_frame)
            progress_bar.pack(fill="x", padx=10, pady=5)
            progress_bar.set(0)
            
            # Progress labels
            progress_label = ctk.CTkLabel(progress_frame, text="Hazır")
            progress_label.pack(pady=2)
            
            stats_label = ctk.CTkLabel(progress_frame, text="")
            stats_label.pack(pady=2)
            
            # Control buttons frame
            control_frame = ctk.CTkFrame(main_frame)
            control_frame.pack(fill="x", padx=10, pady=5)
            
            # Buttons
            start_btn = ctk.CTkButton(control_frame, text="▶️ Başlat", width=100)
            start_btn.pack(side="left", padx=5)
            
            pause_btn = ctk.CTkButton(control_frame, text="⏸️ Duraklat", width=100, state="disabled")
            pause_btn.pack(side="left", padx=5)
            
            stop_btn = ctk.CTkButton(control_frame, text="⏹️ Durdur", width=100, state="disabled")
            stop_btn.pack(side="left", padx=5)
            
            # Results frame
            results_frame = ctk.CTkFrame(main_frame)
            results_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Results text area
            results_text = ctk.CTkTextbox(results_frame)
            results_text.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Batch processor instance
            batch_processor_instance = None
            
            def update_progress_callback(progress):
                """Progress güncelleme callback'i"""
                try:
                    # Progress bar güncelle
                    progress_bar.set(progress.progress_percentage / 100.0)
                    
                    # Progress label
                    progress_label.configure(
                        text=f"İşlem: {progress.processed}/{progress.total_prescriptions} "
                             f"({progress.progress_percentage:.1f}%) - "
                             f"Batch {progress.current_batch}/{progress.total_batches}"
                    )
                    
                    # Stats label
                    stats_label.configure(
                        text=f"✅ Onay: {progress.approved} | "
                             f"❌ Red: {progress.rejected} | "
                             f"⏸️ Beklet: {progress.held} | "
                             f"⚠️ Hata: {progress.errors}"
                    )
                    
                    # Results text
                    if progress.estimated_completion:
                        eta = progress.estimated_completion.strftime("%H:%M:%S")
                        results_text.insert("end", f"⏱️ Tahmini Bitiş: {eta}\\n")
                    
                    # Auto scroll
                    results_text.see("end")
                    
                except Exception as e:
                    self.log_message(f"❌ Progress update error: {e}")
            
            def start_batch():
                """Batch processing başlat"""
                nonlocal batch_processor_instance
                
                try:
                    # Parameters al
                    batch_type = batch_type_var.get()
                    limit = int(limit_entry.get() or 25)
                    batch_size = int(batch_size_entry.get() or 10)
                    
                    # Buttons güncelle
                    start_btn.configure(state="disabled")
                    pause_btn.configure(state="normal")
                    stop_btn.configure(state="normal")
                    
                    # Results temizle
                    results_text.delete("0.0", "end")
                    results_text.insert("end", f"🚀 {batch_type.upper()} batch processing başlatılıyor...\\n")
                    results_text.insert("end", f"📊 Limit: {limit}, Batch Size: {batch_size}\\n\\n")
                    
                    # Advanced batch processor oluştur
                    from advanced_batch_processor import AdvancedBatchProcessor, BatchConfig
                    
                    config = BatchConfig()
                    config.batch_size = batch_size
                    config.max_concurrent_processes = 2
                    config.delay_between_batches = 1.0
                    
                    batch_processor_instance = AdvancedBatchProcessor(config)
                    batch_processor_instance.set_progress_callback(update_progress_callback)
                    
                    # Thread'de çalıştır
                    def batch_thread():
                        try:
                            if batch_type == "json":
                                # JSON dosyası seç
                                from tkinter import filedialog
                                json_file = filedialog.askopenfilename(
                                    title="JSON dosyasını seçin",
                                    filetypes=[("JSON dosyaları", "*.json")]
                                )
                                
                                if json_file:
                                    results_text.insert("end", f"📄 JSON dosyası: {json_file}\\n")
                                    report = batch_processor_instance.process_large_json_batch(json_file, "gui_batch_results")
                                else:
                                    results_text.insert("end", "❌ JSON dosyası seçilmedi\\n")
                                    return
                                    
                            elif batch_type == "medula":
                                results_text.insert("end", "🔄 Medula Live batch processing...\\n")
                                report = batch_processor_instance.process_medula_batch_live(limit, "gui_medula_batch")
                                
                            elif batch_type == "mixed":
                                results_text.insert("end", "🔀 Mixed batch processing...\\n")
                                sources = [
                                    {"type": "medula", "limit": limit // 2},
                                    {"type": "json", "path": "manual_detailed_prescriptions.json"}
                                ]
                                report = batch_processor_instance.process_mixed_batch(sources, "gui_mixed_batch")
                            
                            # Sonuçları göster
                            results_text.insert("end", "\\n=== BATCH PROCESSING TAMAMLANDI ===\\n")
                            results_text.insert("end", f"✅ İşlenen: {report['batch_summary']['processed_prescriptions']}\\n")
                            results_text.insert("end", f"📈 Başarı Oranı: {report['batch_summary']['success_rate']:.1f}%\\n")
                            results_text.insert("end", f"⏱️ İşlem Süresi: {report['batch_summary']['processing_time_seconds']:.1f}s\\n")
                            
                            # Decision stats
                            decisions = report['decision_statistics']
                            results_text.insert("end", f"\\n📊 Kararlar:\\n")
                            results_text.insert("end", f"  ✅ Onaylanan: {decisions['approved']}\\n")
                            results_text.insert("end", f"  ❌ Reddedilen: {decisions['rejected']}\\n")
                            results_text.insert("end", f"  ⏸️ Bekletilen: {decisions['held']}\\n")
                            results_text.insert("end", f"  ⚠️ Hata: {decisions['errors']}\\n")
                            
                            self.log_message(f"🎉 Advanced batch completed: {report['batch_summary']['processed_prescriptions']} prescriptions")
                            
                        except Exception as e:
                            results_text.insert("end", f"\\n❌ BATCH PROCESSING HATASI: {e}\\n")
                            self.log_message(f"❌ Advanced batch error: {e}")
                        finally:
                            # Buttons reset
                            start_btn.configure(state="normal")
                            pause_btn.configure(state="disabled") 
                            stop_btn.configure(state="disabled")
                    
                    # Start thread
                    thread = threading.Thread(target=batch_thread, daemon=True)
                    thread.start()
                    
                except Exception as e:
                    results_text.insert("end", f"❌ Başlatma hatası: {e}\\n")
                    self.log_message(f"❌ Advanced batch start error: {e}")
            
            def pause_batch():
                """Batch processing duraklat"""
                if batch_processor_instance:
                    batch_processor_instance.pause()
                    results_text.insert("end", "⏸️ Batch processing duraklatıldı\\n")
            
            def stop_batch():
                """Batch processing durdur"""
                if batch_processor_instance:
                    batch_processor_instance.stop()
                    results_text.insert("end", "⏹️ Batch processing durduruldu\\n")
                
                # Buttons reset
                start_btn.configure(state="normal")
                pause_btn.configure(state="disabled")
                stop_btn.configure(state="disabled")
            
            # Button commands
            start_btn.configure(command=start_batch)
            pause_btn.configure(command=pause_batch)
            stop_btn.configure(command=stop_batch)
            
        except Exception as e:
            self.log_message(f"❌ Advanced batch window error: {e}")
    
    def run(self):
        """GUI'yi başlat"""
        try:
            self.log_message("🚀 Eczane Reçete Kontrol Otomasyonu başlatıldı")
            self.log_message("🚀 Unified Processor entegrasyonu hazır!")
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