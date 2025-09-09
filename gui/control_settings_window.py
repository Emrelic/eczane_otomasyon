#!/usr/bin/env python3
"""
Reçete Kontrol Ayarları Ekranı
Comprehensive Control Settings Window for Prescription Processing
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import json
from pathlib import Path

class ControlSettingsWindow:
    def __init__(self, parent=None):
        self.parent = parent
        self.settings_data = self.load_control_settings()
        
        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("🎯 Reçete Kontrol Ayarları")
        self.window.geometry("800x700")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the complete UI"""
        
        # Main container with scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.window)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="🎯 REÇETE KONTROL AYARLARI",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # 1. KONTROL MODU SEÇİMİ
        self.setup_control_mode_section()
        
        # 2. GRUP FİLTRELEME SEÇENEKLERİ
        self.setup_group_filter_section()
        
        # 3. TARİH ARALIĞI SEÇENEKLERİ
        self.setup_date_range_section()
        
        # 4. TEK REÇETE SORGU SEÇENEKLERİ
        self.setup_single_prescription_section()
        
        # 5. TOPLU İŞLEM SEÇENEKLERİ
        self.setup_batch_processing_section()
        
        # 6. GELİŞMİŞ KONTROL SEÇENEKLERİ
        self.setup_advanced_control_section()
        
        # Butonlar
        self.setup_buttons()
        
    def setup_control_mode_section(self):
        """Ana kontrol modu seçimi"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            frame, 
            text="🔧 1. KONTROL MODU SEÇİMİ",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Control mode options
        self.control_mode = ctk.StringVar(value="monthly_review")
        
        modes = [
            ("monthly_review", "📅 Aylık Reçete Gözden Geçirme", "Belirli tarih aralığında tüm reçeteler"),
            ("single_query", "🔍 Tek Reçete Sorgulama", "TC kimlik veya reçete no ile spesifik arama"),
            ("patient_history", "👤 Hasta Geçmişi", "Bir hastanın tüm faturası çıkmamış reçeteleri"),
            ("group_processing", "📊 Grup Bazlı İşlem", "A/B/C grubu reçetelerini toplu işleme"),
            ("daily_monitoring", "⏰ Günlük İzleme", "Günlük bazda reçete kontrolü"),
            ("manual_entry", "📝 Manuel Giriş", "Kağıt reçete sisteme giriş ve kontrol")
        ]
        
        for value, text, desc in modes:
            radio_frame = ctk.CTkFrame(frame, fg_color="transparent")
            radio_frame.pack(fill="x", padx=20, pady=5)
            
            radio = ctk.CTkRadioButton(
                radio_frame,
                text=text,
                variable=self.control_mode,
                value=value,
                command=self.on_control_mode_change
            )
            radio.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                radio_frame,
                text=f"   → {desc}",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            desc_label.pack(anchor="w")
            
    def setup_group_filter_section(self):
        """Grup filtreleme seçenekleri"""
        self.group_frame = ctk.CTkFrame(self.scroll_frame)
        self.group_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            self.group_frame, 
            text="📊 2. GRUP FİLTRELEME",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Group selection checkboxes
        groups_frame = ctk.CTkFrame(self.group_frame, fg_color="transparent")
        groups_frame.pack(fill="x", padx=20)
        
        # Create 2 columns
        left_col = ctk.CTkFrame(groups_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)
        
        right_col = ctk.CTkFrame(groups_frame, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)
        
        # Group checkboxes
        self.group_vars = {}
        groups = [
            ("A", "A Grubu", "Raporlu ilaçlar (bir tane bile varsa)", left_col),
            ("B", "B Grubu", "Normal raporsuz ilaçlar", left_col),
            ("C", "C Grubu", "Sıralı dağıtım/üst limitli/kotalı", right_col),
            ("C_blood", "C Grubu - Kan Ürünleri", "Kan ürünü + sıralı dağıtım", right_col),
            ("temp_protection", "Geçici Koruma", "Mülteci/Suriyeli reçeteleri", right_col)
        ]
        
        for key, label, desc, parent in groups:
            self.group_vars[key] = ctk.BooleanVar(value=True)
            
            group_frame = ctk.CTkFrame(parent, fg_color="transparent")
            group_frame.pack(fill="x", pady=5)
            
            checkbox = ctk.CTkCheckBox(
                group_frame,
                text=label,
                variable=self.group_vars[key]
            )
            checkbox.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                group_frame,
                text=f"   → {desc}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            desc_label.pack(anchor="w")
            
    def setup_date_range_section(self):
        """Tarih aralığı seçenekleri"""
        self.date_frame = ctk.CTkFrame(self.scroll_frame)
        self.date_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            self.date_frame, 
            text="📅 3. TARİH ARALIĞI",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Date range type
        date_options_frame = ctk.CTkFrame(self.date_frame, fg_color="transparent")
        date_options_frame.pack(fill="x", padx=20)
        
        self.date_range_type = ctk.StringVar(value="current_month")
        
        date_options = [
            ("current_month", "Bu Ay", "Mevcut ayın tüm reçeteleri"),
            ("last_month", "Geçen Ay", "Önceki ayın reçeteleri"),
            ("last_7_days", "Son 7 Gün", "Geçen haftalık reçeteler"),
            ("custom_range", "Özel Aralık", "Manuel tarih seçimi"),
            ("today_only", "Sadece Bugün", "Güncel reçeteler")
        ]
        
        for value, text, desc in date_options:
            radio_frame = ctk.CTkFrame(date_options_frame, fg_color="transparent")
            radio_frame.pack(fill="x", pady=3)
            
            radio = ctk.CTkRadioButton(
                radio_frame,
                text=text,
                variable=self.date_range_type,
                value=value,
                command=self.on_date_range_change
            )
            radio.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                radio_frame,
                text=f"   → {desc}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            desc_label.pack(anchor="w")
        
        # Custom date selection (initially hidden)
        self.custom_date_frame = ctk.CTkFrame(self.date_frame)
        
        start_date_label = ctk.CTkLabel(self.custom_date_frame, text="Başlangıç Tarihi:")
        start_date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.start_date_var = ctk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.start_date_entry = ctk.CTkEntry(self.custom_date_frame, textvariable=self.start_date_var)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        end_date_label = ctk.CTkLabel(self.custom_date_frame, text="Bitiş Tarihi:")
        end_date_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.end_date_var = ctk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.end_date_entry = ctk.CTkEntry(self.custom_date_frame, textvariable=self.end_date_var)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=10)
        
    def setup_single_prescription_section(self):
        """Tek reçete sorgu seçenekleri"""
        self.single_frame = ctk.CTkFrame(self.scroll_frame)
        self.single_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            self.single_frame, 
            text="🔍 4. TEK REÇETE SORGU",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Query type
        query_frame = ctk.CTkFrame(self.single_frame, fg_color="transparent")
        query_frame.pack(fill="x", padx=20)
        
        self.single_query_type = ctk.StringVar(value="tc_id")
        
        # Query type selection
        tc_radio = ctk.CTkRadioButton(
            query_frame,
            text="TC Kimlik No ile Sorgu",
            variable=self.single_query_type,
            value="tc_id"
        )
        tc_radio.pack(anchor="w", pady=5)
        
        prescription_radio = ctk.CTkRadioButton(
            query_frame,
            text="Reçete/Takip No ile Sorgu",
            variable=self.single_query_type,
            value="prescription_no"
        )
        prescription_radio.pack(anchor="w", pady=5)
        
        # Input fields
        input_frame = ctk.CTkFrame(self.single_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        tc_label = ctk.CTkLabel(input_frame, text="TC Kimlik No:")
        tc_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.tc_id_var = ctk.StringVar()
        self.tc_id_entry = ctk.CTkEntry(input_frame, textvariable=self.tc_id_var, width=200)
        self.tc_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        prescription_label = ctk.CTkLabel(input_frame, text="Reçete/Takip No:")
        prescription_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.prescription_no_var = ctk.StringVar()
        self.prescription_no_entry = ctk.CTkEntry(input_frame, textvariable=self.prescription_no_var, width=200)
        self.prescription_no_entry.grid(row=1, column=1, padx=10, pady=5)
        
    def setup_batch_processing_section(self):
        """Toplu işlem seçenekleri"""
        batch_frame = ctk.CTkFrame(self.scroll_frame)
        batch_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            batch_frame, 
            text="📦 5. TOPLU İŞLEM",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Batch options
        options_frame = ctk.CTkFrame(batch_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20)
        
        # Processing limit
        limit_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        limit_frame.pack(fill="x", pady=5)
        
        limit_label = ctk.CTkLabel(limit_frame, text="İşlem Limiti (0 = Tümü):")
        limit_label.pack(side="left")
        
        self.processing_limit_var = ctk.StringVar(value="50")
        limit_entry = ctk.CTkEntry(limit_frame, textvariable=self.processing_limit_var, width=100)
        limit_entry.pack(side="left", padx=10)
        
        # Auto-stop conditions
        self.auto_stop_errors = ctk.BooleanVar(value=True)
        error_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="5 hata sonrası durdur",
            variable=self.auto_stop_errors
        )
        error_checkbox.pack(anchor="w", pady=3)
        
        self.save_progress = ctk.BooleanVar(value=True)
        save_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="İlerleyişi kaydet (kaldığı yerden devam)",
            variable=self.save_progress
        )
        save_checkbox.pack(anchor="w", pady=3)
        
        self.detailed_logging = ctk.BooleanVar(value=False)
        log_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Detaylı log kayıt",
            variable=self.detailed_logging
        )
        log_checkbox.pack(anchor="w", pady=3)
        
    def setup_advanced_control_section(self):
        """Gelişmiş kontrol seçenekleri"""
        advanced_frame = ctk.CTkFrame(self.scroll_frame)
        advanced_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            advanced_frame, 
            text="⚙️ 6. GELİŞMİŞ KONTROLLER",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=15)
        
        # Advanced options
        options_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20)
        
        # Control level
        level_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        level_frame.pack(fill="x", pady=5)
        
        level_label = ctk.CTkLabel(level_frame, text="Kontrol Seviyesi:")
        level_label.pack(anchor="w")
        
        self.control_level = ctk.StringVar(value="standard")
        
        level_options = [
            ("fast", "Hızlı (Sadece temel kontroller)"),
            ("standard", "Standart (Normal kontrol süreci)"),
            ("detailed", "Detaylı (Tam analiz + AI)")
        ]
        
        for value, text in level_options:
            radio = ctk.CTkRadioButton(
                level_frame,
                text=text,
                variable=self.control_level,
                value=value
            )
            radio.pack(anchor="w", padx=20, pady=2)
        
        # Additional controls
        self.skip_processed = ctk.BooleanVar(value=True)
        skip_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Daha önce işlenen reçeteleri atla",
            variable=self.skip_processed
        )
        skip_checkbox.pack(anchor="w", pady=3)
        
        self.use_ai_analysis = ctk.BooleanVar(value=True)
        ai_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="AI analizi kullan (Claude)",
            variable=self.use_ai_analysis
        )
        ai_checkbox.pack(anchor="w", pady=3)
        
        self.conservative_decisions = ctk.BooleanVar(value=True)
        conservative_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Muhafazakar karar verme (şüphede beklet)",
            variable=self.conservative_decisions
        )
        conservative_checkbox.pack(anchor="w", pady=3)
        
    def setup_buttons(self):
        """Butonları ayarla"""
        button_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Test settings button
        test_button = ctk.CTkButton(
            button_frame,
            text="🧪 Ayarları Test Et",
            command=self.test_settings,
            width=150
        )
        test_button.pack(side="left", padx=10)
        
        # Save and apply
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet & Uygula",
            command=self.save_and_apply,
            width=150
        )
        save_button.pack(side="right", padx=10)
        
        # Cancel
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=self.cancel,
            width=100,
            fg_color="gray"
        )
        cancel_button.pack(side="right", padx=5)
        
    def on_control_mode_change(self):
        """Kontrol modu değiştiğinde UI güncelle"""
        mode = self.control_mode.get()
        
        # Show/hide relevant sections based on mode
        if mode == "single_query":
            self.single_frame.pack(fill="x", pady=(0, 20))
            self.group_frame.pack_forget()
            self.date_frame.pack_forget()
        elif mode == "group_processing":
            self.group_frame.pack(fill="x", pady=(0, 20))
            self.date_frame.pack(fill="x", pady=(0, 20))
            self.single_frame.pack_forget()
        elif mode == "manual_entry":
            self.single_frame.pack_forget()
            self.group_frame.pack_forget()
            self.date_frame.pack_forget()
        else:  # monthly_review, patient_history, daily_monitoring
            self.group_frame.pack(fill="x", pady=(0, 20))
            self.date_frame.pack(fill="x", pady=(0, 20))
            self.single_frame.pack_forget()
            
    def on_date_range_change(self):
        """Tarih aralığı seçimi değiştiğinde"""
        if self.date_range_type.get() == "custom_range":
            self.custom_date_frame.pack(fill="x", padx=20, pady=10)
        else:
            self.custom_date_frame.pack_forget()
            
    def test_settings(self):
        """Ayarları test et"""
        settings = self.get_current_settings()
        
        # Create test summary
        summary = f"""
🧪 TEST AYARLARI ÖZETİ:

📋 Kontrol Modu: {settings['control_mode']}
📊 Seçili Gruplar: {', '.join([k for k, v in settings['groups'].items() if v])}
📅 Tarih Aralığı: {settings['date_range_type']}
🔍 İşlem Limiti: {settings['processing_limit']}
⚙️ Kontrol Seviyesi: {settings['control_level']}

✅ AI Analizi: {'Aktif' if settings['use_ai_analysis'] else 'Pasif'}
✅ Muhafazakar Kararlar: {'Aktif' if settings['conservative_decisions'] else 'Pasif'}
✅ İşlenmiş Atla: {'Aktif' if settings['skip_processed'] else 'Pasif'}
        """
        
        messagebox.showinfo("Test Sonucu", summary)
        
    def get_current_settings(self):
        """Mevcut ayarları al"""
        return {
            "control_mode": self.control_mode.get(),
            "groups": {k: v.get() for k, v in self.group_vars.items()},
            "date_range_type": self.date_range_type.get(),
            "start_date": self.start_date_var.get(),
            "end_date": self.end_date_var.get(),
            "single_query_type": self.single_query_type.get(),
            "tc_id": self.tc_id_var.get(),
            "prescription_no": self.prescription_no_var.get(),
            "processing_limit": int(self.processing_limit_var.get() or 0),
            "auto_stop_errors": self.auto_stop_errors.get(),
            "save_progress": self.save_progress.get(),
            "detailed_logging": self.detailed_logging.get(),
            "control_level": self.control_level.get(),
            "skip_processed": self.skip_processed.get(),
            "use_ai_analysis": self.use_ai_analysis.get(),
            "conservative_decisions": self.conservative_decisions.get()
        }
        
    def save_and_apply(self):
        """Ayarları kaydet ve uygula"""
        settings = self.get_current_settings()
        
        # Validate settings
        if not self.validate_settings(settings):
            return
            
        # Save to file
        self.save_control_settings(settings)
        
        # Return settings to parent
        if self.parent and hasattr(self.parent, 'apply_control_settings'):
            self.parent.apply_control_settings(settings)
            
        messagebox.showinfo("Başarılı", "Ayarlar kaydedildi ve uygulandı!")
        self.window.destroy()
        
    def validate_settings(self, settings):
        """Ayarları doğrula"""
        # Date validation for custom range
        if settings['date_range_type'] == 'custom_range':
            try:
                datetime.strptime(settings['start_date'], "%d.%m.%Y")
                datetime.strptime(settings['end_date'], "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz tarih formatı! DD.MM.YYYY formatında giriniz.")
                return False
                
        # Single query validation
        if settings['control_mode'] == 'single_query':
            if not settings['tc_id'] and not settings['prescription_no']:
                messagebox.showerror("Hata", "Tek reçete sorgu için TC kimlik veya reçete numarası gerekli!")
                return False
                
        return True
        
    def cancel(self):
        """İptal"""
        self.window.destroy()
        
    def load_control_settings(self):
        """Kayıtlı ayarları yükle"""
        settings_file = Path("control_settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_control_settings(self, settings):
        """Ayarları dosyaya kaydet"""
        try:
            with open("control_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}")
            
    def load_current_settings(self):
        """Mevcut ayarları UI'ya yükle"""
        if not self.settings_data:
            return
            
        # Load control mode
        if 'control_mode' in self.settings_data:
            self.control_mode.set(self.settings_data['control_mode'])
            
        # Load groups
        if 'groups' in self.settings_data:
            for key, value in self.settings_data['groups'].items():
                if key in self.group_vars:
                    self.group_vars[key].set(value)
                    
        # Load other settings...
        # (Additional loading logic as needed)

# Test function
def test_control_settings():
    """Test the control settings window"""
    root = ctk.CTk()
    root.withdraw()  # Hide main window
    
    settings_window = ControlSettingsWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    test_control_settings()