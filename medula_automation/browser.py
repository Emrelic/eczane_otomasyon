"""
Medula Web Otomasyon Sınıfı
Selenium kullanarak Medula sistemi ile etkileşim
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime
from pathlib import Path
from loguru import logger


class MedulaBrowser:
    """Medula web sitesi otomasyon sınıfı"""
    
    def __init__(self, settings):
        self.settings = settings
        self.driver = None
        self.wait = None
        
        # Dizinleri oluştur
        self.settings.create_directories()
        
        # Logger'ı yapılandır
        logger.add(
            self.settings.log_file,
            rotation="1 day",
            level=self.settings.log_level
        )
    
    def start(self):
        """Browser'ı başlatır"""
        try:
            logger.info(f"Browser başlatılıyor: {self.settings.browser_type}")
            
            if self.settings.browser_type == 'chrome':
                self._start_chrome()
            elif self.settings.browser_type == 'firefox':
                self._start_firefox()
            elif self.settings.browser_type == 'edge':
                self._start_edge()
            else:
                raise ValueError(f"Desteklenmeyen browser: {self.settings.browser_type}")
            
            # WebDriverWait nesnesini oluştur
            self.wait = WebDriverWait(self.driver, self.settings.page_load_timeout)
            
            # Implicit wait ayarla
            self.driver.implicitly_wait(self.settings.implicit_wait)
            
            logger.success("Browser başarıyla başlatıldı")
            return True
            
        except Exception as e:
            logger.error(f"Browser başlatılırken hata: {e}")
            return False
    
    def _start_chrome(self):
        """Chrome browser'ı başlatır"""
        options = webdriver.ChromeOptions()
        
        if self.settings.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def _start_firefox(self):
        """Firefox browser'ı başlatır"""
        options = webdriver.FirefoxOptions()
        
        if self.settings.headless:
            options.add_argument('--headless')
        
        service = FirefoxService(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=options)
    
    def _start_edge(self):
        """Edge browser'ı başlatır"""
        options = webdriver.EdgeOptions()
        
        if self.settings.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)
    
    def login(self):
        """Medula sistemine giriş yapar"""
        try:
            logger.info("Medula'ya giriş yapılıyor...")
            
            # Ana sayfaya git
            self.driver.get(self.settings.medula_url)
            
            # Login sayfasının yüklenmesini bekle
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            
            # Kullanıcı adı ve şifre gir
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(self.settings.medula_username)
            
            password_field.clear()
            password_field.send_keys(self.settings.medula_password)
            
            # Screenshot al (eğer aktifse)
            if self.settings.enable_screenshots:
                self._take_screenshot("login_page")
            
            # Giriş butonuna tıkla
            login_button = self.driver.find_element(By.ID, "loginButton")
            login_button.click()
            
            # Ana sayfanın yüklenmesini bekle
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-menu")))
            
            logger.success("Medula'ya başarıyla giriş yapıldı")
            return True
            
        except TimeoutException:
            logger.error("Medula giriş sayfası yüklenemedi (timeout)")
            return False
        except NoSuchElementException as e:
            logger.error(f"Giriş elemanları bulunamadı: {e}")
            return False
        except Exception as e:
            logger.error(f"Giriş sırasında hata: {e}")
            return False
    
    def get_pending_prescriptions(self):
        """Bekleyen reçeteleri getirir"""
        try:
            logger.info("Bekleyen reçeteler getiriliyor...")
            
            # Reçete yönetimi sayfasına git
            self.driver.get(f"{self.settings.medula_url}/prescription/pending")
            
            # Tablo yüklenene kadar bekle
            self.wait.until(EC.presence_of_element_located((By.ID, "prescriptionTable")))
            
            # Reçete satırlarını bul
            prescription_rows = self.driver.find_elements(By.CSS_SELECTOR, "#prescriptionTable tbody tr")
            
            prescriptions = []
            for row in prescription_rows:
                prescription_data = self._extract_prescription_data(row)
                if prescription_data:
                    prescriptions.append(prescription_data)
            
            logger.info(f"{len(prescriptions)} adet bekleyen reçete bulundu")
            return prescriptions
            
        except Exception as e:
            logger.error(f"Reçeteler getirilirken hata: {e}")
            return []
    
    def _extract_prescription_data(self, row):
        """Reçete satırından veri çıkarır"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            return {
                'id': cells[0].text.strip(),
                'patient_name': cells[1].text.strip(),
                'patient_tc': cells[2].text.strip(),
                'doctor_name': cells[3].text.strip(),
                'hospital': cells[4].text.strip(),
                'prescription_date': cells[5].text.strip(),
                'total_amount': cells[6].text.strip(),
                'status': cells[7].text.strip(),
                'element': row
            }
            
        except Exception as e:
            logger.warning(f"Reçete verisi çıkarılırken hata: {e}")
            return None
    
    def apply_decision(self, prescription, decision):
        """AI kararını reçeteye uygular"""
        try:
            logger.info(f"Karar uygulanıyor - Reçete ID: {prescription['id']}, Karar: {decision['action']}")
            
            # Reçete satırına tıkla
            prescription['element'].click()
            
            # Detay sayfasının yüklenmesini bekle
            self.wait.until(EC.presence_of_element_located((By.ID, "prescriptionDetail")))
            
            if decision['action'] == 'approve':
                self._approve_prescription(prescription, decision)
            elif decision['action'] == 'reject':
                self._reject_prescription(prescription, decision)
            elif decision['action'] == 'hold':
                self._hold_prescription(prescription, decision)
            
            return True
            
        except Exception as e:
            logger.error(f"Karar uygulanırken hata: {e}")
            return False
    
    def _approve_prescription(self, prescription, decision):
        """Reçeteyi onaylar"""
        approve_button = self.driver.find_element(By.ID, "approveButton")
        approve_button.click()
        
        # Onay mesajını bekle
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        
        logger.success(f"Reçete onaylandı - ID: {prescription['id']}")
    
    def _reject_prescription(self, prescription, decision):
        """Reçeteyi reddeder"""
        reject_button = self.driver.find_element(By.ID, "rejectButton")
        reject_button.click()
        
        # Red nedeni gir
        reason_field = self.driver.find_element(By.ID, "rejectReason")
        reason_field.send_keys(decision['reason'])
        
        # Onayla
        confirm_button = self.driver.find_element(By.ID, "confirmReject")
        confirm_button.click()
        
        logger.info(f"Reçete reddedildi - ID: {prescription['id']}, Neden: {decision['reason']}")
    
    def _hold_prescription(self, prescription, decision):
        """Reçeteyi bekletir"""
        hold_button = self.driver.find_element(By.ID, "holdButton")
        hold_button.click()
        
        # Bekleme nedeni gir
        note_field = self.driver.find_element(By.ID, "holdNote")
        note_field.send_keys(decision['reason'])
        
        # Onayla
        confirm_button = self.driver.find_element(By.ID, "confirmHold")
        confirm_button.click()
        
        logger.info(f"Reçete bekletildi - ID: {prescription['id']}, Neden: {decision['reason']}")
    
    def _take_screenshot(self, name):
        """Screenshot alır"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = Path(self.settings.screenshot_dir) / filename
            
            self.driver.save_screenshot(str(filepath))
            logger.debug(f"Screenshot alındı: {filepath}")
            
        except Exception as e:
            logger.warning(f"Screenshot alınamadı: {e}")
    
    def quit(self):
        """Browser'ı kapatır"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser kapatıldı")
        except Exception as e:
            logger.error(f"Browser kapatılırken hata: {e}")