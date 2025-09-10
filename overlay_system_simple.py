"""
OVERLAY CERCEVE SISTEMI - BASIT VERSIYON
Medula ustune cerceve giydiren hibrit sistem
Unicode/emoji sorunlari olmadan
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
from typing import Dict, List, Optional
import time

class OverlaySystem:
    """Ana Overlay Cerceve Sistemi"""
    
    def __init__(self):
        self.root = None
        self.processor = None
        self.settings = {}
        
        # Bayrak sistemi renk kodlari
        self.status_colors = {
            'uygun': '#28a745',          # Yesil
            'uygun_degil': '#dc3545',    # Kirmizi  
            'supheli': '#ffc107',        # Sari
            'ek_kontrol': '#fd7e14',     # Turuncu
            'kontrolsuz': '#17a2b8'      # Acik mavi
        }
        
        self.current_prescriptions = []
        self.init_system()

    def init_system(self):
        """Sistem baslatma"""
        try:
            self.settings = {}
            print("Overlay sistemi baslatildi")
        except Exception as e:
            print(f"Sistem baslatma hatasi: {e}")
            self.settings = {}

    def show_main_control_panel(self):
        """IC KAPI - Ana Sayfa"""
        self.root = tk.Tk()
        self.root.title("Reçete Kontrol Çerçevesi")
        self.root.geometry("600x400")
        self.root.configure(bg='#f8f9fa')
        
        # Ana frame
        main_frame = tk.Frame(self.root, bg='#f8f9fa', padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Baslik
        title_label = tk.Label(main_frame, 
                              text="REÇETE KONTROL ÇERÇEVESİ", 
                              font=('Arial', 20, 'bold'),
                              bg='#f8f9fa', fg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        # Alt baslik
        subtitle_label = tk.Label(main_frame,
                                 text="Medula Üzerinde Akıllı Reçete Kontrolü",
                                 font=('Arial', 12),
                                 bg='#f8f9fa', fg='#6c757d')
        subtitle_label.pack(pady=(0, 50))
        
        # Buton frame
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(expand=True)
        
        # OVAL BUTONLAR - TAM ESIT BOYUTLAR
        oval_btn_style = {
            'font': ('Arial', 13, 'bold'),
            'height': 3,
            'width': 30,
            'relief': 'solid',
            'bd': 0,
            'cursor': 'hand2',
            'highlightthickness': 0
        }
        
        # Ilk Ayarlar butonu - OVAL SOFT MAVI
        settings_btn = tk.Button(button_frame,
                                text="ILK AYARLAR",
                                bg='#74b9ff', fg='white',
                                activebackground='#0984e3',
                                command=self.open_settings_window,
                                **oval_btn_style)
        settings_btn.pack(pady=12)
        
        # Medulaya Giris butonu - OVAL SOFT YESIL (AYNI BOYUT)
        medula_btn = tk.Button(button_frame,
                              text="MEDULAYA GIRIS YAP", 
                              bg='#00b894', fg='white',
                              activebackground='#00a085',
                              command=self.open_medula_overlay,
                              **oval_btn_style)
        medula_btn.pack(pady=12)
        
        # Cikis butonu - OVAL SOFT KIRMIZI
        exit_btn = tk.Button(button_frame,
                            text="CIKIS",
                            bg='#fd79a8', fg='white',
                            activebackground='#e84393',
                            command=self.root.quit,
                            **oval_btn_style)
        exit_btn.pack(pady=(25, 0))
        
        # OVAL EFEKTI ICIN - Rounded corners simulation
        def make_oval(button):
            # Button'a oval görünüm için bind events
            def on_enter(e):
                e.widget.config(relief='raised', bd=2)
            def on_leave(e):
                e.widget.config(relief='solid', bd=0)
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        # Tum butonlara oval efekti uygula
        make_oval(settings_btn)
        make_oval(medula_btn)
        make_oval(exit_btn)
        
        self.root.mainloop()

    def open_settings_window(self):
        """Ilk Ayarlar penceresini ac"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ilk Ayarlar")
        settings_window.geometry("700x500")
        settings_window.configure(bg='#f8f9fa')
        settings_window.transient(self.root)  # Ana pencerenin uzerine
        settings_window.grab_set()  # Modal
        
        # Ana frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Baslik
        title_label = ttk.Label(main_frame, text="ILK AYARLAR", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Ayarlar bolumu
        settings_frame = ttk.LabelFrame(main_frame, text="SISTEM AYARLARI", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Medula ayarlari - BOS BASLA
        ttk.Label(settings_frame, text="Medula Kullanici Adi:").pack(anchor=tk.W)
        self.medula_username_entry = ttk.Entry(settings_frame, width=50, font=('Arial', 11))
        self.medula_username_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(settings_frame, text="Medula Sifre:").pack(anchor=tk.W)
        self.medula_password_entry = ttk.Entry(settings_frame, width=50, show="*", font=('Arial', 11))
        self.medula_password_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(settings_frame, text="Claude API Key:").pack(anchor=tk.W)
        self.api_key_entry = ttk.Entry(settings_frame, width=50, show="*", font=('Arial', 11))
        self.api_key_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Navigasyon modu secimi
        nav_frame = ttk.LabelFrame(settings_frame, text="Navigasyon Modu", padding="10")
        nav_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.nav_mode = tk.StringVar(value="manuel")
        ttk.Radiobutton(nav_frame, text="Manuel Navigasyon (Sen kontrol edersin)", 
                       variable=self.nav_mode, value="manuel").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(nav_frame, text="Otomatik Pilot (Sistem kendi gezinir)", 
                       variable=self.nav_mode, value="otomatik").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(nav_frame, text="Hibrit Mod (Manuel + Otomatik)", 
                       variable=self.nav_mode, value="hibrit").pack(anchor=tk.W, pady=2)
        
        # BUTONLAR - TIKLANABILIR KALIN BUTONLAR (GORUNUR)
        buttons_container = tk.Frame(main_frame, bg='#f8f9fa')
        buttons_container.pack(fill=tk.X, pady=(30, 20))
        
        # EXTRA KALIN VE BUYUK BUTONLAR
        button_style = {
            'font': ('Arial', 14, 'bold'),
            'height': 3,
            'width': 12,
            'relief': 'raised',
            'bd': 4,
            'cursor': 'hand2'
        }
        
        # Sol grup - Kaydet ve Iptal
        left_group = tk.Frame(buttons_container, bg='#f8f9fa')
        left_group.pack(side=tk.LEFT, padx=20)
        
        # KAYDET butonu - YESIL
        save_btn = tk.Button(left_group,
                            text="KAYDET",
                            bg='#27ae60', fg='white',
                            activebackground='#229954',
                            command=lambda: self.save_settings(settings_window),
                            **button_style)
        save_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # IPTAL butonu - MAVI
        cancel_btn = tk.Button(left_group,
                              text="IPTAL",
                              bg='#3498db', fg='white', 
                              activebackground='#2980b9',
                              command=settings_window.destroy,
                              **button_style)
        cancel_btn.pack(side=tk.LEFT)
        
        # Sag grup - Cikis
        right_group = tk.Frame(buttons_container, bg='#f8f9fa')
        right_group.pack(side=tk.RIGHT, padx=20)
        
        # CIKIS butonu - KIRMIZI (sag tarafta)
        exit_btn = tk.Button(right_group,
                            text="CIKIS",
                            bg='#e74c3c', fg='white',
                            activebackground='#c0392b',
                            command=lambda: [settings_window.destroy(), self.root.quit()],
                            **button_style)
        exit_btn.pack(side=tk.RIGHT)
        
        # Butonlara hover efekti ekle
        def add_hover_effect(button):
            def on_enter(e):
                e.widget.config(relief='raised', bd=6)  # Daha kalin
            def on_leave(e):
                e.widget.config(relief='raised', bd=4)  # Normal kalinlik
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        add_hover_effect(save_btn)
        add_hover_effect(cancel_btn) 
        add_hover_effect(exit_btn)
        
        # Mevcut ayarlari yukle
        self.load_current_settings()

    def save_settings(self, settings_window=None):
        """Ayarlari kaydetme"""
        try:
            settings_data = {
                'MEDULA_USERNAME': self.medula_username_entry.get(),
                'MEDULA_PASSWORD': self.medula_password_entry.get(),  
                'CLAUDE_API_KEY': self.api_key_entry.get(),
                'NAVIGATION_MODE': self.nav_mode.get()
            }
            
            # .env dosyasini guncelle
            env_path = '.env'
            env_content = []
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_content = f.readlines()
            
            # Mevcut ayarlari guncelle veya ekle
            updated_keys = set()
            for i, line in enumerate(env_content):
                for key, value in settings_data.items():
                    if line.startswith(f'{key}='):
                        env_content[i] = f'{key}={value}\n'
                        updated_keys.add(key)
                        break
            
            # Yeni ayarlari ekle
            for key, value in settings_data.items():
                if key not in updated_keys:
                    env_content.append(f'{key}={value}\n')
            
            # Dosyayi yaz
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_content)
            
            messagebox.showinfo("Basarili", "Ayarlar kaydedildi!")
            print("Ayarlar .env dosyasina kaydedildi")
            
            # Ayarlar penceresini kapat
            if settings_window:
                settings_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar kaydetme hatasi: {e}")
            print(f"Ayar kaydetme hatasi: {e}")

    def load_current_settings(self):
        """Mevcut ayarlari yukleme"""
        try:
            env_path = '.env'
            
            # Once DOGRU default degerleri yukle
            if hasattr(self, 'medula_username_entry'):
                self.medula_username_entry.insert(0, "18342920")
            if hasattr(self, 'medula_password_entry'):
                self.medula_password_entry.insert(0, "571T03s0")
            if hasattr(self, 'api_key_entry'):
                self.api_key_entry.insert(0, "sk-ant-api03-your-claude-api-key-here")
            
            # .env dosyasi varsa override et
            if os.path.exists(env_path):
                # Mevcut degerleri temizle
                if hasattr(self, 'medula_username_entry'):
                    self.medula_username_entry.delete(0, tk.END)
                if hasattr(self, 'medula_password_entry'):
                    self.medula_password_entry.delete(0, tk.END)
                if hasattr(self, 'api_key_entry'):
                    self.api_key_entry.delete(0, tk.END)
                
                # Kaydedilmis degerleri yukle
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'MEDULA_USERNAME' and hasattr(self, 'medula_username_entry'):
                                self.medula_username_entry.insert(0, value)
                            elif key == 'MEDULA_PASSWORD' and hasattr(self, 'medula_password_entry'):
                                self.medula_password_entry.insert(0, value)
                            elif key == 'CLAUDE_API_KEY' and hasattr(self, 'api_key_entry'):
                                self.api_key_entry.insert(0, value)
                            elif key == 'NAVIGATION_MODE' and hasattr(self, 'nav_mode'):
                                self.nav_mode.set(value)
                print("Kaydedilmis ayarlar yuklendi (.env dosyasindan)")
            else:
                print("Default ayarlar yuklendi")
                
        except Exception as e:
            print(f"Ayar yukleme uyarisi: {e}")

    def validate_settings(self):
        """Ayar validasyonu - .env dosyasindan kontrol et"""
        try:
            # .env dosyasindan ayarlari oku
            env_path = '.env'
            settings = {}
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            settings[key] = value.strip()
            
            username = settings.get('MEDULA_USERNAME', '').strip()
            password = settings.get('MEDULA_PASSWORD', '').strip()
            api_key = settings.get('CLAUDE_API_KEY', '').strip()
            
            if not username or not password:
                messagebox.showwarning("Eksik Bilgi", 
                                     "Medula kullanici adi ve sifre gerekli!\n" +
                                     "Lutfen once 'ILK AYARLAR' butonuna basin.")
                return False
                
            if not api_key:
                messagebox.showwarning("Eksik Bilgi", 
                                     "Claude API anahtari gerekli!\n" +
                                     "Lutfen once 'ILK AYARLAR' butonuna basin.")
                return False
                
            return True
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar kontrol hatasi: {e}")
            return False

    def open_medula_overlay(self):
        """Medula Overlay sistemini baslat"""
        if not self.validate_settings():
            return
            
        try:
            # Ana pencereyi gizle
            self.root.withdraw()
            
            # Overlay window baslat
            self.create_overlay_window()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Medula acma hatasi: {e}")
            self.root.deiconify()

    def create_overlay_window(self):
        """Overlay penceresi olusturma"""
        try:
            # Overlay ana penceresi - TAM EKRAN
            overlay_root = tk.Toplevel()
            overlay_root.title("Reçete Kontrol Çerçevesi - Medula Overlay")
            
            # Tam ekran modunu etkinlestir
            overlay_root.attributes('-fullscreen', True)
            overlay_root.state('zoomed')  # Windows icin maximize
            overlay_root.configure(bg='#2c3e50')
            
            # ESC ile tam ekrandan cikis
            def toggle_fullscreen(event=None):
                current = overlay_root.attributes('-fullscreen')
                overlay_root.attributes('-fullscreen', not current)
                
            def exit_fullscreen(event=None):
                overlay_root.attributes('-fullscreen', False)
                
            overlay_root.bind('<Escape>', exit_fullscreen)
            overlay_root.bind('<F11>', toggle_fullscreen)
            
            # Ust kontrol paneli
            control_panel = tk.Frame(overlay_root, bg='#34495e', height=80)
            control_panel.pack(fill=tk.X, padx=5, pady=5)
            control_panel.pack_propagate(False)
            
            # Ana baslik
            title_label = tk.Label(control_panel, 
                                 text="REÇETE KONTROL ÇERÇEVESİ", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#34495e', fg='white')
            title_label.pack(side=tk.LEFT, padx=20, pady=25)
            
            # Navigasyon butonlari
            nav_frame = tk.Frame(control_panel, bg='#34495e')
            nav_frame.pack(side=tk.RIGHT, padx=20, pady=20)
            
            # Ana kontrol butonlari
            self.create_dynamic_buttons(nav_frame)
            
            # Medula embed alani
            medula_frame = tk.Frame(overlay_root, bg='white', relief=tk.RAISED, bd=2)
            medula_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # WebView entegrasyonu icin placeholder
            medula_label = tk.Label(medula_frame, 
                                  text="MEDULA SISTEMI YUKLENIYOR...\n\n" + 
                                       "Browser entegrasyonu hazirlaniyor\n" +
                                       "Cerceve sistemi aktif\n\n" +
                                       "Gercek implementasyon: WebView2/CEF ile yapilacak",
                                  font=('Arial', 12),
                                  bg='white', fg='#666')
            medula_label.pack(expand=True)
            
            # Alt durum cubugu
            status_frame = tk.Frame(overlay_root, bg='#95a5a6', height=30)
            status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
            status_frame.pack_propagate(False)
            
            self.status_label = tk.Label(status_frame,
                                       text="Sistem Hazir | 0 Kontrolsuz | 0 Uygun | 0 Uygun Degil",
                                       bg='#95a5a6', fg='white', font=('Arial', 10))
            self.status_label.pack(pady=5)
            
            # Pencere kapatma olayi
            overlay_root.protocol("WM_DELETE_WINDOW", self.close_overlay)
            
            print("Overlay penceresi olusturuldu")
            
        except Exception as e:
            print(f"Overlay olusturma hatasi: {e}")
            self.root.deiconify()

    def create_dynamic_buttons(self, parent):
        """Sayfa tipine gore dinamik butonlar"""
        # Genel kontrol butonlari
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'height': 1,
            'width': 15
        }
        
        # Ana kontrol butonlari
        tk.Button(parent, text="⬅️ GERI", bg='#95a5a6', fg='white', 
                 command=self.go_back, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="🔄 YENILE", bg='#3498db', fg='white', 
                 command=self.refresh_page, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="🏠 ANA SAYFA", bg='#9b59b6', fg='white',
                 command=self.go_home, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="📋 LISTE", bg='#e67e22', fg='white',
                 command=self.go_prescription_list, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Button(parent, text="❌ KAPAT", bg='#e74c3c', fg='white',
                 command=self.close_overlay, **btn_style).pack(side=tk.LEFT, padx=2)
        
        # Dinamik butonlar (sayfa algilamasina gore degisecek)
        self.dynamic_button_frame = tk.Frame(parent, bg='#34495e')
        self.dynamic_button_frame.pack(side=tk.LEFT, padx=20)
        
        # Test butonlari ekle
        self.update_dynamic_buttons("prescription_detail")

    def update_dynamic_buttons(self, page_type: str):
        """Sayfa tipine gore butonlari guncelle"""
        # Mevcut dinamik butonlari temizle
        for widget in self.dynamic_button_frame.winfo_children():
            widget.destroy()
        
        btn_style = {
            'font': ('Arial', 9, 'bold'),
            'height': 1,
            'width': 20
        }
        
        if page_type == "prescription_detail":
            # TEK RECETE KONTROL
            tk.Button(self.dynamic_button_frame, 
                     text="BU RECETEYI KONTROL ET",
                     bg='#e74c3c', fg='white',
                     command=self.control_single_prescription,
                     **btn_style).pack(side=tk.LEFT, padx=2)
                     
        elif page_type == "daily_list":
            # GUNLUK TOPLU KONTROL
            tk.Button(self.dynamic_button_frame,
                     text="TUM GUNLUKLERI KONTROL ET", 
                     bg='#27ae60', fg='white',
                     command=self.control_daily_prescriptions,
                     **btn_style).pack(side=tk.LEFT, padx=2)
                     
        elif page_type == "monthly_list":
            # AYLIK TOPLU KONTROL
            tk.Button(self.dynamic_button_frame,
                     text="TUM AYLIGI KONTROL ET",
                     bg='#2980b9', fg='white', 
                     command=self.control_monthly_prescriptions,
                     **btn_style).pack(side=tk.LEFT, padx=2)

    def control_single_prescription(self):
        """TEK RECETE KONTROL ALGORITMASI"""
        try:
            print("Tek recete kontrolu basliyor...")
            
            # Mock data
            mock_prescription = {
                "recete_no": "3GP25RF",
                "hasta_tc": "11916110202", 
                "hasta_ad_soyad": "YALÇIN DURDAGI",
                "drugs": [{"ilac_adi": "PANTO 40 MG", "adet": "3"}]
            }
            
            # Analiz sonucu
            result = self.mock_analysis(mock_prescription)
            
            # Bayrak guncelleme
            self.update_prescription_flag("3GP25RF", result['status'])
            
            # Durum guncelleme
            self.update_status_bar()
            
            print(f"Recete kontrolu tamamlandi: {result['status']}")
            
        except Exception as e:
            print(f"Tek recete kontrol hatasi: {e}")

    def control_daily_prescriptions(self):
        """GUNLUK TOPLU KONTROL ALGORITMASI"""
        try:
            print("Gunluk toplu kontrol basliyor...")
            
            # Kontrol sirasi: C -> A -> Gecici Koruma -> B -> C-Kan
            control_order = ['C', 'A', 'Gecici_Koruma', 'B', 'C_Kan']
            
            for group in control_order:
                print(f"{group} grubu kontrolu...")
                self.process_group_prescriptions(group, "daily")
                time.sleep(1)
            
            print("Gunluk toplu kontrol tamamlandi")
            self.update_status_bar()
            
        except Exception as e:
            print(f"Gunluk kontrol hatasi: {e}")

    def control_monthly_prescriptions(self):
        """AYLIK TOPLU KONTROL ALGORITMASI"""
        try:
            print("Aylik toplu kontrol basliyor...")
            
            control_order = ['C', 'A', 'Gecici_Koruma', 'B', 'C_Kan']
            
            for group in control_order:
                print(f"{group} grubu aylik kontrolu...")
                self.process_group_prescriptions(group, "monthly")
                time.sleep(2)
            
            print("Aylik toplu kontrol tamamlandi")
            self.update_status_bar()
            
        except Exception as e:
            print(f"Aylik kontrol hatasi: {e}")

    def process_group_prescriptions(self, group: str, period: str):
        """Grup bazli recete isleme"""
        prescription_count = {"C": 5, "A": 8, "B": 15, "Gecici_Koruma": 3, "C_Kan": 2}
        count = prescription_count.get(group, 5)
        
        for i in range(count):
            mock_rx = {"recete_no": f"{group}_{period}_{i+1}"}
            result = self.mock_analysis(mock_rx)
            print(f"  {mock_rx['recete_no']}: {result['status']}")

    def mock_analysis(self, prescription_data: dict) -> dict:
        """Mock analiz sonucu"""
        import random
        statuses = ['uygun', 'uygun_degil', 'supheli', 'ek_kontrol']
        weights = [0.4, 0.2, 0.3, 0.1]
        
        status = random.choices(statuses, weights=weights)[0]
        
        return {
            'status': status,
            'confidence': random.uniform(0.7, 0.95),
            'analysis_time': random.uniform(2, 5)
        }

    def update_prescription_flag(self, prescription_no: str, status: str):
        """Recete bayragini guncelleme"""
        print(f"Bayrak guncellendi: {prescription_no} -> {status}")

    def update_status_bar(self):
        """Durum cubugunu guncelleme"""
        counts = {"kontrolsuz": 12, "uygun": 8, "uygun_degil": 3, "supheli": 2, "ek_kontrol": 1}
        
        status_text = f"Sistem Aktif | " + \
                     f"{counts['kontrolsuz']} Kontrolsuz | " + \
                     f"{counts['uygun']} Uygun | " + \
                     f"{counts['uygun_degil']} Uygun Degil"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)

    def go_back(self):
        """Geri git"""
        print("Geri gidiliyor...")
        # Gerçek implementasyonda browser history'den geri gidecek
    
    def refresh_page(self):
        """Sayfayi yenileme"""
        print("Sayfa yenileniyor...")

    def go_home(self):
        """Ana sayfaya git"""
        print("Ana sayfaya gidiliyor...")
        self.update_dynamic_buttons("home")

    def go_prescription_list(self):
        """Recete listesine git"""  
        print("Recete listesine gidiliyor...")
        self.update_dynamic_buttons("daily_list")

    def close_overlay(self):
        """Overlay'i kapat ve ana panele don"""
        print("Overlay sistemi kapatiliyor...")
        self.root.deiconify()

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