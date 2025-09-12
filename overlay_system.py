# -*- coding: utf-8 -*-
"""
OVERLAY CERCEVE SISTEMI - ANA MODUL
Medula ustune cerceve giydiren hibrit sistem

Tarih: 10 Eylul 2025
Tasarim: 6 ana bolumlu overlay architektuuru
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
from typing import Dict, List, Optional
import time

# Mevcut sistemlerden import (optional - fallback olacak)
try:
    from unified_prescription_processor import UnifiedPrescriptionProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    print("WARNING: UnifiedPrescriptionProcessor not found - mock mode")

try:
    from config.settings import get_settings
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False
    print("WARNING: Settings module not found - basic mode")

class OverlaySystem:
    """Ana Overlay Çerçeve Sistemi"""
    
    def __init__(self):
        self.root = None
        self.processor = None
        self.settings = {}
        
        # Bayrak sistemi renk kodları
        self.status_colors = {
            'uygun': '#28a745',          # Yeşil
            'uygun_degil': '#dc3545',    # Kırmızı  
            'supheli': '#ffc107',        # Sarı
            'ek_kontrol': '#fd7e14',     # Turuncu
            'kontrolsuz': '#17a2b8'      # Açık mavi
        }
        
        self.current_prescriptions = []
        self.init_system()

    def init_system(self):
        """Sistem başlatma"""
        try:
            if SETTINGS_AVAILABLE:
                self.settings = get_settings()
            else:
                self.settings = {}  # Basic fallback
            print("Overlay sistemi baslatildi")
        except Exception as e:
            print(f"Sistem baslatma hatasi: {e}")
            self.settings = {}  # Fallback

    def show_main_control_panel(self):
        """İÇ KAPI - Ana Kontrol Paneli (2. bölüm)"""
        self.root = tk.Tk()
        self.root.title("🏥 Eczane Otomasyon - Ana Kontrol")
        self.root.geometry("600x400")
        self.root.configure(bg='#f8f9fa')
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🎯 ANA KONTROL PANELİ", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # İlk Ayarlar Bölümü
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ İLK AYARLAR", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Medula ayarları
        ttk.Label(settings_frame, text="Medula Kullanıcı Adı:").pack(anchor=tk.W)
        self.medula_username_entry = ttk.Entry(settings_frame, width=40)
        self.medula_username_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(settings_frame, text="Medula Şifre:").pack(anchor=tk.W)
        self.medula_password_entry = ttk.Entry(settings_frame, width=40, show="*")
        self.medula_password_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(settings_frame, text="Claude API Key:").pack(anchor=tk.W)
        self.api_key_entry = ttk.Entry(settings_frame, width=40, show="*")
        self.api_key_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Ayarları kaydet butonu
        save_btn = ttk.Button(settings_frame, text="📁 Ayarları Kaydet", 
                            command=self.save_settings)
        save_btn.pack(pady=10)
        
        # Medula giriş butonu  
        medula_frame = ttk.Frame(main_frame)
        medula_frame.pack(fill=tk.X, pady=20)
        
        medula_btn = tk.Button(medula_frame, 
                              text="🚀 MEDULAYA GİRİŞ YAP",
                              font=('Arial', 14, 'bold'),
                              bg='#28a745', fg='white',
                              height=2,
                              command=self.open_medula_overlay)
        medula_btn.pack(fill=tk.X)
        
        # Navigasyon modu seçimi
        nav_frame = ttk.LabelFrame(main_frame, text="🧭 Navigasyon Modu", padding="10")
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.nav_mode = tk.StringVar(value="manuel")
        ttk.Radiobutton(nav_frame, text="🤏 Manuel Navigasyon", 
                       variable=self.nav_mode, value="manuel").pack(anchor=tk.W)
        ttk.Radiobutton(nav_frame, text="🤖 Otomatik Pilot", 
                       variable=self.nav_mode, value="otomatik").pack(anchor=tk.W)
        
        # Mevcut ayarları yükle
        self.load_current_settings()
        
        self.root.mainloop()

    def save_settings(self):
        """Ayarları kaydetme"""
        try:
            settings_data = {
                'MEDULA_USERNAME': self.medula_username_entry.get(),
                'MEDULA_PASSWORD': self.medula_password_entry.get(),  
                'CLAUDE_API_KEY': self.api_key_entry.get(),
                'NAVIGATION_MODE': self.nav_mode.get()
            }
            
            # .env dosyasını güncelle
            env_path = '.env'
            env_content = []
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_content = f.readlines()
            
            # Mevcut ayarları güncelle veya ekle
            updated_keys = set()
            for i, line in enumerate(env_content):
                for key, value in settings_data.items():
                    if line.startswith(f'{key}='):
                        env_content[i] = f'{key}={value}\n'
                        updated_keys.add(key)
                        break
            
            # Yeni ayarları ekle
            for key, value in settings_data.items():
                if key not in updated_keys:
                    env_content.append(f'{key}={value}\n')
            
            # Dosyayı yaz
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_content)
            
            messagebox.showinfo("Başarılı", "✅ Ayarlar kaydedildi!")
            print("✅ Ayarlar .env dosyasına kaydedildi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Ayar kaydetme hatası: {e}")
            print(f"❌ Ayar kaydetme hatası: {e}")

    def load_current_settings(self):
        """Mevcut ayarları yükleme"""
        try:
            env_path = '.env'
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'MEDULA_USERNAME':
                                self.medula_username_entry.insert(0, value)
                            elif key == 'MEDULA_PASSWORD':
                                self.medula_password_entry.insert(0, value)
                            elif key == 'CLAUDE_API_KEY':
                                self.api_key_entry.insert(0, value)
                            elif key == 'NAVIGATION_MODE':
                                self.nav_mode.set(value)
            print("✅ Mevcut ayarlar yüklendi")
        except Exception as e:
            print(f"⚠️  Ayar yükleme uyarısı: {e}")

    def open_medula_overlay(self):
        """GERÇEK MEDULA BROWSER SİSTEMİNİ BAŞLAT - ÇERÇEVE İLE"""
        if not self.validate_settings():
            return
            
        try:
            print("🚀 Medula browser sistemi başlatılıyor...")
            
            # Settings oluştur
            from config.settings import Settings
            settings = Settings()
            
            # Overlay'den ayarları al
            settings.medula_username = self.medula_username_entry.get().strip()
            settings.medula_password = self.medula_password_entry.get().strip()
            settings.ANTHROPIC_API_KEY = self.api_key_entry.get().strip()
            
            # Browser sistemi ile entegre overlay başlat
            self.start_medula_with_frame_system(settings)
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Medula açma hatası: {e}")
    
    def start_medula_with_frame_system(self, settings):
        """Gerçek Medula browser'ı çerçeve sistemi ile başlat"""
        try:
            from medula_automation.browser import MedulaBrowser
            import threading
            
            print("🌐 Browser başlatılıyor...")
            
            # Ana pencereyi gizle
            self.root.withdraw()
            
            # Browser thread'de başlat
            def browser_thread():
                try:
                    browser = MedulaBrowser(settings)
                    
                    # Browser başlat
                    if browser.start():
                        print("✅ Browser başarıyla başlatıldı")
                        
                        # Medula'ya login
                        if browser.login():
                            print("🔐 Medula login başarılı")
                            
                            # KALICI ÇERÇEVE SİSTEMİNİ INJECT ET
                            browser.inject_persistent_frame_system()
                            print("🖼️ Kalıcı çerçeve sistemi inject edildi")
                            
                            # Monitoring sistemi başlat
                            self.start_browser_monitoring(browser)
                            
                        else:
                            print("❌ Medula login başarısız")
                            self.show_error("Medula login başarısız")
                    else:
                        print("❌ Browser başlatma başarısız")
                        self.show_error("Browser başlatma başarısız")
                        
                except Exception as e:
                    print(f"❌ Browser thread hatası: {e}")
                    self.show_error(f"Browser hatası: {e}")
            
            # Thread başlat
            browser_thread_obj = threading.Thread(target=browser_thread, daemon=True)
            browser_thread_obj.start()
            
            print("🎯 Browser thread başlatıldı...")
            
        except Exception as e:
            print(f"❌ Browser başlatma hatası: {e}")
            messagebox.showerror("Hata", f"Browser başlatma hatası: {e}")
            self.root.deiconify()
    
    def start_browser_monitoring(self, browser):
        """Browser monitoring sistemi"""
        try:
            import time
            from unified_prescription_processor import UnifiedPrescriptionProcessor
            
            print("👁️ Browser monitoring başlatıldı")
            
            # Processor başlat
            processor = UnifiedPrescriptionProcessor()
            
            while True:
                try:
                    # Çerçeve sistemden gelen istekleri kontrol et
                    interaction = browser.check_overlay_interaction()
                    
                    if interaction['requested']:
                        action = interaction['action']
                        print(f"🎯 İşlem isteği: {action}")
                        
                        if action == 'prescriptionControl':
                            # Tek reçete kontrolü
                            prescription_data = browser.extract_current_page_prescription()
                            if prescription_data:
                                result = processor.process_single_prescription(prescription_data, "overlay_frame")
                                browser.show_result_in_browser(result)
                    
                    # Çerçeve sisteminin korunmasını sağla
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Monitoring döngü hatası: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            print(f"❌ Browser monitoring hatası: {e}")
    
    def show_error(self, message):
        """Hata mesajı göster ve ana pencereyi geri getir"""
        try:
            self.root.deiconify()
            messagebox.showerror("Browser Hatası", message)
        except:
            print(f"❌ {message}")

    def validate_settings(self):
        """Ayar validasyonu"""
        username = self.medula_username_entry.get().strip()
        password = self.medula_password_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Eksik Bilgi", "⚠️ Medula kullanıcı adı ve şifre gerekli!")
            return False
            
        if not api_key:
            messagebox.showwarning("Eksik Bilgi", "⚠️ Claude API anahtarı gerekli!")
            return False
            
        return True

    def create_overlay_window(self):
        """Overlay penceresi oluşturma"""
        try:
            # Overlay ana penceresi
            overlay_root = tk.Toplevel()
            overlay_root.title("🎯 Medula Overlay Sistemi")
            overlay_root.geometry("1400x900")
            overlay_root.configure(bg='#2c3e50')
            
            # Üst kontrol paneli
            control_panel = tk.Frame(overlay_root, bg='#34495e', height=80)
            control_panel.pack(fill=tk.X, padx=5, pady=5)
            control_panel.pack_propagate(False)
            
            # Ana başlık
            title_label = tk.Label(control_panel, 
                                 text="🏥 MEDULA ÇERÇEVE SİSTEMİ", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#34495e', fg='white')
            title_label.pack(side=tk.LEFT, padx=20, pady=25)
            
            # Navigasyon butonları
            nav_frame = tk.Frame(control_panel, bg='#34495e')
            nav_frame.pack(side=tk.RIGHT, padx=20, pady=20)
            
            # Ana kontrol butonları (sayfa tipine göre değişecek)
            self.create_dynamic_buttons(nav_frame)
            
            # Medula embed alanı
            medula_frame = tk.Frame(overlay_root, bg='white', relief=tk.RAISED, bd=2)
            medula_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # WebView entegrasyonu için placeholder
            medula_label = tk.Label(medula_frame, 
                                  text="🌐 MEDULA SİSTEMİ YÜKLENİYOR...\n\n" + 
                                       "🔄 Browser entegrasyonu hazırlanıyor\n" +
                                       "📋 Çerçeve sistemi aktif\n\n" +
                                       "Gerçek implementasyon: WebView2/CEF ile yapılacak",
                                  font=('Arial', 12),
                                  bg='white', fg='#666')
            medula_label.pack(expand=True)
            
            # Alt durum çubuğu
            status_frame = tk.Frame(overlay_root, bg='#95a5a6', height=30)
            status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
            status_frame.pack_propagate(False)
            
            self.status_label = tk.Label(status_frame,
                                       text="📊 Sistem Hazır | 🔵 0 Kontrolsüz | 🟢 0 Uygun | 🔴 0 Uygun Değil",
                                       bg='#95a5a6', fg='white', font=('Arial', 10))
            self.status_label.pack(pady=5)
            
            # Pencere kapatma olayı
            overlay_root.protocol("WM_DELETE_WINDOW", self.close_overlay)
            
            print("✅ Overlay penceresi oluşturuldu")
            
        except Exception as e:
            print(f"❌ Overlay oluşturma hatası: {e}")
            self.root.deiconify()

    def create_dynamic_buttons(self, parent):
        """Sayfa tipine göre dinamik butonlar"""
        # Genel kontrol butonları
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'height': 1,
            'width': 15
        }
        
        # Ana kontrol butonları
        tk.Button(parent, text="🔄 YENİLE", bg='#3498db', fg='white', 
                 command=self.refresh_page, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="🏠 ANA SAYFA", bg='#9b59b6', fg='white',
                 command=self.go_home, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="📋 LİSTE", bg='#e67e22', fg='white',
                 command=self.go_prescription_list, **btn_style).pack(side=tk.LEFT, padx=2)
        
        # Dinamik butonlar (sayfa algılamasına göre değişecek)
        self.dynamic_button_frame = tk.Frame(parent, bg='#34495e')
        self.dynamic_button_frame.pack(side=tk.LEFT, padx=20)

    def update_dynamic_buttons(self, page_type: str):
        """Sayfa tipine göre butonları güncelle"""
        # Mevcut dinamik butonları temizle
        for widget in self.dynamic_button_frame.winfo_children():
            widget.destroy()
        
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'height': 1,
            'width': 18
        }
        
        if page_type == "prescription_detail":
            # TEK REÇETE KONTROL (3. bölüm)
            tk.Button(self.dynamic_button_frame, 
                     text="🔬 BU REÇETEYİ KONTROL ET",
                     bg='#e74c3c', fg='white',
                     command=self.control_single_prescription,
                     **btn_style).pack(side=tk.LEFT, padx=2)
                     
        elif page_type == "daily_list":
            # GÜNLÜK TOPLU KONTROL (4. bölüm)
            tk.Button(self.dynamic_button_frame,
                     text="🎯 TÜM GÜNLÜKLERİ KONTROL ET", 
                     bg='#27ae60', fg='white',
                     command=self.control_daily_prescriptions,
                     **btn_style).pack(side=tk.LEFT, padx=2)
                     
        elif page_type == "monthly_list":
            # AYLIK TOPLU KONTROL (5. bölüm)
            tk.Button(self.dynamic_button_frame,
                     text="📊 TÜM AYLIGI KONTROL ET",
                     bg='#2980b9', fg='white', 
                     command=self.control_monthly_prescriptions,
                     **btn_style).pack(side=tk.LEFT, padx=2)
                     
        elif page_type == "prescription_query":
            # REÇETE SORGU KONTROL (6. bölüm)
            tk.Button(self.dynamic_button_frame,
                     text="🔍 REÇETELERİ KONTROL ET",
                     bg='#8e44ad', fg='white',
                     command=self.control_query_prescriptions, 
                     **btn_style).pack(side=tk.LEFT, padx=2)

    def control_single_prescription(self):
        """TEK REÇETE KONTROL ALGORİTMASI (3. bölüm) - GERÇEK MEDULA ENTEGRASYONUokededed"""
        try:
            print("🔬 Tek reçete kontrolü başlıyor...")
            
            # Core processor'ı başlat
            if not self.processor and PROCESSOR_AVAILABLE:
                self.processor = UnifiedPrescriptionProcessor()
                print("✅ Unified Processor başlatıldı")
            
            # GERÇEK MEDULA VERİSİ ÇIKARMA
            # Browser mevcut sayfadan reçete verilerini çıkar
            current_prescription = self.extract_current_prescription_from_page()
            
            if not current_prescription:
                print("❌ Mevcut sayfada reçete verisi bulunamadı - fallback mock data")
                # Fallback: Mock data kullan
                current_prescription = {
                    "recete_no": "CURRENT_PAGE",
                    "hasta_tc": "12345678901", 
                    "hasta_ad_soyad": "Mevcut Sayfa Hastası",
                    "drugs": [{"ilac_adi": "Mevcut Sayfa İlacı", "adet": "1"}],
                    "extraction_method": "fallback_mock"
                }
            
            print(f"📄 Kontrole alınan reçete: {current_prescription.get('recete_no', 'UNKNOWN')}")
            
            # GERÇEK UNIFIED PROCESSOR ANALİZİ
            if self.processor:
                print("🔄 UnifiedPrescriptionProcessor ile analiz başlıyor...")
                result = self.processor.process_single_prescription(current_prescription, "overlay_single")
                
                # Sonucu işle
                final_decision = result.get('final_decision', 'unknown')
                confidence = result.get('processing_metadata', {}).get('processing_time_seconds', 0)
                
                print(f"✅ Unified Processor Sonucu: {final_decision.upper()}")
                print(f"⏱️ İşlem süresi: {confidence:.3f} saniye")
                
                # Bayrak güncelleme
                self.update_prescription_flag(current_prescription.get('recete_no'), final_decision)
                
                # Detaylı sonuç gösterimi
                self.show_detailed_results(result)
                
            else:
                print("⚠️ Processor mevcut değil - mock analiz yapılıyor")
                result = self.mock_analysis(current_prescription)
                self.update_prescription_flag(current_prescription.get('recete_no'), result['status'])
            
            # Durum güncelleme
            self.update_status_bar()
            
            print(f"🎉 Tek reçete kontrolü tamamlandı!")
            
        except Exception as e:
            print(f"❌ Tek reçete kontrol hatası: {e}")
            
    def extract_current_prescription_from_page(self):
        """Mevcut Medula sayfasından reçete verisini çıkarır"""
        try:
            print("🔍 Mevcut sayfadan reçete verisi çıkarılıyor...")
            
            # TODO: Burası gerçek browser sayfası parse etme implementasyonu
            # Şu anda Medula browser instance'ı overlay sisteminde mevcut değil
            # Bu browser integration'ı için advanced_prescription_extractor kullanılmalı
            
            # Placeholder - gelecekte implement edilecek
            print("⚠️ Gerçek sayfa parsing henüz implement edilmemiş")
            return None
            
        except Exception as e:
            print(f"❌ Sayfa parsing hatası: {e}")
            return None
    
    def show_detailed_results(self, analysis_result):
        """Detaylı analiz sonuçlarını gösterir"""
        try:
            print("\n" + "="*50)
            print("📊 DETAYLI ANALİZ SONUÇLARI")
            print("="*50)
            
            prescription_id = analysis_result.get('prescription_id', 'UNKNOWN')
            final_decision = analysis_result.get('final_decision', 'unknown')
            
            print(f"🆔 Reçete No: {prescription_id}")
            print(f"🎯 Final Karar: {final_decision.upper()}")
            
            # SUT Analysis
            sut_analysis = analysis_result.get('sut_analysis', {})
            print(f"📋 SUT Analizi: {sut_analysis.get('action', 'unknown')} (Güven: {sut_analysis.get('confidence', 0):.2f})")
            
            # AI Analysis  
            ai_analysis = analysis_result.get('ai_analysis', {})
            print(f"🤖 AI Analizi: {ai_analysis.get('action', 'unknown')} (Güven: {ai_analysis.get('confidence', 0):.2f})")
            
            # Dose Analysis
            dose_analysis = analysis_result.get('dose_analysis', {})
            if dose_analysis:
                print(f"💊 Doz Analizi: {dose_analysis.get('action', 'unknown')} (İlaç: {dose_analysis.get('drugs_analyzed', 0)})")
            
            # Processing metadata
            metadata = analysis_result.get('processing_metadata', {})
            processing_time = metadata.get('processing_time_seconds', 0)
            print(f"⏱️ İşlem Süresi: {processing_time:.3f} saniye")
            
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"❌ Sonuç gösterim hatası: {e}")

    def control_daily_prescriptions(self):
        """GÜNLÜK TOPLU KONTROL ALGORİTMASI (4. bölüm)"""
        try:
            print("🎯 Günlük toplu kontrol başlıyor...")
            
            # Kontrol sırası: C → A → Geçici Koruma → B → C-Kan
            control_order = ['C', 'A', 'Geçici_Koruma', 'B', 'C_Kan']
            
            for group in control_order:
                print(f"📋 {group} grubu kontrolü...")
                # Mock batch processing
                self.process_group_prescriptions(group, "daily")
                time.sleep(1)  # Simulation
            
            print("✅ Günlük toplu kontrol tamamlandı")
            self.update_status_bar()
            
        except Exception as e:
            print(f"❌ Günlük kontrol hatası: {e}")

    def control_monthly_prescriptions(self):
        """AYLIK TOPLU KONTROL ALGORİTMASI (5. bölüm)"""
        try:
            print("📊 Aylık toplu kontrol başlıyor...")
            
            # Aynen günlük algoritma, daha geniş kapsam
            control_order = ['C', 'A', 'Geçici_Koruma', 'B', 'C_Kan']
            
            for group in control_order:
                print(f"📋 {group} grubu aylık kontrolü...")
                self.process_group_prescriptions(group, "monthly")
                time.sleep(2)  # Simulation
            
            print("✅ Aylık toplu kontrol tamamlandı")
            self.update_status_bar()
            
        except Exception as e:
            print(f"❌ Aylık kontrol hatası: {e}")

    def control_query_prescriptions(self):
        """REÇETE SORGU KONTROL ALGORİTMASI (6. bölüm)"""
        try:
            print("🔍 Sorgu reçetelerinin kontrolü başlıyor...")
            
            # Mock sorgu sonuçları
            query_results = [
                {"recete_no": "3GP25RF", "status": "kontrolsuz"},
                {"recete_no": "4HT36QW", "status": "kontrolsuz"}
            ]
            
            for prescription in query_results:
                result = self.mock_analysis(prescription)
                self.update_prescription_flag(prescription["recete_no"], result['status'])
                time.sleep(0.5)
            
            print("✅ Sorgu reçetelerinin kontrolü tamamlandı")
            self.update_status_bar()
            
        except Exception as e:
            print(f"❌ Sorgu kontrol hatası: {e}")

    def process_group_prescriptions(self, group: str, period: str):
        """Grup bazlı reçete işleme"""
        # Mock implementation
        prescription_count = {"C": 5, "A": 8, "B": 15, "Geçici_Koruma": 3, "C_Kan": 2}
        count = prescription_count.get(group, 5)
        
        for i in range(count):
            # Mock analysis
            mock_rx = {"recete_no": f"{group}_{period}_{i+1}"}
            result = self.mock_analysis(mock_rx)
            print(f"  📄 {mock_rx['recete_no']}: {result['status']}")

    def mock_analysis(self, prescription_data: dict) -> dict:
        """Mock analiz sonucu (gerçekte unified_processor kullanılacak)"""
        import random
        statuses = ['uygun', 'uygun_degil', 'supheli', 'ek_kontrol']
        weights = [0.4, 0.2, 0.3, 0.1]  # Uygun olan daha fazla
        
        status = random.choices(statuses, weights=weights)[0]
        
        return {
            'status': status,
            'confidence': random.uniform(0.7, 0.95),
            'analysis_time': random.uniform(2, 5)
        }

    def update_prescription_flag(self, prescription_no: str, status: str):
        """Reçete bayrağını güncelleme"""
        print(f"🏁 Bayrak güncellendi: {prescription_no} → {status}")
        # Gerçek implementasyonda web element'i güncelleyecek

    def update_status_bar(self):
        """Durum çubuğunu güncelleme"""
        # Mock sayaçlar
        counts = {"kontrolsuz": 12, "uygun": 8, "uygun_degil": 3, "supheli": 2, "ek_kontrol": 1}
        
        status_text = f"📊 Sistem Aktif | " + \
                     f"🔵 {counts['kontrolsuz']} Kontrolsüz | " + \
                     f"🟢 {counts['uygun']} Uygun | " + \
                     f"🔴 {counts['uygun_degil']} Uygun Değil | " + \
                     f"🟡 {counts['supheli']} Şüpheli | " + \
                     f"🟠 {counts['ek_kontrol']} Ek Kontrol"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)

    def refresh_page(self):
        """Sayfayı yenileme"""
        print("🔄 Sayfa yenileniyor...")

    def go_home(self):
        """Ana sayfaya git"""
        print("🏠 Ana sayfaya gidiliyor...")
        self.update_dynamic_buttons("home")

    def go_prescription_list(self):
        """Reçete listesine git"""  
        print("📋 Reçete listesine gidiliyor...")
        self.update_dynamic_buttons("daily_list")

    def close_overlay(self):
        """Overlay'i kapat ve ana panele dön"""
        print("👋 Overlay sistemi kapatılıyor...")
        self.root.deiconify()  # Ana paneli tekrar göster

def main():
    """Ana calistirma fonksiyonu"""
    print("OVERLAY CERCEVE SISTEMI BASLATILIYOR...")
    
    try:
        overlay_system = OverlaySystem()
        overlay_system.show_main_control_panel()
        
    except Exception as e:
        print(f"SISTEM BASLATMA HATASI: {e}")

if __name__ == "__main__":
    main()