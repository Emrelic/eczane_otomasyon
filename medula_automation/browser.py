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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
            self.wait.until(EC.presence_of_element_located((By.NAME, "j_username")))
            
            # Kullanıcı adı ve şifre gir
            username_field = self.driver.find_element(By.NAME, "j_username")
            password_field = self.driver.find_element(By.NAME, "j_password")
            
            username_field.clear()
            username_field.send_keys(self.settings.medula_username)
            
            password_field.clear()
            password_field.send_keys(self.settings.medula_password)
            
            # Screenshot al (eğer aktifse)
            if self.settings.enable_screenshots:
                self._take_screenshot("login_page")
            
            # KVKK checkbox'ını işaretle (CAPTCHA'dan önce)
            try:
                kvkk_checkbox = self.driver.find_element(By.NAME, "kvkkTaahhut")
                if not kvkk_checkbox.is_selected():
                    kvkk_checkbox.click()
                    logger.info("KVKK taahhütü işaretlendi")
                    print("[BAŞARILI] KVKK kutucuğu işaretlendi")
            except:
                logger.warning("KVKK checkbox bulunamadı")
                print("[UYARI] KVKK kutucuğu bulunamadı")
            
            # CAPTCHA kontrolü ve otomatik submit
            print("[CAPTCHA] CAPTCHA girin - 6. rakamı girince otomatik login!")
            print("[BEKLEMEde] CAPTCHA bekleniyor...")
            
            # CAPTCHA alanını bul - GERÇEK MEDULA SELECTOR'I EN ÜSTTE!
            captcha_field = None
            captcha_selectors = [
                # REAL MEDULA CAPTCHA SELECTORS - ÖNCELİKLİ!
                "input[name='guvenlikNumarasi']",  # GERÇEK MEDULA CAPTCHA!
                "input[type='text'][maxlength='6']",  # Generic 6-char input
                "input[id='verificationCode']",  # Fallback
                "#verificationCode",
                "input[name='verificationCode']",
                
                # Diğer muhtemel selectors
                "input[name='captcha']",
                "input[name='captchaCode']", 
                "input[name='j_captcha']",
                "input[id='captcha']",
                "input[id='captchaCode']",
                
                # Class-based selectors
                "input[class*='captcha']",
                "input[class*='verification']",
                "input[class*='code']",
                
                # General text inputs with specific attributes
                "input[type='text'][maxlength='6']",
                "input[type='text'][maxlength='5']",
                "input[type='text'][maxlength='4']",
                "input[type='text'][size='6']",
                "input[type='text'][size='5']",
                
                # XPath selectors
                "//input[@maxlength='6']",
                "//input[@maxlength='5']", 
                "//input[@maxlength='4']",
                "//input[contains(@name, 'captcha')]",
                "//input[contains(@name, 'verification')]",
                "//input[contains(@id, 'captcha')]",
                "//input[contains(@id, 'verification')]",
                "//input[contains(@class, 'captcha')]",
                "//input[contains(@class, 'verification')]",
                
                # Form-based approach - input near CAPTCHA image
                "//img[contains(@src, 'captcha')]/..//input[@type='text']",
                "//img[contains(@src, 'verification')]/..//input[@type='text']",
                "//div[contains(@class, 'captcha')]//input[@type='text']",
                "//td[contains(text(), 'Doğrulama')]//input[@type='text']",
                "//label[contains(text(), 'Doğrulama')]//input[@type='text']",
                
                # Fallback - any text input in login form
                "form input[type='text']:not([name='j_username'])"
            ]
            
            for selector in captcha_selectors:
                try:
                    if selector.startswith("//"):
                        captcha_field = self.driver.find_element(By.XPATH, selector)
                    else:
                        captcha_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"[BULUNAN] CAPTCHA alanı bulundu: {selector}")
                    break
                except:
                    continue
            
            if captcha_field:
                self._monitor_captcha_input(captcha_field)
            else:
                print("[UYARI] CAPTCHA alanı bulunamadı - sayfa analizi yapılıyor...")
                self._debug_page_inputs()
                print("[FALLBACK] Manuel CAPTCHA çözümü bekleniyor...")
                time.sleep(10)
            
            
            # Ana sayfanın yüklenmesini bekle (daha esnek kontrol)
            time.sleep(3)  # Sayfa yüklenmesi için bekle
            
            # Session keep-alive için çerez ayarları
            self.driver.add_cookie({
                'name': 'session_keep_alive', 
                'value': 'true',
                'domain': 'medeczane.sgk.gov.tr'
            })
            
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
    
    def _monitor_captcha_input(self, captcha_field):
        """CAPTCHA girişini izler ve 6. rakamda otomatik login yapar - GELİŞMİŞ VERSİYON"""
        try:
            logger.info("🔍 CAPTCHA monitoring başlatıldı - 6 rakam bekleniyor")
            print("[MONITORING] 🔍 CAPTCHA alanı izleniyor - 6 rakam girin!")
            print("[INFO] Sistem 6. karakteri girdiğinizde OTOMATIK giriş yapacak")
            
            # Maksimum bekleme süresi (saniye)
            max_wait = 180  # 3 dakika
            start_time = time.time()
            last_length = 0
            
            while time.time() - start_time < max_wait:
                try:
                    # Refresh element to avoid stale references
                    captcha_field = self._find_captcha_field()
                    if not captcha_field:
                        print("[ERROR] CAPTCHA alanı kayboldu!")
                        time.sleep(1)
                        continue
                        
                    # CAPTCHA alanındaki değeri kontrol et
                    current_value = captcha_field.get_attribute('value') or ""
                    current_length = len(current_value)
                    
                    # Değişiklik varsa rapor et
                    if current_length != last_length:
                        if current_length > 0:
                            print(f"[PROGRESS] ✏️ {current_length}/6 rakam girildi ({current_value})")
                        last_length = current_length
                    
                    # 6 rakam tamamlandıysa otomatik giriş yap
                    if current_length == 6:
                        print(f"[SUCCESS] ✅ 6 rakam tamamlandı: {current_value}")
                        print(f"[AUTO-SUBMIT] 🚀 Otomatik giriş başlatılıyor...")
                        logger.info(f"CAPTCHA completed with 6 digits: {current_value}")
                        
                        # Element fresh olmaya devam etsin
                        time.sleep(0.5)  # Biraz daha bekle
                        
                        # Multi-method login button click
                        success = self._enhanced_login_click()
                        
                        if success:
                            print(f"[SUCCESS] ✅ Otomatik giriş başarılı!")
                            logger.info("Auto-login successful after CAPTCHA completion")
                            return True
                        else:
                            print(f"[ERROR] ❌ Otomatik giriş başarısız - manuel deneyin")
                            # Try one more time with different method
                            time.sleep(1)
                            if self._emergency_login_click():
                                print(f"[SUCCESS] ✅ Emergency login başarılı!")
                                return True
                            return False
                    
                    # Kısa bekleme - daha responsive
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.debug(f"CAPTCHA monitoring iteration error: {e}")
                    time.sleep(0.5)
                    continue
            
            # Timeout durumu
            print("[TIMEOUT] ⏰ CAPTCHA bekleme süresi doldu - manuel login gerekli")
            logger.warning("CAPTCHA monitoring timeout")
            return False
            
        except Exception as e:
            logger.error(f"CAPTCHA monitoring critical error: {e}")
            print(f"[ERROR] CAPTCHA monitoring hatası: {e}")
            return False
    
    def _find_captcha_field(self):
        """CAPTCHA alanını bul - fresh element"""
        captcha_selectors = [
            "input[name='guvenlikNumarasi']",  # GERÇEK MEDULA CAPTCHA SELECTOR!
            "input[type='text'][maxlength='6']",
            "input[id='verificationCode']",  # Fallback
            "#verificationCode",
            "input[name='verificationCode']",
            "input[placeholder*='doğrulama']",
            "input[placeholder*='captcha' i]"
        ]
        
        for selector in captcha_selectors:
            try:
                field = self.driver.find_element(By.CSS_SELECTOR, selector)
                if field and field.is_enabled():
                    return field
            except:
                continue
        return None
    
    def _enhanced_login_click(self):
        """Gelişmiş login butonu tıklama - multiple methods"""
        try:
            print("[LOGIN] 🎯 Login butonu aranıyor...")
            
            # Login button selectors - priority order - GERÇEK MEDULA SELECTORS
            button_selectors = [
                "input[type='submit'][value='Giriş Yap']",  # TAM DOĞRU!
                "input[type='submit']",  # Generic submit
                "input[value='Giriş Yap']",  # Value match
                "input.button[value='Giriş Yap']",  # Class + value
                "button[type='submit']",
                "button:contains('Giriş')",
                ".login-button",
                "#loginButton",
                "button.btn-primary",
                "[onclick*='login']"
            ]
            
            for i, selector in enumerate(button_selectors):
                try:
                    print(f"[LOGIN] Selector {i+1}: {selector}")
                    
                    if "contains" in selector:
                        # XPath for contains - DOĞRU BUTON ADI: "Giriş Yap"
                        xpath = "//button[contains(text(), 'Giriş Yap')] | //input[@value='Giriş Yap'] | //button[contains(text(), 'Giriş')] | //input[@value='Giriş']"
                        button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button and button.is_enabled():
                        print(f"[LOGIN] ✅ Button bulundu: {selector}")
                        
                        # Method 1: Normal click
                        try:
                            button.click()
                            print("[LOGIN] ✅ Normal click başarılı")
                            time.sleep(1)
                            return True
                        except:
                            pass
                            
                        # Method 2: JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            print("[LOGIN] ✅ JavaScript click başarılı")
                            time.sleep(1)
                            return True
                        except:
                            pass
                            
                        # Method 3: Submit form if button is in form
                        try:
                            form = button.find_element(By.XPATH, "./ancestor::form")
                            if form:
                                form.submit()
                                print("[LOGIN] ✅ Form submit başarılı")
                                time.sleep(1)
                                return True
                        except:
                            pass
                        
                except Exception as e:
                    logger.debug(f"Login selector {selector} failed: {e}")
                    continue
            
            print("[LOGIN] ❌ Hiçbir login butonu bulunamadı")
            return False
            
        except Exception as e:
            logger.error(f"Enhanced login click error: {e}")
            return False
    
    def _emergency_login_click(self):
        """Emergency login method - en son çare"""
        try:
            print("[EMERGENCY] 🆘 Emergency login deneniyor...")
            
            # Try Enter key on CAPTCHA field
            captcha_field = self._find_captcha_field()
            if captcha_field:
                try:
                    captcha_field.send_keys(Keys.ENTER)
                    print("[EMERGENCY] ✅ Enter key gönderildi")
                    time.sleep(1)
                    return True
                except:
                    pass
            
            # Try Tab + Enter
            try:
                from selenium.webdriver.common.keys import Keys
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
                print("[EMERGENCY] ✅ Tab+Enter gönderildi")
                time.sleep(1)
                return True
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Emergency login error: {e}")
            return False
    
    def _click_login_button(self):
        """Login butonuna tıklar"""
        try:
            # Login butonunu bul ve tıkla
            login_button = None
            selectors = [
                "input[type='submit'][value='Giriş Yap']",  # TAM DOĞRU SELECTOR!
                "input[type='submit']",  # Generic submit
                "input[value='Giriş Yap']",  # Value match
                "input.button[value='Giriş Yap']",  # Class + value
                "//input[@type='submit' and @value='Giriş Yap']",  # XPATH exact match
                "//input[@type='submit']",  # XPATH generic
                "//input[@value='Giriş Yap']",  # XPATH value
                "//input[contains(@value, 'Giriş')]",  # XPATH contains
                "button[type='submit']",
                "//button[contains(text(), 'Giriş Yap')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        login_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # JavaScript click kullan - daha güvenilir
                    self.driver.execute_script("arguments[0].click();", login_button)
                    print(f"[AUTO-LOGIN] Login butonu otomatik tıklandı!")
                    logger.info(f"Auto login button clicked: {selector}")
                    return True
                    
                except Exception as e:
                    continue
            
            print("[ERROR] Login butonu bulunamadı")
            logger.error("Login button not found for auto-click")
            return False
            
        except Exception as e:
            logger.error(f"Auto login click error: {e}")
            return False
    
    def _debug_page_inputs(self):
        """Sayfadaki tüm input alanlarını listeler (debug için)"""
        try:
            print("[DEBUG] Sayfadaki tüm input alanları:")
            
            # Tüm input elementlerini bul
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = input_elem.get_attribute('type') or 'text'
                    input_name = input_elem.get_attribute('name') or 'N/A'
                    input_id = input_elem.get_attribute('id') or 'N/A'
                    input_class = input_elem.get_attribute('class') or 'N/A'
                    maxlength = input_elem.get_attribute('maxlength') or 'N/A'
                    
                    print(f"  Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}', class='{input_class[:30]}...', maxlength='{maxlength}'")
                    
                except Exception:
                    print(f"  Input {i+1}: [Error reading attributes]")
            
            print(f"[DEBUG] Toplam {len(inputs)} input alanı bulundu")
            
        except Exception as e:
            print(f"[DEBUG ERROR] Input analysis failed: {e}")
    
    def get_pending_prescriptions(self):
        """Bekleyen reçeteleri getirir"""
        try:
            logger.info("Bekleyen reçeteler getiriliyor...")
            
            # Ana sayfada kalmaya devam et - menü sistemini kullan
            logger.info("Ana sayfada menü sistemi aranıyor...")
            
            # Reçete listesi menü linkini bul (Medula sol menü için genişletildi)
            menu_selectors = [
                "//a[contains(text(), 'Reçete Listesi')]",
                "//span[contains(text(), 'Reçete Listesi')]", 
                "//div[contains(text(), 'Reçete Listesi')]",
                "//li[contains(text(), 'Reçete Listesi')]",
                "//a[contains(text(), 'Reçete')]",
                "//*[contains(text(), 'Reçete Listesi')]",
                "a[href*='recete']",
                "*[onclick*='recete']",
                ".menu-item:contains('Reçete')",
                "[title*='Reçete']"
            ]
            
            menu_found = False
            for selector in menu_selectors:
                try:
                    if selector.startswith('//') or selector.startswith('//*'):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # JavaScript click kullan - daha güvenli
                    self.driver.execute_script("arguments[0].click();", element)
                    menu_found = True
                    logger.info(f"Menü bulundu ve tıklandı: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"Selector başarısız {selector}: {e}")
                    continue
            
            if not menu_found:
                logger.warning("Reçete menüsü bulunamadı - Ana sayfada kalınıyor")
                return []
            
            # Sayfa yüklenmesini bekle
            import time
            time.sleep(3)
            
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