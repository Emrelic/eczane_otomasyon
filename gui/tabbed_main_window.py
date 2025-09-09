#!/usr/bin/env python3
"""
Sekmeli Ana GUI Penceresi - Yeni Tasarım
5 Sekme + Küçültülmüş Log Alanı
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Proje root dizinini path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import Settings
from medula_automation.browser import MedulaBrowser
from ai_analyzer.decision_engine import DecisionEngine
from database.models import get_db_manager
from unified_prescription_processor import UnifiedPrescriptionProcessor
from advanced_batch_processor import AdvancedBatchProcessor
from gui.control_settings_window import ControlSettingsWindow

class TabbedMainWindow:
    """Yeni Sekmeli Ana GUI"""
    
    def __init__(self):
        # CustomTkinter tema
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Ana pencere
        self.root = ctk.CTk()
        self.root.title("🏥 Eczane Reçete Kontrol Sistemi - Sekmeli Versiyon")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Ayarları yükle
        try:
            self.settings = Settings()
        except ValueError as e:
            messagebox.showerror("Ayar Hatası", str(e))
            self.root.destroy()
            return
        
        # Bileşenler
        self.unified_processor = UnifiedPrescriptionProcessor()
        self.batch_processor = AdvancedBatchProcessor()
        self.db_manager = get_db_manager()
        
        # Kontrol ayarları
        self.control_settings = {}
        
        # GUI oluştur
        self.setup_gui()
        
    def setup_gui(self):
        """Ana GUI yapısını kur"""
        
        # Başlık
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🏥 ECZANE REÇETE KONTROL SİSTEMİ",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=15)
        
        # Kontrol ayarları butonu
        settings_button = ctk.CTkButton(
            title_frame,
            text="🎯 Kontrol Ayarları",
            command=self.open_control_settings,
            width=150
        )
        settings_button.pack(side="right", padx=10)
        
        # Ana container - Üst 3/4, Alt 1/4
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Üst alan container
        top_container = ctk.CTkFrame(main_container)
        top_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Sol panel - Hızlı işlem butonları
        self.setup_quick_actions_panel(top_container)
        
        # Sağ alan - Sekmeli yapı (3/4)
        self.tabview = ctk.CTkTabview(top_container, height=500)
        self.tabview.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # 5 Sekme oluştur
        self.create_tabs()
        
        # Alt alan - Log (1/4)
        self.setup_log_area(main_container)
    
    def setup_quick_actions_panel(self, parent):
        """Sol hızlı işlem paneli"""
        quick_panel = ctk.CTkFrame(parent)
        quick_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # Başlık
        ctk.CTkLabel(
            quick_panel,
            text="⚡ Hızlı İşlemler",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # İşlem Butonları
        buttons_frame = ctk.CTkFrame(quick_panel)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Medula Live
        self.medula_live_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Medula Live",
            command=self.process_medula_live,
            width=150,
            height=35
        )
        self.medula_live_btn.pack(pady=3)
        
        # JSON İşle
        self.json_btn = ctk.CTkButton(
            buttons_frame,
            text="📄 JSON İşle",
            command=self.process_json,
            width=150,
            height=35
        )
        self.json_btn.pack(pady=3)
        
        # Batch İşle
        self.batch_btn = ctk.CTkButton(
            buttons_frame,
            text="📊 Batch İşle",
            command=self.process_batch,
            width=150,
            height=35
        )
        self.batch_btn.pack(pady=3)
        
        # Gelişmiş Batch
        self.advanced_batch_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Gelişmiş Batch",
            command=self.process_advanced_batch,
            width=150,
            height=35
        )
        self.advanced_batch_btn.pack(pady=3)
        
        # Ayırıcı
        separator = ctk.CTkFrame(quick_panel, height=2)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Database & System
        system_frame = ctk.CTkFrame(quick_panel)
        system_frame.pack(fill="x", padx=10, pady=5)
        
        # DB Test
        self.db_test_btn = ctk.CTkButton(
            system_frame,
            text="🔧 DB Test",
            command=self.test_database,
            width=150,
            height=35
        )
        self.db_test_btn.pack(pady=3)
        
        # İstatistikler
        self.stats_btn = ctk.CTkButton(
            system_frame,
            text="📊 İstatistikler",
            command=self.show_statistics,
            width=150,
            height=35
        )
        self.stats_btn.pack(pady=3)
        
        # Ayarları Göster
        self.settings_btn = ctk.CTkButton(
            system_frame,
            text="🔧 Sistem Ayarları",
            command=self.show_settings,
            width=150,
            height=35
        )
        self.settings_btn.pack(pady=3)
        
    def create_tabs(self):
        """5 ana sekmeyi oluştur"""
        
        # Sekmeleri ekle
        self.tabview.add("📱 E-Reçete Sorgu")
        self.tabview.add("📝 Reçete Giriş") 
        self.tabview.add("📊 Reçete Listesi")
        self.tabview.add("📅 Günlük Liste")
        self.tabview.add("🔍 Reçete Sorgu")
        
        # Her sekmenin içeriğini oluştur
        self.setup_erecete_tab()
        self.setup_giris_tab()
        self.setup_liste_tab()
        self.setup_gunluk_tab()
        self.setup_sorgu_tab()
        
    def setup_erecete_tab(self):
        """1. Sekme - E-Reçete Sorgu"""
        tab = self.tabview.tab("📱 E-Reçete Sorgu")
        
        # Development notice
        dev_frame = ctk.CTkFrame(tab)
        dev_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        dev_label = ctk.CTkLabel(
            dev_frame,
            text="🚧 YAPIM AŞAMASINDA 🚧",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="orange"
        )
        dev_label.pack(pady=50)
        
        description = ctk.CTkLabel(
            dev_frame,
            text="Bu sekme TC kimlik numarası ve E-reçete numarası ile\nspesifik reçeteleri görüntülemeye yarayacak.\n\nŞu anda kayıtlı reçetelerde kontrol yapıldığı için\nbu özellik henüz geliştirilmemiştir.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        description.pack(pady=30)
        
    def setup_giris_tab(self):
        """2. Sekme - Reçete Giriş"""
        tab = self.tabview.tab("📝 Reçete Giriş")
        
        # Development notice
        dev_frame = ctk.CTkFrame(tab)
        dev_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        dev_label = ctk.CTkLabel(
            dev_frame,
            text="🚧 YAPIM AŞAMASINDA 🚧",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="orange"
        )
        dev_label.pack(pady=50)
        
        description = ctk.CTkLabel(
            dev_frame,
            text="Bu sekme kağıt reçetelerden bilgi girişi için\nmanuel veri giriş ekranı olacak.\n\nŞu anda otomatik Medula işlemleri öncelikli olduğu için\nbu özellik henüz geliştirilmemiştir.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        description.pack(pady=30)
        
    def setup_liste_tab(self):
        """3. Sekme - Reçete Listesi (ANA SEKMEMİZ)"""
        tab = self.tabview.tab("📊 Reçete Listesi")
        
        # Sol panel - Kontroller
        left_frame = ctk.CTkFrame(tab)
        left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        # Başlık
        ctk.CTkLabel(
            left_frame,
            text="📊 Reçete Listesi Kontrolü",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Dönem seçimi
        period_frame = ctk.CTkFrame(left_frame)
        period_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(period_frame, text="📅 Dönem:").pack(pady=(5, 0))
        self.period_var = ctk.StringVar(value="Bu Ay")
        period_combo = ctk.CTkComboBox(
            period_frame,
            values=["Bu Ay", "Geçen Ay", "Son 7 Gün", "Bugün", "Özel Aralık"],
            variable=self.period_var,
            width=180
        )
        period_combo.pack(pady=5)
        
        # Grup seçimi
        group_frame = ctk.CTkFrame(left_frame)
        group_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(group_frame, text="🏥 Reçete Grubu:").pack(pady=(5, 0))
        
        # Grup checkboxları
        self.group_vars = {}
        groups = [
            ("A", "A Grubu (Raporlu)", "green"),
            ("B", "B Grubu (Normal)", "blue"), 
            ("C", "C Grubu (Kotalı)", "orange"),
            ("C_blood", "C-Kan Ürünü", "red"),
            ("temp_protection", "Geçici Koruma", "purple")
        ]
        
        for group_id, label, color in groups:
            self.group_vars[group_id] = ctk.BooleanVar(value=group_id=="A")
            
            checkbox = ctk.CTkCheckBox(
                group_frame,
                text=label,
                variable=self.group_vars[group_id],
                text_color=color
            )
            checkbox.pack(anchor="w", pady=3)
        
        # Kontrol butonu
        control_button = ctk.CTkButton(
            left_frame,
            text="🚀 Kontrolü Başlat",
            command=self.start_liste_control,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        control_button.pack(pady=20)
        
        # Sağ panel - Sonuçlar
        self.setup_results_panel(tab)
        
    def setup_gunluk_tab(self):
        """4. Sekme - Günlük Liste"""
        tab = self.tabview.tab("📅 Günlük Liste")
        
        # Sol panel - Kontroller
        left_frame = ctk.CTkFrame(tab)
        left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        # Başlık
        ctk.CTkLabel(
            left_frame,
            text="📅 Günlük Kontrol",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Tarih seçimi
        date_frame = ctk.CTkFrame(left_frame)
        date_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(date_frame, text="📆 Tarih Seç:").pack(pady=(5, 0))
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=self.date_var,
            placeholder_text="DD.MM.YYYY",
            width=180
        )
        date_entry.pack(pady=5)
        
        # Hızlı tarih butonları
        quick_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        quick_frame.pack(fill="x", pady=5)
        
        today_btn = ctk.CTkButton(
            quick_frame,
            text="Bugün",
            command=lambda: self.date_var.set(datetime.now().strftime("%d.%m.%Y")),
            width=60
        )
        today_btn.pack(side="left", padx=2)
        
        yesterday_btn = ctk.CTkButton(
            quick_frame,
            text="Dün",
            command=lambda: self.date_var.set((datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")),
            width=60
        )
        yesterday_btn.pack(side="left", padx=2)
        
        # Kontrol butonu
        daily_control_button = ctk.CTkButton(
            left_frame,
            text="📅 Günlük Kontrolü Başlat",
            command=self.start_daily_control,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        daily_control_button.pack(pady=20)
        
        # Sağ panel - Sonuçlar
        self.setup_results_panel(tab)
        
    def setup_sorgu_tab(self):
        """5. Sekme - Reçete Sorgu"""
        tab = self.tabview.tab("🔍 Reçete Sorgu")
        
        # Ana container
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        ctk.CTkLabel(
            main_frame,
            text="🔍 Reçete Sorgu - Medula Tarzı",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 30))
        
        # Sorgu alanları
        query_frame = ctk.CTkFrame(main_frame)
        query_frame.pack(pady=20)
        
        # E-reçete numarası sorgu
        erecete_frame = ctk.CTkFrame(query_frame)
        erecete_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            erecete_frame,
            text="📱 E-Reçete Numarası:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        erecete_input_frame = ctk.CTkFrame(erecete_frame, fg_color="transparent")
        erecete_input_frame.pack(fill="x", pady=(0, 10))
        
        self.erecete_var = ctk.StringVar()
        erecete_entry = ctk.CTkEntry(
            erecete_input_frame,
            textvariable=self.erecete_var,
            placeholder_text="E-reçete numarasını girin...",
            width=300
        )
        erecete_entry.pack(side="left", padx=(0, 10))
        
        erecete_btn = ctk.CTkButton(
            erecete_input_frame,
            text="🔍 E-Reçete Sorgula",
            command=self.query_erecete,
            width=150
        )
        erecete_btn.pack(side="left")
        
        # TC kimlik sorgu
        tc_frame = ctk.CTkFrame(query_frame)
        tc_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            tc_frame,
            text="🆔 TC Kimlik Numarası:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        tc_input_frame = ctk.CTkFrame(tc_frame, fg_color="transparent")
        tc_input_frame.pack(fill="x", pady=(0, 10))
        
        self.tc_var = ctk.StringVar()
        tc_entry = ctk.CTkEntry(
            tc_input_frame,
            textvariable=self.tc_var,
            placeholder_text="TC kimlik numarasını girin...",
            width=300
        )
        tc_entry.pack(side="left", padx=(0, 10))
        
        tc_btn = ctk.CTkButton(
            tc_input_frame,
            text="🔍 TC ile Sorgula",
            command=self.query_tc,
            width=150
        )
        tc_btn.pack(side="left")
        
        # Sonuç alanı
        self.setup_results_panel(tab)
        
    def setup_results_panel(self, parent):
        """Sonuçlar paneli - her sekmede kullanılacak"""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Başlık
        ctk.CTkLabel(
            results_frame,
            text="📊 Kontrol Sonuçları",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Sonuçlar tablosu (placeholder)
        results_text = ctk.CTkTextbox(results_frame, height=300)
        results_text.pack(fill="both", expand=True, padx=10, pady=10)
        results_text.insert("0.0", "Henüz kontrol işlemi başlatılmamış.\n\n🚀 Sol taraftaki 'Kontrolü Başlat' butonuna tıklayın.\n\nSonuçlar burada görünecek:\n- ✅ Onaylanan reçeteler\n- ❌ Reddedilen reçeteler  \n- ⏳ Bekletilen reçeteler\n- 📊 İstatistikler")
        
    def setup_log_area(self, parent):
        """Alt log alanı - 1/4 yükseklik"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="x", pady=5)
        
        # Log başlık
        log_header = ctk.CTkFrame(log_frame)
        log_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            log_header,
            text="📝 Sistem Logları",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Clear button
        clear_btn = ctk.CTkButton(
            log_header,
            text="🗑️ Temizle",
            command=self.clear_logs,
            width=80
        )
        clear_btn.pack(side="right")
        
        # Log text area
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", padx=10, pady=(0, 10))
        
        # İlk log mesajı
        self.log_message("🏥 Eczane Reçete Kontrol Sistemi başlatıldı")
        self.log_message("🎯 Kontrol ayarlarını seçin ve kontrolü başlatın")
        
    def open_control_settings(self):
        """Kontrol ayarları penceresini aç"""
        try:
            settings_window = ControlSettingsWindow(self.root)
            self.log_message("🎯 Kontrol ayarları penceresi açıldı")
        except Exception as e:
            self.log_message(f"❌ Kontrol ayarları hatası: {e}")
    
    def start_liste_control(self):
        """Reçete listesi kontrolünü başlat"""
        try:
            # Seçili grupları al
            selected_groups = [k for k, v in self.group_vars.items() if v.get()]
            period = self.period_var.get()
            
            if not selected_groups:
                messagebox.showwarning("Uyarı", "En az bir grup seçmelisiniz!")
                return
                
            self.log_message(f"🚀 Reçete listesi kontrolü başlatılıyor...")
            self.log_message(f"📊 Gruplar: {', '.join(selected_groups)}")
            self.log_message(f"📅 Dönem: {period}")
            
            # Thread'de çalıştır
            def process_thread():
                try:
                    results = self.unified_processor.process_from_medula_live(
                        limit=10,
                        group=selected_groups[0] if selected_groups else 'A'
                    )
                    
                    self.log_message(f"✅ Liste kontrolü tamamlandı: {len(results)} reçete")
                    
                except Exception as e:
                    self.log_message(f"❌ Liste kontrol hatası: {e}")
            
            threading.Thread(target=process_thread, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Liste kontrol başlatma hatası: {e}")
    
    def start_daily_control(self):
        """Günlük kontrolü başlat"""
        try:
            selected_date = self.date_var.get()
            self.log_message(f"📅 Günlük kontrol başlatılıyor: {selected_date}")
            
            # TODO: Günlük kontrol implementasyonu
            self.log_message("⚠️ Günlük kontrol henüz geliştirilmemiş")
            
        except Exception as e:
            self.log_message(f"❌ Günlük kontrol hatası: {e}")
    
    def query_erecete(self):
        """E-reçete numarası ile sorgu"""
        erecete_no = self.erecete_var.get().strip()
        if not erecete_no:
            messagebox.showwarning("Uyarı", "E-reçete numarası girin!")
            return
            
        self.log_message(f"🔍 E-reçete sorgusu: {erecete_no}")
        # TODO: E-reçete sorgu implementasyonu
        self.log_message("⚠️ E-reçete sorgu henüz geliştirilmemiş")
    
    def query_tc(self):
        """TC kimlik ile sorgu"""
        tc_no = self.tc_var.get().strip()
        if not tc_no:
            messagebox.showwarning("Uyarı", "TC kimlik numarası girin!")
            return
            
        if len(tc_no) != 11:
            messagebox.showwarning("Uyarı", "TC kimlik numarası 11 haneli olmalı!")
            return
            
        self.log_message(f"🔍 TC kimlik sorgusu: {tc_no}")
        # TODO: TC kimlik sorgu implementasyonu
        self.log_message("⚠️ TC kimlik sorgu henüz geliştirilmemiş")
    
    def log_message(self, message):
        """Log mesajı ekle"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            
            self.log_text.insert("end", log_line)
            self.log_text.see("end")
            
        except Exception as e:
            print(f"Log error: {e}")
    
    def clear_logs(self):
        """Logları temizle"""
        try:
            self.log_text.delete("0.0", "end")
            self.log_message("🗑️ Loglar temizlendi")
        except Exception as e:
            print(f"Clear logs error: {e}")
    
    # Hızlı işlem fonksiyonları
    def process_medula_live(self):
        """Medula Live işleme"""
        try:
            self.log_message("🔄 Medula Live işleme başlatılıyor...")
            
            def process_thread():
                try:
                    results = self.unified_processor.process_from_medula_live(limit=5, group='A')
                    self.log_message(f"✅ Medula Live tamamlandı: {len(results)} reçete")
                except Exception as e:
                    self.log_message(f"❌ Medula Live hatası: {e}")
            
            threading.Thread(target=process_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Medula Live başlatma hatası: {e}")
    
    def process_json(self):
        """JSON dosya işleme"""
        try:
            self.log_message("📄 JSON işleme başlatılıyor...")
            
            def process_thread():
                try:
                    results = self.unified_processor.process_from_json(limit=5)
                    self.log_message(f"✅ JSON işleme tamamlandı: {len(results)} reçete")
                except Exception as e:
                    self.log_message(f"❌ JSON işleme hatası: {e}")
            
            threading.Thread(target=process_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ JSON başlatma hatası: {e}")
    
    def process_batch(self):
        """Batch işleme"""
        try:
            self.log_message("📊 Batch işleme başlatılıyor...")
            
            def process_thread():
                try:
                    results = self.batch_processor.process_batch(batch_size=10)
                    self.log_message(f"✅ Batch işleme tamamlandı: {len(results)} reçete")
                except Exception as e:
                    self.log_message(f"❌ Batch işleme hatası: {e}")
            
            threading.Thread(target=process_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Batch başlatma hatası: {e}")
    
    def process_advanced_batch(self):
        """Gelişmiş batch işleme"""
        try:
            self.log_message("🚀 Gelişmiş batch işleme başlatılıyor...")
            
            def process_thread():
                try:
                    results = self.batch_processor.advanced_processing(limit=20)
                    self.log_message(f"✅ Gelişmiş batch tamamlandı: {len(results)} reçete")
                except Exception as e:
                    self.log_message(f"❌ Gelişmiş batch hatası: {e}")
            
            threading.Thread(target=process_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Gelişmiş batch başlatma hatası: {e}")
    
    def test_database(self):
        """Database test"""
        try:
            self.log_message("🔧 Database test başlatılıyor...")
            
            def test_thread():
                try:
                    # Test database connection
                    stats = self.db_manager.get_prescription_stats()
                    total = stats.get('total_prescriptions', 0)
                    self.log_message(f"✅ DB Test başarılı: {total} reçete kayıtlı")
                except Exception as e:
                    self.log_message(f"❌ DB Test hatası: {e}")
            
            threading.Thread(target=test_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ DB Test başlatma hatası: {e}")
    
    def show_statistics(self):
        """İstatistikleri göster"""
        try:
            self.log_message("📊 İstatistikler yükleniyor...")
            
            def stats_thread():
                try:
                    stats = self.db_manager.get_prescription_stats()
                    
                    stats_text = f"""
📊 SİSTEM İSTATİSTİKLERİ:
- Toplam Reçete: {stats.get('total_prescriptions', 0)}
- Onaylanan: {stats.get('approved', 0)}
- Reddedilen: {stats.get('rejected', 0)}
- Bekletilen: {stats.get('pending', 0)}
- Son İşlem: {stats.get('last_processed', 'Yok')}
                    """
                    
                    self.log_message(stats_text)
                except Exception as e:
                    self.log_message(f"❌ İstatistik hatası: {e}")
            
            threading.Thread(target=stats_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ İstatistik başlatma hatası: {e}")
    
    def show_settings(self):
        """Sistem ayarlarını göster"""
        try:
            settings_info = f"""
🔧 SİSTEM AYARLARI:
- Medula URL: {self.settings.medula_url}
- Browser: {self.settings.browser_type}
- Headless: {self.settings.headless}
- AI Provider: {self.settings.ai_provider}
- AI Model: {self.settings.ai_model}
- Kontrol Aralığı: {self.settings.check_interval}s
- Auto Approve: {self.settings.auto_approve_threshold}
            """
            self.log_message(settings_info)
        except Exception as e:
            self.log_message(f"❌ Ayar gösterme hatası: {e}")
    
    def run(self):
        """GUI'yi başlat"""
        self.root.mainloop()

def main():
    """Ana fonksiyon"""
    app = TabbedMainWindow()
    app.run()

if __name__ == "__main__":
    main()