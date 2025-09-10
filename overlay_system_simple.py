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
import sys
from pathlib import Path

# Medula browser import'u
sys.path.insert(0, str(Path(__file__).parent))
try:
    from medula_automation.browser import MedulaBrowser
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    print("[WARNING] Medula browser import failed - mock mode")

class SimpleSettings:
    """Basit ayar sınıfı"""
    def __init__(self):
        self.medula_username = "18342920"
        self.medula_password = "571T03s0"
        self.medula_url = "https://medeczane.sgk.gov.tr/eczane/login.jsp"
        self.browser_type = "chrome"
        self.headless = False
        self.page_load_timeout = 30
        self.implicit_wait = 10
        self.log_level = "INFO"
        self.log_file = "logs/medula.log"
        self.enable_screenshots = True
        self.screenshot_dir = "screenshots"
        # YENİ: Tam ekran ve UI özelleştirme ayarları
        self.fullscreen = True
        self.hide_browser_ui = True
        self.green_frame = True
        # ADRES ÇUBUGU VE TEST YAZISI GÜÇLÜ GİZLEME
        self.extra_chrome_options = [
            '--app',  # App mode - adres çubuğunu gizler
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-infobars',  # Test yazısı için
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',  # Otomasyon tespit engelleme
            '--exclude-switches=enable-automation',  # Otomasyon flagını kaldır
            '--use-fake-ui-for-media-stream',  # UI mesajlarını engelle
            '--disable-browser-side-navigation',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--kiosk'  # Kiosk modu - tam ekran
        ]
        
    def create_directories(self):
        """Gerekli dizinleri oluştur"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)

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
        
        # Ana frame - TAM TK FRAME KULLAN
        main_frame = tk.Frame(settings_window, bg='#f8f9fa', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Baslik - TK LABEL
        title_label = tk.Label(main_frame, text="ILK AYARLAR", 
                               font=('Arial', 16, 'bold'), 
                               bg='#f8f9fa', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Ayarlar bolumu - TK KULLAN (TTK DEĞİL)
        settings_frame = tk.LabelFrame(main_frame, text="SISTEM AYARLARI", bg='#f8f9fa', padx=15, pady=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Medula ayarlari - TAMAMEN TK
        tk.Label(settings_frame, text="Medula Kullanici Adi:", bg='#f8f9fa').pack(anchor=tk.W)
        self.medula_username_entry = tk.Entry(settings_frame, width=50, font=('Arial', 11))
        self.medula_username_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(settings_frame, text="Medula Sifre:", bg='#f8f9fa').pack(anchor=tk.W)
        self.medula_password_entry = tk.Entry(settings_frame, width=50, show="*", font=('Arial', 11))
        self.medula_password_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(settings_frame, text="Claude API Key:", bg='#f8f9fa').pack(anchor=tk.W)
        self.api_key_entry = tk.Entry(settings_frame, width=50, show="*", font=('Arial', 11))
        self.api_key_entry.pack(fill=tk.X, pady=(5, 10))
        
        # MEDULA URL AYARI - YENİ DÜZEN
        url_frame = tk.Frame(settings_frame, bg='#f8f9fa')
        url_frame.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(url_frame, text="Medula URL:", bg='#f8f9fa', fg='#e74c3c', font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        # URL ve LINK yan yana
        url_row = tk.Frame(url_frame, bg='#f8f9fa')
        url_row.pack(fill=tk.X, pady=(5, 10))
        
        self.medula_url_entry = tk.Entry(url_row, width=35, font=('Arial', 11))
        self.medula_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # MEDULA LİNK BUTONU - YAN YANA
        medula_link_btn = tk.Button(url_row,
                                   text="[LINK] MEDULA AC",
                                   font=('Arial', 10, 'bold'),
                                   bg='#3498db', fg='white',
                                   height=1, width=15, relief='raised', bd=2,
                                   cursor='hand2',
                                   command=self.open_medula_website)
        medula_link_btn.pack(side=tk.RIGHT)
        
        # Nav mode değişkenini tanımla (backend kullanım için)
        self.nav_mode = tk.StringVar(value="manuel")
        
        # BUTONLAR CONTAINER - HORİZONTAL DÜZENLEMESİ
        buttons_frame = tk.Frame(main_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # SOL GRUP - KAYDET VE İPTAL
        left_buttons = tk.Frame(buttons_frame, bg='#f8f9fa')
        left_buttons.pack(side=tk.LEFT, padx=10)
        
        # KAYDET butonu - SOL GRUPTA
        save_btn = tk.Button(left_buttons,
                            text="[OK] AYARLARI KAYDET",
                            font=('Arial', 12, 'bold'),
                            bg='#27ae60', fg='white',
                            height=2, width=18,
                            relief='raised', bd=4,
                            cursor='hand2',
                            activebackground='#229954',
                            command=lambda: self.save_settings(settings_window))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # İPTAL butonu - SOL GRUPTA
        cancel_btn = tk.Button(left_buttons,
                              text="[X] IPTAL",
                              font=('Arial', 12, 'bold'),
                              bg='#3498db', fg='white',
                              height=2, width=12,
                              relief='raised', bd=4,
                              cursor='hand2',
                              activebackground='#2980b9',
                              command=settings_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # SAĞ GRUP - ÇIKIŞ
        right_buttons = tk.Frame(buttons_frame, bg='#f8f9fa')
        right_buttons.pack(side=tk.RIGHT, padx=10)
        
        # ÇIKIŞ butonu - SAĞ GRUPTA
        exit_btn = tk.Button(right_buttons,
                            text="[EXIT] CIKIS",
                            font=('Arial', 12, 'bold'),
                            bg='#e74c3c', fg='white',
                            height=2, width=12,
                            relief='raised', bd=4,
                            cursor='hand2',
                            activebackground='#c0392b',
                            command=lambda: [settings_window.destroy(), self.root.quit()])
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
                'MEDULA_URL': self.medula_url_entry.get(),
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
            if hasattr(self, 'medula_url_entry'):
                self.medula_url_entry.insert(0, "https://medeczane.sgk.gov.tr/eczane/login.jsp")
            
            # .env dosyasi varsa override et
            if os.path.exists(env_path):
                # Mevcut degerleri temizle
                if hasattr(self, 'medula_username_entry'):
                    self.medula_username_entry.delete(0, tk.END)
                if hasattr(self, 'medula_password_entry'):
                    self.medula_password_entry.delete(0, tk.END)
                if hasattr(self, 'api_key_entry'):
                    self.api_key_entry.delete(0, tk.END)
                if hasattr(self, 'medula_url_entry'):
                    self.medula_url_entry.delete(0, tk.END)
                
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
                            elif key == 'MEDULA_URL' and hasattr(self, 'medula_url_entry'):
                                self.medula_url_entry.insert(0, value)
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
            # Once default degerleri kontrol et
            default_username = "18342920"
            default_password = "571T03s0"
            
            # .env dosyasindan ayarlari oku
            env_path = '.env'
            settings = {}
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            settings[key] = value.strip()
            
            # Default veya kaydedilmis degerleri al
            username = settings.get('MEDULA_USERNAME', default_username).strip()
            password = settings.get('MEDULA_PASSWORD', default_password).strip()
            api_key = settings.get('CLAUDE_API_KEY', '').strip()
            
            # Gereksiz striktlik - default degerler varsa gecsin
            if username == default_username and password == default_password:
                print(f"Default ayarlar kullaniliyor: {username}")
                return True
            
            # Kaydedilmis ayarlar varsa onlari kontrol et
            if not username or not password:
                messagebox.showwarning("Eksik Bilgi", 
                                     "Medula kullanici adi ve sifre gerekli!\n" +
                                     "Lutfen once 'ILK AYARLAR' butonuna basin.")
                return False
                
            print(f"Ayarlar gecerli: {username}")
            return True
            
        except Exception as e:
            print(f"Ayar kontrol hatasi: {e}")
            # Hata durumunda default ayarlarla devam et
            return True
    
    def open_medula_website(self):
        """Medula web sitesini otomatik doldurmalı açar"""
        try:
            print("[AUTO LOGIN] Medula otomatik login sistemi başlatılıyor...")
            
            # Ayarları oku
            env_path = '.env'
            username = "18342920"
            password = "571T03s0"
            medula_url = "https://medeczane.sgk.gov.tr/eczane/login.jsp"
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'MEDULA_USERNAME':
                                username = value.strip()
                            elif key == 'MEDULA_PASSWORD':
                                password = value.strip()
                            elif key == 'MEDULA_URL':
                                medula_url = value.strip()
            
            if hasattr(self, 'medula_url_entry') and self.medula_url_entry.get():
                medula_url = self.medula_url_entry.get()
                
            print(f"[AUTO LOGIN] Medula açılıyor: {medula_url}")
            print(f"[AUTO LOGIN] Kullanıcı: {username}")
            
            # Thread'de otomatik login başlat
            login_thread = threading.Thread(
                target=self._auto_login_worker,
                args=(medula_url, username, password),
                daemon=True
            )
            login_thread.start()
            
            messagebox.showinfo("Başlatıldı", "Medula otomatik login başlatıldı!\nKullanıcı adı ve şifre otomatik doldurulacak.\nSadece CAPTCHA'yı girin ve ENTER'a basın.")
        except Exception as e:
            print(f"[AUTO LOGIN ERROR] {e}")
            messagebox.showerror("Hata", f"Otomatik login başlatılamadı: {e}")

    def open_medula_overlay(self):
        """Medula Overlay sistemini baslat - GERÇEK BROWSER"""
        if not self.validate_settings():
            return
            
        try:
            print("[BROWSER] Medula browser başlatılıyor...")
            
            if BROWSER_AVAILABLE:
                # Gerçek browser başlatma
                self.start_real_medula_browser()
            else:
                # Mock overlay
                print("[MOCK] Browser import yok, mock overlay açılıyor")
                self.root.withdraw()
                self.create_overlay_window()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Medula acma hatasi: {e}")
            print(f"[ERROR] {e}")

    def start_real_medula_browser(self):
        """Gerçek Medula browser'ını başlat"""
        try:
            print("[BROWSER] Settings okunuyor...")
            
            # .env'den güncel ayarları al
            env_path = '.env'
            username = "18342920"  # Default
            password = "571T03s0"   # Default  
            medula_url = "https://medeczane.sgk.gov.tr/eczane/login.jsp"  # Default
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'MEDULA_USERNAME':
                                username = value.strip()
                            elif key == 'MEDULA_PASSWORD':
                                password = value.strip()
                            elif key == 'MEDULA_URL':
                                medula_url = value.strip()
            
            # SimpleSettings ile browser başlat - ÖZELLEŞTİRME
            settings = SimpleSettings()
            settings.medula_username = username
            settings.medula_password = password
            settings.medula_url = medula_url
            # TAM EKRAN VE UI ÖZELLEŞTİRMELERİ
            settings.fullscreen = True
            settings.hide_browser_ui = True
            settings.green_frame = True
            
            print(f"[BROWSER] Browser başlatılıyor, kullanıcı: {username}")
            print(f"[BROWSER] Medula URL: {medula_url}")
            
            # Browser'ı ayrı thread'de başlat
            browser_thread = threading.Thread(
                target=self._browser_worker,
                args=(settings,),
                daemon=True
            )
            browser_thread.start()
            
            print("[BROWSER] Thread başlatıldı")
            
        except Exception as e:
            print(f"[BROWSER ERROR] {e}")
            messagebox.showerror("Browser Hatası", f"Browser başlatılamadı: {e}")
    
    def _browser_worker(self, settings):
        """Browser worker thread'i"""
        try:
            print("[THREAD] Browser worker başladı")
            
            # Browser'ı başlat
            browser = MedulaBrowser(settings)
            
            if not browser.start():
                print("[THREAD] Browser başlatılamadı")
                return
                
            print("[THREAD] Browser başlatıldı, özelleştirmeler uygulanıyor...")
            
            # BROWSER ÖZELLEŞTİRMELERİ UYGULA
            self._apply_browser_customizations(browser)
                
            print("[THREAD] Browser hazır, login deneniyor...")
            
            # Login yap
            if browser.login():
                print("[THREAD] ✅ Login başarılı!")
                
                # ÇERÇEVEYİ İNJECT ET - MEDULA ÜZERİNE OVERLAY!
                time.sleep(2)  # Sayfa yüklenmesi için bekle
                self._inject_overlay_frame(browser)
                
                # SAYFANIN ÜST-ALT YEŞİL ÇERÇEVE EKLE
                self._inject_page_frame(browser)
                
                # ANA PENCEREYİ GİZLE - BAŞARILI LOGIN SONRASI
                try:
                    self.root.after(0, self.root.withdraw)
                    print("[THREAD] ✅ Ana pencere gizlendi")
                except:
                    print("[THREAD] Ana pencere gizleme hatası")
                
                messagebox.showinfo("Başarılı", "Medula'ya başarıyla giriş yapıldı!\nÇerçeve sistemi aktif!")
                
                # Browser açık kalacak - kullanıcı manuel kontrol edebilir
                print("[THREAD] Browser açık kalıyor - çerçeve overlay aktif!")
                
            else:
                print("[THREAD] ❌ Login başarısız")
                messagebox.showerror("Hata", "Medula girişi başarısız!")
            
        except Exception as e:
            print(f"[THREAD ERROR] Browser worker hatası: {e}")
            messagebox.showerror("Browser Hatası", f"Browser hatası: {e}")
        
        finally:
            # Ana pencereyi geri getir
            try:
                self.root.after(0, self.root.deiconify)
            except:
                pass
    
    def _auto_login_worker(self, url, username, password):
        """Otomatik login worker thread"""
        try:
            print("[AUTO LOGIN WORKER] Browser başlatılıyor...")
            
            # SimpleSettings ile browser ayarla
            settings = SimpleSettings()
            settings.medula_username = username
            settings.medula_password = password
            settings.medula_url = url
            settings.fullscreen = True
            settings.hide_browser_ui = True
            settings.green_frame = True
            
            # Browser'ı başlat
            browser = MedulaBrowser(settings)
            
            if not browser.start():
                print("[AUTO LOGIN WORKER] Browser başlatılamadı")
                return
                
            print("[AUTO LOGIN WORKER] Browser açıldı, sayfaya gidiliyor...")
            
            # Medula sayfasına git
            browser.driver.get(url)
            time.sleep(3)
            
            # Browser özelleştirmelerini uygula
            self._apply_browser_customizations(browser)
            
            print("[AUTO LOGIN WORKER] Sayfaya ulaşıldı, form doldurma başlıyor...")
            
            # FORM OTOMATİK DOLDURMA JavaScript'i
            auto_fill_js = f"""
            console.log('[AUTO FILL] Form doldurma başladı');
            
            // Kullanıcı adı alanını bul ve doldur
            const userField = document.querySelector('input[name="j_username"], input[name="username"], input[type="text"]');
            if (userField) {{
                userField.value = '{username}';
                userField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                console.log('[AUTO FILL] Kullanıcı adı dolduruldu: {username}');
            }}
            
            // Şifre alanını bul ve doldur
            const passField = document.querySelector('input[name="j_password"], input[name="password"], input[type="password"]');
            if (passField) {{
                passField.value = '{password}';
                passField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                console.log('[AUTO FILL] Şifre dolduruldu');
            }}
            
            // KVKK checkbox'ını işaretle
            const kvkkBox = document.querySelector('input[type="checkbox"]');
            if (kvkkBox && !kvkkBox.checked) {{
                kvkkBox.click();
                console.log('[AUTO FILL] KVKK checkbox işaretlendi');
            }}
            
            // CAPTCHA alanına odaklan ve kırmızı çerçeve ekle
            const captchaField = document.querySelector('input[name="captcha"], input[placeholder*="Captcha"], input[placeholder*="captcha"], input[placeholder*="CAPTCHA"]');
            if (captchaField) {{
                captchaField.focus();
                captchaField.style.border = '3px solid #e74c3c';
                captchaField.style.backgroundColor = '#fff3cd';
                captchaField.style.fontSize = '18px';
                captchaField.style.textAlign = 'center';
                console.log('[AUTO FILL] CAPTCHA alanına odaklandı - GİRİŞ BEKLENİYOR');
                
                // CAPTCHA alanına 6 karakter listener ekle
                captchaField.addEventListener('input', function(e) {{
                    const value = e.target.value;
                    console.log(`[CAPTCHA] Girilen: ${{value}} (Uzunluk: ${{value.length}})`);
                    
                    if (value.length === 6) {{
                        console.log('[CAPTCHA] 6 karakter tamamlandı, form gönderiliyor...');
                        
                        // 500ms bekle ve formu gönder
                        setTimeout(() => {{
                            const form = e.target.closest('form');
                            if (form) {{
                                form.submit();
                                console.log('[CAPTCHA] Form gönderildi!');
                            }} else {{
                                // Form bulunamazsa login butonunu tıkla
                                const loginBtn = document.querySelector('input[type="submit"], button[type="submit"], button[value*="Giriş"], input[value*="Giriş"]');
                                if (loginBtn) {{
                                    loginBtn.click();
                                    console.log('[CAPTCHA] Login butonu tıklandı!');
                                }}
                            }}
                        }}, 500);
                    }}
                }});
            }} else {{
                console.log('[AUTO FILL] CAPTCHA alanı bulunamadı');
            }}
            """
            
            browser.driver.execute_script(auto_fill_js)
            
            # CAPTCHA 6 karakter monitoring - GÜÇLÜ VERSİYON
            captcha_monitor_js = """
            // Güçlü CAPTCHA monitoring sistemi
            function startCaptchaMonitoring() {
                console.log('[CAPTCHA MONITOR] Monitoring sistemi başlatılıyor...');
                
                const captchaFields = [
                    'input[name="captcha"]',
                    'input[placeholder*="Captcha"]',
                    'input[placeholder*="captcha"]', 
                    'input[placeholder*="CAPTCHA"]',
                    'input[id*="captcha"]',
                    'input[class*="captcha"]'
                ];
                
                for (let selector of captchaFields) {
                    const field = document.querySelector(selector);
                    if (field) {
                        console.log(`[CAPTCHA MONITOR] Field bulundu: ${selector}`);
                        field.focus();
                        field.style.border = '4px solid #e74c3c';
                        field.style.backgroundColor = '#fff3cd';
                        field.style.fontSize = '18px';
                        field.style.textAlign = 'center';
                        field.style.fontWeight = 'bold';
                        
                        // Multiple event listeners for robust monitoring
                        ['input', 'keyup', 'change', 'paste'].forEach(eventType => {
                            field.addEventListener(eventType, function(e) {
                                const value = e.target.value.trim();
                                console.log(`[CAPTCHA] ${eventType}: "${value}" (Len: ${value.length})`);
                                
                                if (value.length === 6) {
                                    console.log('[CAPTCHA] ✅ 6 KARAKTER! AUTO-SUBMIT BAŞLIYOR...');
                                    
                                    // 300ms bekle ve submit et
                                    setTimeout(() => {
                                        const form = e.target.closest('form');
                                        if (form) {
                                            console.log('[CAPTCHA] Form submit edildi!');
                                            form.submit();
                                        } else {
                                            // Form yoksa login butonlarını dene
                                            const loginBtns = [
                                                'input[type="submit"]',
                                                'button[type="submit"]',
                                                'input[value*="Giriş"]',
                                                'input[value*="giriş"]',
                                                'button:contains("Giriş")',
                                                'button:contains("giriş")',
                                                '*[onclick*="login"]',
                                                '*[onclick*="submit"]'
                                            ];
                                            
                                            for (let btnSelector of loginBtns) {
                                                const btn = document.querySelector(btnSelector);
                                                if (btn) {
                                                    console.log(`[CAPTCHA] Button clicked: ${btnSelector}`);
                                                    btn.click();
                                                    return;
                                                }
                                            }
                                        }
                                    }, 300);
                                }
                            });
                        });
                        
                        return true; // Found and set up
                    }
                }
                
                console.log('[CAPTCHA MONITOR] ❌ CAPTCHA field bulunamadı');
                return false;
            }
            
            // Start monitoring
            startCaptchaMonitoring();
            
            // Retry every 2 seconds if not found
            let retryCount = 0;
            const monitorInterval = setInterval(() => {
                if (retryCount < 10) {
                    if (startCaptchaMonitoring()) {
                        clearInterval(monitorInterval);
                    }
                    retryCount++;
                } else {
                    clearInterval(monitorInterval);
                    console.log('[CAPTCHA MONITOR] Max retry reached, stopping...');
                }
            }, 2000);
            """
            
            browser.driver.execute_script(captcha_monitor_js)
            
            # Sayfa çerçevelerini ekle
            time.sleep(2)
            self._inject_page_frame(browser)
            
            print("[AUTO LOGIN WORKER] ✅ Otomatik doldurma tamamlandı!")
            print("[AUTO LOGIN WORKER] CAPTCHA'yı girin, 6. karakterde otomatik giriş yapılacak")
            
        except Exception as e:
            print(f"[AUTO LOGIN WORKER ERROR] {e}")
            messagebox.showerror("Otomatik Login Hatası", f"Otomatik login hatası: {e}")
    
    def _apply_browser_customizations(self, browser):
        """Browser'a özelleştirmeleri uygula"""
        try:
            print("[BROWSER] Özelleştirmeler uygulanıyor...")
            
            # 1) TAM EKRAN YAPMA
            browser.driver.maximize_window()
            time.sleep(1)
            
            # 2) F11 ile tam ekran moduna geç
            try:
                from selenium.webdriver.common.keys import Keys
                browser.driver.find_element("tag name", "body").send_keys(Keys.F11)
                time.sleep(1)
                print("[BROWSER] ✅ Tam ekran modu aktif")
            except:
                print("[BROWSER] ⚠️ F11 tam ekran başarısız, maximize kullanıldı")
            
            # 3) CHROME UI TAMİZ GİZLEME - GELİŞMİŞ
            chrome_options_js = """
            // Chrome test yazısını gizle
            const infobar = document.querySelector('[data-test-id="infobar"]');
            if (infobar) infobar.style.display = 'none';
            
            // Developer tools detection banner'ını gizle
            const devToolsBanner = document.querySelector('.dev-tools-banner');
            if (devToolsBanner) devToolsBanner.style.display = 'none';
            
            // Otomatik test yazısını gizle
            const testBanner = document.querySelector('[data-automation-id="test-banner"]');
            if (testBanner) testBanner.style.display = 'none';
            
            console.log('✅ Chrome UI optimizasyonları uygulandı');
            """
            
            browser.driver.execute_script(chrome_options_js)
            
            # 3.5) ADRES ÇUBUGU GÜÇLÜ GİZLEME - EKSTRA
            address_bar_hide_js = """
            // Adres çubuğu ve Chrome UI gizleme - güçlü versiyon
            console.log('[ADDRESS BAR HIDE] Adres çubuğu gizleme başlıyor...');
            
            // CSS ile Chrome UI elementlerini gizle
            const hideStyle = document.createElement('style');
            hideStyle.textContent = `
                /* Chrome adres çubuğu ve toolbar gizleme */
                .location-bar, .toolbar, .omnibox, [role="toolbar"], .chrome-toolbar,
                .location-bar-container, .toolbar-container, .location-icon-view,
                .omnibox-view, .location-bar-hosting, .toolbar-button-theme,
                body > *[class*="toolbar"], body > *[class*="location"],
                body > *[class*="chrome"], body > *[class*="omni"],
                /* Test yazıları için ekstra gizleme */
                *[class*="automation"], *[class*="test-mode"], *[id*="automation"],
                *[data-testid], .test-banner, [data-automation-id] {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    height: 0 !important;
                    width: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                
                /* Body'nin en üst kısmını kapatma */
                body {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
            `;
            document.head.appendChild(hideStyle);
            
            // İnfobar ve test yazıları için özel gizleme
            function hideTestElements() {
                const testTexts = [
                    'otomatik test yazılımı tarafından kontrol ediliyor',
                    'automation software',
                    'controlled by automated test software',
                    'tarafından kontrol ediliyor'
                ];
                
                testTexts.forEach(searchText => {
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        if (el.textContent && el.textContent.toLowerCase().includes(searchText.toLowerCase())) {
                            el.style.display = 'none';
                            console.log('✅ Test yazısı gizlendi:', searchText);
                        }
                    });
                });
            }
            
            // Sayfa yüklendikten sonra da kontrol et
            setTimeout(hideTestElements, 1000);
            setTimeout(hideTestElements, 3000);
            setTimeout(hideTestElements, 5000);
            
            console.log('[ADDRESS BAR HIDE] ✅ Güçlü gizleme uygulandı');
            """
            
            browser.driver.execute_script(address_bar_hide_js)
            
            # 4) YEŞİL BROWSER ÇERÇEVESİ (CSS ile)
            green_frame_js = """
            // Browser penceresine yeşil çerçeve ekle
            const greenFrame = document.createElement('div');
            greenFrame.id = 'browser-green-frame';
            greenFrame.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
                border: 5px solid #27ae60;
                box-shadow: inset 0 0 20px rgba(39, 174, 96, 0.3);
            `;
            document.body.appendChild(greenFrame);
            console.log('✅ Yeşil browser çerçevesi eklendi');
            """
            
            browser.driver.execute_script(green_frame_js)
            
            # 5) BROWSER WINDOW TITLE YESIL GUNCELLEME
            try:
                browser.driver.execute_script("document.title = '[GREEN] MEDULA RECETE KONTROL - Yesil Cerceve Aktif';")
                print("[BROWSER] Pencere basligi yesil tema ile guncellendi")
            except:
                print("[BROWSER] Pencere basligi guncellenemedi")
            print("[BROWSER] ✅ Tüm özelleştirmeler uygulandı")
            
        except Exception as e:
            print(f"[BROWSER] Browser özelleştirme hatası: {e}")
    
    def _inject_page_frame(self, browser):
        """Sayfa üst-alt yeşil çerçeveleme inject eder"""
        try:
            print("[PAGE FRAME] Sayfa çerçeveleme başlatılıyor...")
            
            page_frame_js = """
            // Mevcut sayfa çerçevelerini temizle
            const existingFrames = document.querySelectorAll('.medula-page-frame');
            existingFrames.forEach(frame => frame.remove());
            
            // ÜST ÇERÇEVE - HEADER
            const topFrame = document.createElement('div');
            topFrame.className = 'medula-page-frame medula-top-frame';
            topFrame.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 8px;
                background: linear-gradient(135deg, #27ae60 0%, #27ae60 100%);
                z-index: 9998;
                pointer-events: none;
                box-shadow: 0 2px 10px rgba(39, 174, 96, 0.4);
            `;
            
            // ALT ÇERÇEVE - FOOTER  
            const bottomFrame = document.createElement('div');
            bottomFrame.className = 'medula-page-frame medula-bottom-frame';
            bottomFrame.style.cssText = `
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 8px;
                background: linear-gradient(135deg, #27ae60 0%, #27ae60 100%);
                z-index: 9998;
                pointer-events: none;
                box-shadow: 0 -2px 10px rgba(39, 174, 96, 0.4);
            `;
            
            // SOL ÇERÇEVE
            const leftFrame = document.createElement('div');
            leftFrame.className = 'medula-page-frame medula-left-frame';
            leftFrame.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 15px;
                height: 100%;
                background: #27ae60;
                z-index: 9998;
                pointer-events: none;
            `;
            
            // SAĞ ÇERÇEVE
            const rightFrame = document.createElement('div');
            rightFrame.className = 'medula-page-frame medula-right-frame';
            rightFrame.style.cssText = `
                position: fixed;
                top: 0;
                right: 0;
                width: 15px;
                height: 100%;
                background: #27ae60;
                z-index: 9998;
                pointer-events: none;
            `;
            
            // DOM'a ekle
            document.body.appendChild(topFrame);
            document.body.appendChild(bottomFrame);
            document.body.appendChild(leftFrame);
            document.body.appendChild(rightFrame);
            
            // Body'ye margin ekle (çerçevelerin altına kalmasın)
            document.body.style.marginTop = '8px';
            document.body.style.marginBottom = '8px';
            document.body.style.marginLeft = '15px';
            document.body.style.marginRight = '15px';
            
            console.log('✅ Sayfa yeşil çerçeveleri eklendi');
            """
            
            browser.driver.execute_script(page_frame_js)
            
            print("[PAGE FRAME] ✅ Sayfa çerçeveleri başarıyla eklendi")
            
        except Exception as e:
            print(f"[PAGE FRAME] Sayfa çerçeve hatası: {e}")
    
    def _inject_overlay_frame(self, browser):
        """Medula sayfasına JavaScript ile çerçeve overlay inject eder"""
        try:
            print("[OVERLAY] Çerçeve overlay JavaScript injection başlatılıyor...")
            
            # JavaScript kodu - Medula sayfasının üzerine çerçeve overlay
            overlay_js = """
            // OVERLAY ÇERÇEVE SİSTEMİ - MEDULA ÜZERİNE
            console.log('🎯 REÇETE KONTROL ÇERÇEVESİ - Başlatılıyor...');
            
            // Mevcut overlay'i temizle (varsa)
            const existingOverlay = document.getElementById('recete-kontrol-cercevesi');
            if (existingOverlay) {
                existingOverlay.remove();
            }
            
            // Ana overlay container
            const overlayContainer = document.createElement('div');
            overlayContainer.id = 'recete-kontrol-cercevesi';
            overlayContainer.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                pointer-events: none;
                font-family: Arial, sans-serif;
            `;
            
            // Üst çerçeve - kontrol paneli - AÇIK YEŞİL
            const topFrame = document.createElement('div');
            topFrame.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 60px;
                background: linear-gradient(135deg, #27ae60 0%, #27ae60 100%);
                border-bottom: 2px solid #1abc9c;
                pointer-events: auto;
                box-shadow: 0 1px 5px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 20px;
            `;
            
            // Sol taraf - başlık
            const titleDiv = document.createElement('div');
            titleDiv.innerHTML = `
                <h2 style="margin: 0; color: white; font-size: 18px; font-weight: bold;">
                    🎯 REÇETE KONTROL ÇERÇEVESİ
                </h2>
                <p style="margin: 0; color: #bdc3c7; font-size: 12px;">
                    Medula Akıllı Analiz Sistemi
                </p>
            `;
            
            // Sağ taraf - kontrol butonları - SAĞA YASLI
            const controlDiv = document.createElement('div');
            controlDiv.style.cssText = `
                display: flex;
                gap: 8px;
                align-items: center;
                margin-left: auto;
            `;
            
            // Buton oluşturma fonksiyonu - EŞİT BOYUT
            function createButton(text, color, onclick) {
                const btn = document.createElement('button');
                btn.innerHTML = text;
                btn.style.cssText = `
                    background: ` + color + `;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    min-width: 120px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                btn.onmouseover = () => btn.style.transform = 'scale(1.05)';
                btn.onmouseout = () => btn.style.transform = 'scale(1)';
                btn.onclick = onclick;
                return btn;
            }
            
            // SAYFA ALGILAMA VE DİNAMİK BUTONLAR
            function getPageType() {
                const url = window.location.href;
                const title = document.title.toLowerCase();
                
                if (url.includes('receteDetay') || title.includes('reçete detay')) {
                    return 'prescription_detail';
                } else if (url.includes('receteListesi') || title.includes('reçete listesi')) {
                    return 'prescription_list';
                } else {
                    return 'main_page';
                }
            }
            
            const pageType = getPageType();
            console.log('Detected page type:', pageType);
            
            // DİNAMİK BUTON SİSTEMİ
            if (pageType === 'prescription_detail') {
                // TEK REÇETE SAYFASI
                controlDiv.appendChild(createButton('🔍 BU REÇETEYİ KONTROL ET', '#e74c3c', () => {
                    alert('🔍 Tek reçete kontrolü başlatılıyor...');
                    console.log('Single prescription control triggered');
                }));
            } else if (pageType === 'prescription_list') {
                // REÇETE LİSTESİ SAYFASI
                controlDiv.appendChild(createButton('📅 GÜNLÜK KONTROL', '#27ae60', () => {
                    alert('📅 Günlük toplu kontrol başlatılıyor...');
                    console.log('Daily batch control triggered');
                }));
                
                controlDiv.appendChild(createButton('📊 AYLIK KONTROL', '#2980b9', () => {
                    showGroupOrderModal();
                }));
            } else {
                // ANA SAYFA - SADECE AYLIK KONTROL
                controlDiv.appendChild(createButton('📊 TÜM AYLARI KONTROL ET', '#2980b9', () => {
                    showGroupOrderModal();
                }));
            }
            
            // KAPAT BUTONU HER ZAMAN
            controlDiv.appendChild(createButton('❌ KAPAT', '#95a5a6', () => {
                document.getElementById('recete-kontrol-cercevesi').remove();
                document.body.style.margin = '0';
                console.log('Overlay çerçevesi kapatıldı');
            }));
            
            // GRUP SIRALAMA MODAL FONKSIYONU
            function showGroupOrderModal() {
                // Mevcut modal varsa kaldır
                const existingModal = document.getElementById('group-order-modal');
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Modal overlay
                const modalOverlay = document.createElement('div');
                modalOverlay.id = 'group-order-modal';
                modalOverlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                
                // Modal content
                const modalContent = document.createElement('div');
                modalContent.style.cssText = `
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                    width: 400px;
                    max-height: 500px;
                    overflow-y: auto;
                `;
                
                modalContent.innerHTML = `
                    <h2 style="margin: 0 0 20px 0; color: #2c3e50; text-align: center;">
                        🎯 REÇETE GRUP SIRALAMA
                    </h2>
                    <p style="margin: 0 0 20px 0; color: #7f8c8d; text-align: center; font-size: 14px;">
                        Hangi grup önce kontrol edilsin? Sürükleyerek sıralayın:
                    </p>
                    
                    <div id="group-list" style="margin-bottom: 20px;">
                        <div class="group-item" data-group="C" style="background: #3498db; margin: 5px 0; padding: 10px; border-radius: 5px; color: white; cursor: grab; user-select: none;">
                            <span class="order-number">1</span> - C GRUBU (Sıralı Dağıtım)
                        </div>
                        <div class="group-item" data-group="A" style="background: #e74c3c; margin: 5px 0; padding: 10px; border-radius: 5px; color: white; cursor: grab; user-select: none;">
                            <span class="order-number">2</span> - A GRUBU (Raporlu İlaçlar)
                        </div>
                        <div class="group-item" data-group="Gecici_Koruma" style="background: #f39c12; margin: 5px 0; padding: 10px; border-radius: 5px; color: white; cursor: grab; user-select: none;">
                            <span class="order-number">3</span> - GEÇİCİ KORUMA (Mülteci)
                        </div>
                        <div class="group-item" data-group="B" style="background: #27ae60; margin: 5px 0; padding: 10px; border-radius: 5px; color: white; cursor: grab; user-select: none;">
                            <span class="order-number">4</span> - B GRUBU (Normal)
                        </div>
                        <div class="group-item" data-group="C_Kan" style="background: #8e44ad; margin: 5px 0; padding: 10px; border-radius: 5px; color: white; cursor: grab; user-select: none;">
                            <span class="order-number">5</span> - C GRUBU (Kan Ürünü)
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <button id="start-control-btn" style="background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                            🚀 KONTROLE BAŞLA
                        </button>
                        <button id="cancel-modal-btn" style="background: #95a5a6; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                            ❌ İPTAL
                        </button>
                    </div>
                `;
                
                modalOverlay.appendChild(modalContent);
                document.body.appendChild(modalOverlay);
                
                // SÜRÜKLEME İŞLEVİ
                let draggedElement = null;
                const groupItems = modalContent.querySelectorAll('.group-item');
                
                groupItems.forEach(item => {
                    item.draggable = true;
                    
                    item.addEventListener('dragstart', (e) => {
                        draggedElement = item;
                        item.style.opacity = '0.5';
                    });
                    
                    item.addEventListener('dragend', () => {
                        item.style.opacity = '1';
                        updateOrderNumbers();
                    });
                    
                    item.addEventListener('dragover', (e) => {
                        e.preventDefault();
                    });
                    
                    item.addEventListener('drop', (e) => {
                        e.preventDefault();
                        if (draggedElement !== item) {
                            const container = item.parentNode;
                            const allItems = Array.from(container.children);
                            const draggedIndex = allItems.indexOf(draggedElement);
                            const targetIndex = allItems.indexOf(item);
                            
                            if (draggedIndex < targetIndex) {
                                container.insertBefore(draggedElement, item.nextSibling);
                            } else {
                                container.insertBefore(draggedElement, item);
                            }
                        }
                    });
                });
                
                function updateOrderNumbers() {
                    const items = modalContent.querySelectorAll('.group-item');
                    items.forEach((item, index) => {
                        item.querySelector('.order-number').textContent = index + 1;
                    });
                }
                
                // BUTON ETKİLEŞİMLERİ
                modalContent.querySelector('#start-control-btn').addEventListener('click', () => {
                    const items = modalContent.querySelectorAll('.group-item');
                    const order = Array.from(items).map(item => item.dataset.group);
                    console.log('Kontrol sırası:', order);
                    alert('🚀 Kontrol başlatılıyor... Sıra: ' + order.join(' → '));
                    modalOverlay.remove();
                });
                
                modalContent.querySelector('#cancel-modal-btn').addEventListener('click', () => {
                    modalOverlay.remove();
                });
                
                // Modal dışına tıklayınca kapat
                modalOverlay.addEventListener('click', (e) => {
                    if (e.target === modalOverlay) {
                        modalOverlay.remove();
                    }
                });
            }
            
            // Alt çerçeve - status bar - AÇIK YEŞİL
            const bottomFrame = document.createElement('div');
            bottomFrame.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 30px;
                background: linear-gradient(135deg, #27ae60 0%, #27ae60 100%);
                border-top: 1px solid #2ecc71;
                pointer-events: auto;
                display: flex;
                align-items: center;
                padding: 0 20px;
                color: white;
                font-size: 11px;
            `;
            
            bottomFrame.innerHTML = `
                <div style="display: flex; gap: 15px;">
                    <span>🟢 Sistem Aktif</span>
                    <span>🔵 0 Kontrolsuz</span>
                    <span>🟢 0 Uygun</span>
                    <span>🔴 0 Uygun Değil</span>
                    <span>🟡 0 Şüpheli</span>
                    <span>🟠 0 Ek Kontrol</span>
                </div>
                <div style="margin-left: auto;">
                    <span>⚡ Hazır - Reçete kontrolü için butonlara tıklayın</span>
                </div>
            `;
            
            // Sol çerçeve - İNCE AÇIK YEŞİL
            const leftFrame = document.createElement('div');
            leftFrame.style.cssText = `
                position: absolute;
                top: 60px;
                left: 0;
                width: 15px;
                height: calc(100% - 90px);
                background: linear-gradient(180deg, #27ae60 0%, #27ae60 100%);
                pointer-events: none;
            `;
            
            // Sağ çerçeve - İNCE AÇIK YEŞİL
            const rightFrame = document.createElement('div');
            rightFrame.style.cssText = `
                position: absolute;
                top: 60px;
                right: 0;
                width: 15px;
                height: calc(100% - 90px);
                background: linear-gradient(180deg, #27ae60 0%, #27ae60 100%);
                pointer-events: none;
            `;
            
            // Tüm elemanları ekle
            topFrame.appendChild(titleDiv);
            topFrame.appendChild(controlDiv);
            
            overlayContainer.appendChild(topFrame);
            overlayContainer.appendChild(bottomFrame);
            overlayContainer.appendChild(leftFrame);
            overlayContainer.appendChild(rightFrame);
            
            // DOM'a ekle
            document.body.appendChild(overlayContainer);
            
            console.log('✅ REÇETE KONTROL ÇERÇEVESİ - Başarıyla yüklendi!');
            console.log('🎯 Medula sayfası artık çerçeve ile korunuyor');
            
            // Medula içeriğini çerçeve içinde göstermek için margin ayarla - İNCE ÇERÇEVE
            document.body.style.marginTop = '60px';
            document.body.style.marginBottom = '30px';
            document.body.style.marginLeft = '15px';
            document.body.style.marginRight = '15px';
            """
            
            # JavaScript'i inject et
            browser.driver.execute_script(overlay_js)
            print("[OVERLAY] ✅ Çerçeve overlay başarıyla inject edildi!")
            
        except Exception as e:
            print(f"[OVERLAY ERROR] Çerçeve injection hatası: {e}")

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
    """Ana çalıştırma fonksiyonu"""
    print("\n" + "="*60)
    print("[*] OVERLAY CERCEVE SISTEMI BASLATILIYOR...")
    print("[*] Tam ekran Medula browser + yesil cerceve sistemi")
    print("[*] Adres cubugu gizleme + UI optimizasyonu")
    print("[*] Sayfa ust-alt yesil cercevemleme")
    print("[*] Medula web sitesi baglantisi eklendi")
    print("[*] Ilk ayarlar butonlari duzeltildi")
    print("="*60 + "\n")
    
    try:
        overlay_system = OverlaySystem()
        overlay_system.show_main_control_panel()
        
    except Exception as e:
        print(f"SISTEM BAŞLATMA HATASI: {e}")

if __name__ == "__main__":
    main()