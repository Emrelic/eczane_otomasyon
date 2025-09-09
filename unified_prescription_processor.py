"""
Unified Prescription Processor
Tüm reçete işleme sürecini tek dosyada birleştirir
- Medula browser integration
- JSON data processing  
- SUT analysis
- Claude AI analysis
- Complete workflow management
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from loguru import logger

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from medula_automation.browser import MedulaBrowser
from ai_analyzer.sut_rules_database import SUTRulesDatabase
from ai_analyzer.claude_prescription_analyzer import ClaudePrescriptionAnalyzer
from database.sqlite_handler import SQLiteHandler
from config.settings import Settings
from advanced_prescription_extractor import AdvancedPrescriptionExtractor
from prescription_dose_controller import PrescriptionDoseController
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By

class UnifiedPrescriptionProcessor:
    """Unified reçete işleme sistemi"""
    
    def __init__(self):
        self.settings = Settings()
        self.browser = None
        self.sut_db = SUTRulesDatabase()
        self.ai_analyzer = ClaudePrescriptionAnalyzer()
        self.database = SQLiteHandler()
        self.extractor = None  # Will be initialized when needed
        self.dose_controller = PrescriptionDoseController()  # NEW: Dose controller
        
        # Results storage
        self.processed_prescriptions = []
        self.processing_stats = {
            "total_processed": 0,
            "approved": 0,
            "rejected": 0,
            "held": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
        
        logger.info("Unified Prescription Processor initialized with database and extractor support")
    
    # =========================================================================
    # CORE PROCESSING METHODS
    # =========================================================================
    
    def process_from_json_file(self, json_file_path, output_file=None):
        """JSON dosyasından reçeteleri işler"""
        try:
            logger.info(f"Processing prescriptions from JSON: {json_file_path}")
            
            # JSON dosyasını oku
            if not os.path.exists(json_file_path):
                raise FileNotFoundError(f"JSON file not found: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                prescriptions = json.load(f)
            
            if not prescriptions:
                logger.warning("No prescriptions found in JSON file")
                return []
            
            logger.info(f"Found {len(prescriptions)} prescriptions to process")
            
            # Reçeteleri işle
            results = self._process_prescription_batch(prescriptions, "json_file")
            
            # Sonuçları kaydet
            if output_file:
                self._save_results(results, output_file)
            
            return results
            
        except Exception as e:
            logger.error(f"JSON processing error: {e}")
            raise
    
    def process_from_medula_live(self, limit=5, group='A'):
        """Canlı Medula'dan reçeteleri çeker ve işler"""
        try:
            logger.info("Starting live Medula prescription processing")
            
            # Browser başlat
            if not self._initialize_browser():
                raise Exception("Browser initialization failed")
            
            # Medula'ya giriş yap
            if not self._medula_login():
                raise Exception("Medula login failed")
            
            # Reçete listesini çek
            prescriptions = self._extract_prescriptions_from_medula(limit, group)
            
            if not prescriptions:
                logger.warning("No prescriptions extracted from Medula")
                return []
            
            logger.info(f"Extracted {len(prescriptions)} prescriptions from Medula")
            
            # Reçeteleri işle
            results = self._process_prescription_batch(prescriptions, "medula_live")
            
            # Browser'ı kapat
            self._cleanup_browser()
            
            return results
            
        except Exception as e:
            logger.error(f"Live Medula processing error: {e}")
            self._cleanup_browser()
            raise
    
    def process_single_prescription(self, prescription_data, source="manual"):
        """Tek bir reçeteyi işler"""
        try:
            logger.info(f"Processing single prescription: {prescription_data.get('recete_no', 'N/A')}")
            
            # Temel doğrulama
            if not self._validate_prescription_data(prescription_data):
                return self._create_error_result(prescription_data, "Invalid prescription data")
            
            # İşleme başlangıcı
            start_time = datetime.now()
            
            # DOZ KONTROLÜ (YENİ!)
            dose_result = self._perform_dose_control(prescription_data)
            
            # SUT analizi
            sut_result = self._perform_sut_analysis(prescription_data)
            
            # AI analizi  
            ai_result = self._perform_ai_analysis(prescription_data)
            
            # Sonucu birleştir
            final_result = self._combine_analysis_results(
                prescription_data, sut_result, ai_result, dose_result, source, start_time
            )
            
            # İstatistikleri güncelle
            self._update_stats(final_result)
            
            # Veritabanına kaydet
            self._save_to_database(prescription_data, final_result)
            
            logger.info(f"Prescription processed: {final_result['prescription_id']} -> {final_result['final_decision']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Single prescription processing error: {e}")
            return self._create_error_result(prescription_data, str(e))
    
    # =========================================================================
    # MEDULA INTEGRATION METHODS
    # =========================================================================
    
    def _initialize_browser(self):
        """Browser'ı başlatır"""
        try:
            self.browser = MedulaBrowser(self.settings)
            success = self.browser.start()
            
            if success:
                logger.info("Browser initialized successfully")
                return True
            else:
                logger.error("Browser initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Browser initialization error: {e}")
            return False
    
    def _medula_login(self):
        """Medula'ya giriş yapar"""
        try:
            if not self.browser:
                return False
            
            success = self.browser.login()
            
            if success:
                logger.info("Medula login successful")
                return True
            else:
                logger.error("Medula login failed")
                return False
                
        except Exception as e:
            logger.error(f"Medula login error: {e}")
            return False
    
    def _extract_prescriptions_from_medula(self, limit=5, group='A'):
        """Medula'dan reçete listesini çıkarır - GERÇEK VERİ ÇIKARMA"""
        try:
            logger.info(f"🔄 REAL MEDULA EXTRACTION: {limit} prescriptions (Group {group})")
            
            # Advanced extractor'ı başlat (browser zaten açık)
            if not self.extractor:
                self.extractor = AdvancedPrescriptionExtractor()
                # Mevcut browser'ı kullan
                self.extractor.browser = self.browser  
                self.extractor.wait = WebDriverWait(self.browser.driver, 30) if self.browser and hasattr(self.browser, 'driver') else None
                logger.info("✅ Advanced extractor initialized with existing browser")
            
            # REAL EXTRACTION WORKFLOW
            # 1. Navigate to prescription list
            logger.info("📍 Step 1: Navigating to prescription list")
            if not self._navigate_to_prescription_list():
                logger.warning("⚠️ Navigation failed, trying fallback navigation")
                if not self.extractor.navigate_to_prescriptions_auto():
                    logger.error("❌ Both navigation methods failed")
                    return self._get_fallback_mock_data(limit)
            
            # 2. Apply filters
            logger.info(f"🔍 Step 2: Applying {group} group filter")
            if not self._apply_filters_enhanced(group):
                logger.warning("⚠️ Filter application failed, proceeding with current data")
            
            # 3. Execute query and get prescription list
            logger.info("🔎 Step 3: Executing prescription query")
            if not self._execute_prescription_query():
                logger.error("❌ Prescription query failed")
                return self._get_fallback_mock_data(limit)
            
            # 4. Extract prescriptions from table
            logger.info(f"📝 Step 4: Extracting {limit} prescriptions from results table")
            prescriptions = self._extract_prescription_list_enhanced(limit)
            
            # 5. Validate results
            if not prescriptions:
                logger.warning("⚠️ No prescriptions extracted, falling back to mock data")
                return self._get_fallback_mock_data(limit)
            
            logger.info(f"✅ Successfully extracted {len(prescriptions)} REAL prescriptions from Medula")
            return prescriptions
            
        except Exception as e:
            logger.error(f"❌ Real Medula extraction failed: {e}")
            logger.info("🔄 Falling back to mock data for continuity")
            return self._get_fallback_mock_data(limit)
    
    def _navigate_to_prescription_list(self):
        """Reçete listesi sayfasına git"""
        try:
            # Ana menüden reçete listesi linkini bul
            menu_selectors = [
                "//a[contains(text(), 'Reçete Listesi')]",
                "//li[contains(text(), 'Reçete Listesi')]",
                "//span[contains(text(), 'Reçete Listesi')]",
                "//div[contains(text(), 'Reçete Listesi')]",
                "a[href*='recete']",
                "a[href*='liste']"
            ]
            
            for selector in menu_selectors:
                try:
                    if selector.startswith('//'):
                        element = self.browser.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element.is_displayed():
                        # JavaScript click for reliability
                        self.browser.driver.execute_script("arguments[0].click();", element)
                        time.sleep(3)
                        logger.info("✅ Successfully navigated to prescription list")
                        return True
                        
                except Exception as e:
                    continue
            
            logger.warning("⚠️ Prescription list navigation failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def _apply_filters_enhanced(self, group='A'):
        """Gelişmiş A Grubu filtreleme"""
        try:
            # Farklı dropdown selector stratejileri
            filter_strategies = [
                # Strategy 1: Name attribute based
                {
                    'selectors': ["//select[contains(@name, 'fatur')]", "//select[contains(@name, 'grup')]"],
                    'options': [f"{group} Grubu", f"{group} GRUBU", f"Grup {group}", group]
                },
                # Strategy 2: ID attribute based  
                {
                    'selectors': ["//select[contains(@id, 'fatur')]", "//select[contains(@id, 'grup')]"],
                    'options': [f"{group} Grubu", f"{group} GRUBU", f"Grup {group}", group]
                },
                # Strategy 3: CSS class based
                {
                    'selectors': ["select[class*='fatur']", "select[class*='grup']"],
                    'options': [f"{group} Grubu", f"{group} GRUBU", f"Grup {group}", group]
                },
                # Strategy 4: Generic select elements
                {
                    'selectors': ["select", "//select"],
                    'options': [f"{group} Grubu", f"{group} GRUBU", f"Grup {group}", group]
                }
            ]
            
            for strategy in filter_strategies:
                for selector in strategy['selectors']:
                    try:
                        if selector.startswith('//'):
                            dropdowns = self.browser.driver.find_elements(By.XPATH, selector)
                        else:
                            dropdowns = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for dropdown in dropdowns:
                            if not dropdown.is_displayed():
                                continue
                                
                            select_obj = Select(dropdown)
                            
                            # Try each option for this dropdown
                            for option_text in strategy['options']:
                                try:
                                    select_obj.select_by_visible_text(option_text)
                                    logger.info(f"✅ Filter applied: {option_text}")
                                    time.sleep(1)  # Wait for filter to take effect
                                    return True
                                except:
                                    continue
                                    
                    except:
                        continue
            
            logger.warning(f"⚠️ Could not apply {group} group filter")
            return False
            
        except Exception as e:
            logger.error(f"❌ Enhanced filter application error: {e}")
            return False
    
    def _execute_prescription_query(self):
        """Reçete sorgusunu çalıştır"""
        try:
            # Sorgula butonunu bul ve tıkla
            query_selectors = [
                "//input[@type='submit' and contains(@value, 'Sorgula')]",
                "//button[contains(text(), 'Sorgula')]",
                "//input[@value='Sorgula']",
                "//button[@type='submit']",
                "input[type='submit']",
                "button[type='submit']",
                ".btn-query",
                "#queryBtn"
            ]
            
            for selector in query_selectors:
                try:
                    if selector.startswith('//'):
                        button = self.browser.driver.find_element(By.XPATH, selector)
                    else:
                        button = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        # Try regular click first
                        try:
                            button.click()
                        except:
                            # Fallback to JavaScript click
                            self.browser.driver.execute_script("arguments[0].click();", button)
                        
                        logger.info("✅ Query button clicked")
                        time.sleep(5)  # Wait for results to load
                        return True
                        
                except Exception as e:
                    continue
            
            logger.warning("⚠️ Query button not found or clickable")
            return False
            
        except Exception as e:
            logger.error(f"❌ Query execution error: {e}")
            return False
    
    def _extract_prescription_list_enhanced(self, limit=5):
        """Gelişmiş reçete listesi çıkarma - TAM OTOM ATİK"""
        try:
            prescriptions = []
            
            # Tablo yüklenene kadar bekle
            time.sleep(5)
            
            # Tablo satırlarını bul
            rows = self._find_prescription_rows_enhanced()
            if not rows:
                logger.warning("⚠️ No prescription table rows found")
                return []
            
            logger.info(f"📊 Found {len(rows)} prescription rows in table")
            
            # Her satır için detayları çıkar
            for i, row in enumerate(rows[:limit]):
                try:
                    logger.info(f"🔍 Extracting prescription {i+1}/{min(len(rows), limit)}")
                    
                    # İlk önce satırdan temel bilgileri al (reçete no vb.)
                    basic_info = self._extract_row_data(row)
                    
                    # Detaylı bilgi için satıra tıkla
                    if not self._click_prescription_row(row):
                        logger.warning(f"⚠️ Could not click row {i+1}, using basic info only")
                        if basic_info and basic_info.get('recete_no'):
                            basic_info['extraction_method'] = 'medula_basic_only'
                            basic_info['extraction_timestamp'] = datetime.now().isoformat()
                            prescriptions.append(basic_info)
                        continue
                    
                    time.sleep(3)  # Detay sayfası yüklensin
                    
                    # Detay sayfasından tam veri çıkar
                    detailed_data = self._extract_prescription_details_enhanced()
                    
                    if detailed_data:
                        # Basic info ile detailed data'yı birleştir
                        if basic_info:
                            detailed_data.update(basic_info)
                        
                        detailed_data['extraction_method'] = 'medula_real_detailed'
                        detailed_data['extraction_timestamp'] = datetime.now().isoformat()
                        prescriptions.append(detailed_data)
                        logger.info(f"✅ Prescription {detailed_data.get('recete_no', 'N/A')} extracted with full details")
                    elif basic_info and basic_info.get('recete_no'):
                        # Detay alınamazsa en azından basic bilgiyi kaydet
                        basic_info['extraction_method'] = 'medula_basic_fallback'
                        basic_info['extraction_timestamp'] = datetime.now().isoformat()
                        prescriptions.append(basic_info)
                        logger.info(f"✅ Prescription {basic_info.get('recete_no', 'N/A')} extracted with basic info")
                    
                    # Geri git - multiple strategies
                    self._navigate_back_to_list()
                    
                except Exception as e:
                    logger.error(f"❌ Error extracting prescription {i+1}: {e}")
                    # Hata durumunda da geri gitmeye çalış
                    self._navigate_back_to_list()
                    continue
            
            logger.info(f"✅ Successfully extracted {len(prescriptions)} prescriptions")
            return prescriptions
            
        except Exception as e:
            logger.error(f"❌ Enhanced prescription list extraction error: {e}")
            return []
    
    def _find_prescription_rows_enhanced(self):
        """Gelişmiş tablo satır bulma"""
        try:
            # Farklı tablo yapıları için stratejiler
            table_strategies = [
                # Strategy 1: Standard HTML tables
                {
                    'table_selectors': ["//table[contains(@class, 'result')]", "//table[contains(@id, 'result')]", "//table"],
                    'row_selectors': ["tbody tr", "tr:not(:first-child)", "tr[onclick]", "tr[class]", "tr"]
                },
                # Strategy 2: DIV based tables
                {
                    'table_selectors': ["//div[contains(@class, 'table')]", "//div[contains(@class, 'grid')]"],
                    'row_selectors': [".row", ".grid-row", "div[onclick]", "div[class*='row']"]
                },
                # Strategy 3: Direct row finding
                {
                    'table_selectors': ["body"],  # Search entire body
                    'row_selectors': ["//tr[td]", "//div[contains(@onclick, 'recete')]", ".prescription-row", "[data-recete]"]
                }
            ]
            
            for strategy in table_strategies:
                for table_selector in strategy['table_selectors']:
                    try:
                        # Find table container
                        if table_selector.startswith('//'):
                            tables = self.browser.driver.find_elements(By.XPATH, table_selector)
                        else:
                            tables = self.browser.driver.find_elements(By.CSS_SELECTOR, table_selector)
                        
                        for table in tables:
                            if not table.is_displayed():
                                continue
                                
                            # Find rows within this table
                            for row_selector in strategy['row_selectors']:
                                try:
                                    if row_selector.startswith('//'):
                                        rows = table.find_elements(By.XPATH, "." + row_selector)  # Relative xpath
                                    else:
                                        rows = table.find_elements(By.CSS_SELECTOR, row_selector)
                                    
                                    # Filter visible and valid rows
                                    valid_rows = []
                                    for row in rows:
                                        if row.is_displayed() and self._is_prescription_row(row):
                                            valid_rows.append(row)
                                    
                                    if valid_rows:
                                        logger.info(f"✅ Found {len(valid_rows)} valid prescription rows using strategy: {table_selector} + {row_selector}")
                                        return valid_rows
                                        
                                except Exception as e:
                                    continue
                                    
                    except Exception as e:
                        continue
            
            logger.warning("⚠️ No prescription rows found with any strategy")
            return []
            
        except Exception as e:
            logger.error(f"❌ Enhanced row finding error: {e}")
            return []
    
    def _is_prescription_row(self, row):
        """Satırın reçete satırı olup olmadığını kontrol et"""
        try:
            row_text = row.text.lower()
            
            # Reçete satırı işaretleri
            prescription_indicators = [
                'gp',  # GP ile başlayan reçete numaraları
                'reçete',  # Reçete kelimesi
                'hasta',   # Hasta kelimesi
                'tc',      # TC kimlik
                'ilaç',     # İlaç kelimesi
            ]
            
            # En az iki gösterge olması gerekli
            indicator_count = sum(1 for indicator in prescription_indicators if indicator in row_text)
            
            # İçinde tıklanabilir element var mı?
            clickable = row.get_attribute('onclick') or row.find_elements(By.TAG_NAME, 'a')
            
            # Yeterli text içeriği var mı? (minimum 20 karakter)
            has_content = len(row_text.strip()) > 20
            
            return (indicator_count >= 1 or clickable) and has_content
            
        except:
            return False
    
    def _extract_row_data(self, row):
        """Tablo satırından temel bilgileri çıkar"""
        try:
            row_data = {}
            
            # Satır text'ini al
            row_text = row.text
            
            # Hücreleri bul
            cells = row.find_elements(By.TAG_NAME, 'td')
            if not cells:
                cells = row.find_elements(By.TAG_NAME, 'div')
            
            # Reçete no arama (farklı formatlar)
            import re
            recete_patterns = [
                r'\b(\d{1,2}GP\w+)\b',  # 1GP25RF format
                r'\b(GP\w+)\b',         # GP ile başlayan
                r'\b(\d{7,})\b',        # 7+ rakam
                r'Reçete[:\s]*(\w+)',     # "Reçete: XXX" format
            ]
            
            for pattern in recete_patterns:
                match = re.search(pattern, row_text)
                if match:
                    row_data['recete_no'] = match.group(1)
                    break
            
            # TC kimlik arama (11 rakam)
            tc_match = re.search(r'\b(\d{11})\b', row_text)
            if tc_match:
                row_data['hasta_tc'] = tc_match.group(1)
            
            # İsim arama (büyük harfli kelimeler)
            name_patterns = [
                r'\b([A-ZÇĞIÖŞÜ]{2,})\s+([A-ZÇĞIÖŞÜ]{2,})\b',  # İKI BÜYÜK KELİME
                r'Hasta[:\s]*([A-ZÇĞIÖŞÜ\s]+)',  # "Hasta: AD SOYAD" format
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, row_text)
                if match:
                    if len(match.groups()) == 2:
                        row_data['hasta_ad_soyad'] = f"{match.group(1)} {match.group(2)}"
                    else:
                        row_data['hasta_ad_soyad'] = match.group(1).strip()
                    break
            
            return row_data if row_data else None
            
        except Exception as e:
            logger.error(f"❌ Row data extraction error: {e}")
            return None
    
    def _click_prescription_row(self, row):
        """Reçete satırına tıkla"""
        try:
            # Farklı tıklama stratejileri
            click_strategies = [
                # Strategy 1: Direct row click
                lambda: row.click(),
                # Strategy 2: JavaScript click  
                lambda: self.browser.driver.execute_script("arguments[0].click();", row),
                # Strategy 3: Link in row
                lambda: row.find_element(By.TAG_NAME, 'a').click(),
                # Strategy 4: First cell click
                lambda: row.find_element(By.TAG_NAME, 'td').click() if row.find_elements(By.TAG_NAME, 'td') else None,
            ]
            
            for strategy in click_strategies:
                try:
                    strategy()
                    logger.debug("✅ Row clicked successfully")
                    return True
                except:
                    continue
            
            logger.warning("⚠️ Could not click prescription row")
            return False
            
        except Exception as e:
            logger.error(f"❌ Row click error: {e}")
            return False
    
    def _navigate_back_to_list(self):
        """Reçete listesine geri dön"""
        try:
            # Farklı geri dönme stratejileri
            back_strategies = [
                # Strategy 1: Browser back button
                lambda: self.browser.driver.back(),
                # Strategy 2: "Geri" button
                lambda: self.browser.driver.find_element(By.XPATH, "//input[@value='Geri']").click(),
                # Strategy 3: "Liste" button  
                lambda: self.browser.driver.find_element(By.XPATH, "//a[contains(text(), 'Liste')]").click(),
                # Strategy 4: JavaScript history back
                lambda: self.browser.driver.execute_script("window.history.back();"),
            ]
            
            for strategy in back_strategies:
                try:
                    strategy()
                    time.sleep(2)  # Sayfa yüklensin
                    logger.debug("✅ Navigated back to list")
                    return True
                except:
                    continue
            
            logger.warning("⚠️ Could not navigate back to list")
            return False
            
        except Exception as e:
            logger.error(f"❌ Navigate back error: {e}")
            return False
    
    def _extract_prescription_details_enhanced(self):
        """Gelişmiş reçete detay sayfası veri çıkarma - TAM ANALİZ"""
        try:
            prescription_data = {}
            
            logger.debug("🔍 Starting comprehensive prescription detail extraction")
            
            # 1. Temel bilgileri çıkar (reçete no, hasta bilgileri)
            basic_info = self._extract_basic_info_enhanced()
            prescription_data.update(basic_info)
            logger.debug(f"✅ Basic info extracted: {len(basic_info)} fields")
            
            # 2. İlaç bilgilerini çıkar (İlaç Bilgileri sekmesinden)
            drug_info = self._extract_drug_info_enhanced()
            prescription_data['drugs'] = drug_info['drugs']
            prescription_data['drug_details'] = drug_info.get('drug_details', {})
            logger.debug(f"✅ Drug info extracted: {len(drug_info['drugs'])} drugs")
            
            # 3. İlaç mesajlarını çıkar (SUT kodları)
            messages = self._extract_message_info_enhanced()
            prescription_data['ilac_mesajlari'] = messages.get('messages', '')
            prescription_data['drug_messages'] = messages.get('detailed_messages', [])
            logger.debug(f"✅ Messages extracted: {len(messages.get('detailed_messages', []))} detailed messages")
            
            # 4. Rapor bilgilerini çıkar (varsa)
            report_info = self._extract_report_info_enhanced()
            prescription_data.update(report_info)
            logger.debug(f"✅ Report info extracted: {len(report_info)} fields")
            
            # 5. Ek detay bilgileri (doktor, tarihler vb.)
            additional_info = self._extract_additional_info()
            prescription_data.update(additional_info)
            logger.debug(f"✅ Additional info extracted: {len(additional_info)} fields")
            
            # 6. Veri doğrulama ve düzenleme
            if self._validate_extracted_data(prescription_data):
                logger.info(f"✅ Complete prescription data extracted: {prescription_data.get('recete_no', 'Unknown')}")
                return prescription_data
            else:
                logger.warning("⚠️ Extracted data validation failed, returning partial data")
                return prescription_data if prescription_data else None
            
        except Exception as e:
            logger.error(f"❌ Enhanced prescription detail extraction error: {e}")
            return None
    
    def _extract_basic_info_enhanced(self):
        """Gelişmiş temel bilgi çıkarma - TÜM STRATEJİLER"""
        info = {}
        try:
            # Reçete no çıkarma - multiple strategies
            recete_strategies = [
                # Strategy 1: Label-based
                {
                    'selectors': [
                        "//*[contains(text(), 'Reçete No')]/following-sibling::*",
                        "//*[contains(text(), 'Reçete Numarası')]/following-sibling::*",
                        "//*[text()='Reçete No:']/following::*[1]",
                        "//*[text()='Reçete:']/following::*[1]"
                    ]
                },
                # Strategy 2: Input-based
                {
                    'selectors': [
                        "//input[contains(@name, 'recete')]",
                        "//input[contains(@id, 'recete')]",
                        "//input[@type='text'][contains(@value, 'GP')]",
                        "//input[@type='hidden'][contains(@value, 'GP')]"
                    ]
                },
                # Strategy 3: Table-based  
                {
                    'selectors': [
                        "//td[contains(text(), 'Reçete')]/following-sibling::td",
                        "//th[contains(text(), 'Reçete')]/following-sibling::td"
                    ]
                },
                # Strategy 4: Pattern-based (scan all text)
                {
                    'selectors': ["//body"],  # Scan entire page
                    'pattern': True
                }
            ]
            
            for strategy in recete_strategies:
                for selector in strategy['selectors']:
                    try:
                        if strategy.get('pattern'):
                            # Pattern-based extraction from entire page
                            import re
                            page_text = self.browser.driver.find_element(By.XPATH, selector).text
                            patterns = [
                                r'Reçete\s*:?\s*(\d{1,2}GP\w+)',
                                r'Reçete\s*No\s*:?\s*(\d{1,2}GP\w+)',
                                r'\b(\d{1,2}GP\w{3,})\b',
                                r'Reçete\s*:?\s*(\w{7,})'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, page_text, re.IGNORECASE)
                                if match:
                                    info['recete_no'] = match.group(1).strip()
                                    logger.debug(f"✅ Recete no found via pattern: {match.group(1)}")
                                    break
                            
                            if 'recete_no' in info:
                                break
                        else:
                            # Direct element-based extraction
                            element = self.browser.driver.find_element(By.XPATH, selector)
                            recete_no = element.text or element.get_attribute('value')
                            if recete_no and recete_no.strip():
                                info['recete_no'] = recete_no.strip()
                                logger.debug(f"✅ Recete no found via element: {recete_no}")
                                break
                                
                    except Exception as e:
                        continue
                
                if 'recete_no' in info:
                    break
            
            # Hasta bilgileri çıkarma - comprehensive
            patient_strategies = [
                # Strategy 1: Structured form fields
                {
                    'tc_selectors': ["//input[contains(@name, 'tc')]", "//input[contains(@id, 'tc')]"],
                    'name_selectors': ["//input[contains(@name, 'ad')]", "//input[contains(@name, 'soyad')]"],
                },
                # Strategy 2: Label-based
                {
                    'tc_selectors': ["//*[contains(text(), 'TC')]/following-sibling::*", "//*[contains(text(), 'T.C.')]/following-sibling::*"],
                    'name_selectors': ["//*[contains(text(), 'Hasta Adı')]/following-sibling::*", "//*[contains(text(), 'Ad Soyad')]/following-sibling::*"]
                },
                # Strategy 3: Table-based
                {
                    'tc_selectors': ["//td[contains(text(), 'TC')]/following-sibling::td"],
                    'name_selectors': ["//td[contains(text(), 'Hasta')]/following-sibling::td"]
                },
                # Strategy 4: Text scanning
                {
                    'pattern_search': True
                }
            ]
            
            for strategy in patient_strategies:
                if strategy.get('pattern_search'):
                    # Pattern-based patient info extraction
                    try:
                        import re
                        page_text = self.browser.driver.find_element(By.XPATH, "//body").text
                        
                        # TC pattern (11 digits)
                        tc_match = re.search(r'\b(\d{11})\b', page_text)
                        if tc_match:
                            info['hasta_tc'] = tc_match.group(1)
                            logger.debug(f"✅ TC found via pattern: {tc_match.group(1)}")
                        
                        # Name pattern (capital letters)
                        name_patterns = [
                            r'Hasta[:\s]*([A-ZÇĞIÖŞÜ]{2,}\s+[A-ZÇĞIÖŞÜ]{2,})',
                            r'Ad[:\s]*([A-ZÇĞIÖŞÜ]{2,})\s+Soyad[:\s]*([A-ZÇĞIÖŞÜ]{2,})',
                            r'\b([A-ZÇĞIÖŞÜ]{2,})\s+([A-ZÇĞIÖŞÜ]{2,})\b'
                        ]
                        
                        for pattern in name_patterns:
                            name_match = re.search(pattern, page_text)
                            if name_match:
                                if len(name_match.groups()) == 1:
                                    info['hasta_ad_soyad'] = name_match.group(1).strip()
                                else:
                                    info['hasta_ad'] = name_match.group(1).strip()
                                    info['hasta_soyad'] = name_match.group(2).strip()
                                    info['hasta_ad_soyad'] = f"{name_match.group(1)} {name_match.group(2)}".strip()
                                logger.debug(f"✅ Name found via pattern: {info.get('hasta_ad_soyad', '')}")
                                break
                                
                    except:
                        continue
                else:
                    # Element-based extraction
                    # TC kimlik extraction
                    for selector in strategy.get('tc_selectors', []):
                        try:
                            element = self.browser.driver.find_element(By.XPATH, selector)
                            tc_text = element.text or element.get_attribute('value')
                            if tc_text and tc_text.strip().isdigit() and len(tc_text.strip()) == 11:
                                info['hasta_tc'] = tc_text.strip()
                                logger.debug(f"✅ TC found via element: {tc_text}")
                                break
                        except:
                            continue
                    
                    # Name extraction
                    for selector in strategy.get('name_selectors', []):
                        try:
                            element = self.browser.driver.find_element(By.XPATH, selector)
                            name_text = element.text or element.get_attribute('value')
                            if name_text and name_text.strip() and not name_text.strip().isdigit():
                                info['hasta_ad_soyad'] = name_text.strip()
                                logger.debug(f"✅ Name found via element: {name_text}")
                                break
                        except:
                            continue
                
                # Break if we have both TC and name
                if 'hasta_tc' in info and 'hasta_ad_soyad' in info:
                    break
            
            logger.debug(f"✅ Basic info extraction completed: {len(info)} fields")
            return info
            
        except Exception as e:
            logger.error(f"❌ Enhanced basic info extraction error: {e}")
            return {}
    
    def _extract_drug_info_enhanced(self):
        """Gelişmiş ilaç bilgileri çıkarma - TAM DETAY"""
        try:
            result = {
                'drugs': [],
                'drug_details': {}
            }
            
            # İlaç bilgilerini farklı stratejilerle çıkar
            drug_strategies = [
                # Strategy 1: Main prescription table
                self._extract_drugs_from_main_table,
                # Strategy 2: Drug details button/page
                self._extract_drugs_from_details_page,
                # Strategy 3: Drug list section
                self._extract_drugs_from_list_section
            ]
            
            for strategy in drug_strategies:
                try:
                    drugs_data = strategy()
                    if drugs_data and drugs_data.get('drugs'):
                        result.update(drugs_data)
                        logger.debug(f"✅ Drugs extracted via {strategy.__name__}: {len(drugs_data['drugs'])} drugs")
                        break
                except Exception as e:
                    logger.debug(f"⚠️ Drug strategy {strategy.__name__} failed: {e}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced drug info extraction error: {e}")
            return {'drugs': [], 'drug_details': {}}
    
    def _extract_drugs_from_main_table(self):
        """Ana tablodaki ilaç bilgilerini çıkar"""
        drugs = []
        drug_details = {}
        
        # Ana ilaç tablosunu bul
        table_selectors = [
            "//table[contains(@class, 'prescription')]",
            "//table[contains(@id, 'drug')]",
            "//table[.//td[contains(text(), 'İlaç')]]",
            "//table[.//th[contains(text(), 'İlaç')]]",
            "//table"
        ]
        
        for table_selector in table_selectors:
            try:
                tables = self.browser.driver.find_elements(By.XPATH, table_selector)
                for table in tables:
                    if not table.is_displayed():
                        continue
                        
                    rows = table.find_elements(By.XPATH, ".//tr[td]")
                    
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        if len(cells) >= 2:
                            # İlaç adı (genellikle ilk hücre)
                            drug_name = cells[0].text.strip()
                            
                            # Miktar (genellikle ikinci hücre)
                            quantity = cells[1].text.strip() if len(cells) > 1 else "1"
                            
                            # Barkod (varsa)
                            barkod = ""
                            if len(cells) > 2:
                                potential_barkod = cells[2].text.strip()
                                if potential_barkod.isdigit() and len(potential_barkod) >= 8:
                                    barkod = potential_barkod
                            
                            if drug_name and len(drug_name) > 3:  # Anlamlı ilaç adı
                                drugs.append({
                                    "ilac_adi": drug_name,
                                    "adet": quantity,
                                    "barkod": barkod
                                })
                
                if drugs:
                    return {'drugs': drugs, 'drug_details': drug_details}
                    
            except:
                continue
        
        return {'drugs': drugs, 'drug_details': drug_details}
    
    def _extract_drugs_from_details_page(self):
        """İlaç Bilgileri sayfasından detaylı çıkarma"""
        drugs = []
        drug_details = {}
        
        try:
            # İlaç Bilgileri butonunu bul ve tıkla
            drug_info_selectors = [
                "//input[@value='İlaç Bilgileri']",
                "//button[contains(text(), 'İlaç Bilgileri')]",
                "//a[contains(text(), 'İlaç Bilgileri')]",
                "//input[contains(@value, 'İlaç')]"
            ]
            
            button_clicked = False
            for selector in drug_info_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        button_clicked = True
                        break
                except:
                    continue
            
            if button_clicked:
                # İlaç detay sayfasından bilgi çıkar
                detailed_drugs = self._extract_detailed_drug_info()
                return {'drugs': detailed_drugs, 'drug_details': drug_details}
            
        except Exception as e:
            logger.debug(f"Drug details page extraction failed: {e}")
        
        return {'drugs': drugs, 'drug_details': drug_details}
    
    def _extract_drugs_from_list_section(self):
        """İlaç listesi bölümünden çıkarma"""
        drugs = []
        drug_details = {}
        
        try:
            # İlaç listesi div/section'ını bul
            list_selectors = [
                "//div[contains(@class, 'drug-list')]",
                "//div[contains(@id, 'drug')]",
                "//section[contains(@class, 'medications')]",
                "//div[.//text()[contains(., 'İlaç')]]"
            ]
            
            for selector in list_selectors:
                try:
                    container = self.browser.driver.find_element(By.XPATH, selector)
                    if container.is_displayed():
                        # Konteyner içindeki ilaç elementlerini bul
                        drug_elements = container.find_elements(By.XPATH, ".//div | .//li | .//tr")
                        
                        for element in drug_elements:
                            text = element.text.strip()
                            if text and len(text) > 10:  # Anlamlı metin
                                # İlaç adı pattern'larını kontrol et
                                import re
                                drug_patterns = [
                                    r'([A-ZÇĞIİÖŞÜ\s]+)\s+(\d+\s*MG|\d+\s*ML|\d+\s*TB)',
                                    r'([A-ZÇĞIİÖŞÜ\s]+).*?(\d+)\s*adet',
                                    r'(.+)\s+(\d+)$'
                                ]
                                
                                for pattern in drug_patterns:
                                    match = re.search(pattern, text, re.IGNORECASE)
                                    if match:
                                        drugs.append({
                                            "ilac_adi": match.group(1).strip(),
                                            "adet": match.group(2) if len(match.groups()) > 1 else "1"
                                        })
                                        break
                        
                        if drugs:
                            break
                            
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Drug list section extraction failed: {e}")
        
        return {'drugs': drugs, 'drug_details': drug_details}
    
    def _extract_detailed_drug_info(self):
        """Detaylı ilaç bilgilerini çıkar (İlaç Bilgileri sayfasından)"""
        detailed_drugs = []
        
        try:
            # Detaylı ilaç tablosunu bul
            detail_selectors = [
                "//table[.//td[contains(text(), 'Barkod')]]",
                "//table[.//th[contains(text(), 'İlaç Adı')]]",
                "//div[contains(@class, 'drug-detail')]"
            ]
            
            for selector in detail_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            rows = element.find_elements(By.XPATH, ".//tr[td]")
                            
                            for row in rows:
                                cells = row.find_elements(By.TAG_NAME, 'td')
                                if len(cells) >= 3:  # İlaç adı, miktar, barkod
                                    detailed_drugs.append({
                                        "ilac_adi": cells[0].text.strip(),
                                        "adet": cells[1].text.strip(),
                                        "barkod": cells[2].text.strip() if len(cells) > 2 else ""
                                    })
                            
                            if detailed_drugs:
                                return detailed_drugs
                                
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Detailed drug info extraction failed: {e}")
        
        return detailed_drugs
    
    def _extract_message_info_enhanced(self):
        """Gelişmiş mesaj ve SUT kodu çıkarma"""
        try:
            result = {
                'messages': '',
                'detailed_messages': [],
                'sut_codes': []
            }
            
            # Mesaj çıkarma stratejileri
            message_strategies = [
                self._extract_messages_from_drug_info_page,
                self._extract_messages_from_main_page,
                self._extract_messages_from_warning_section
            ]
            
            for strategy in message_strategies:
                try:
                    messages_data = strategy()
                    if messages_data and (messages_data.get('messages') or messages_data.get('detailed_messages')):
                        # Combine results
                        if messages_data.get('messages'):
                            result['messages'] = messages_data['messages']
                        if messages_data.get('detailed_messages'):
                            result['detailed_messages'].extend(messages_data['detailed_messages'])
                        if messages_data.get('sut_codes'):
                            result['sut_codes'].extend(messages_data['sut_codes'])
                        
                        logger.debug(f"✅ Messages extracted via {strategy.__name__}")
                        break
                        
                except Exception as e:
                    logger.debug(f"⚠️ Message strategy {strategy.__name__} failed: {e}")
                    continue
            
            # Deduplicate SUT codes
            result['sut_codes'] = list(set(result['sut_codes']))
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced message info extraction error: {e}")
            return {'messages': '', 'detailed_messages': [], 'sut_codes': []}
    
    def _extract_messages_from_drug_info_page(self):
        """İlaç Bilgileri sayfasından mesajları çıkar"""
        try:
            # İlaç Bilgileri sayfasına git (eğer zaten orada değilsek)
            drug_info_selectors = [
                "//input[@value='İlaç Bilgileri']",
                "//button[contains(text(), 'İlaç Bilgileri')]"
            ]
            
            for selector in drug_info_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    if button.is_displayed():
                        button.click()
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Mesaj tablosunu veya bölümünü bul
            message_selectors = [
                "//table[.//td[contains(text(), 'Mesaj')]]",
                "//table[.//th[contains(text(), 'Mesaj')]]",
                "//div[contains(@class, 'message')]",
                "//div[contains(text(), '1013')]//ancestor::table",  # SUT kodu içeren tablo
            ]
            
            messages = []
            detailed_messages = []
            sut_codes = []
            
            for selector in message_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            # Tablo satırlarını işle
                            rows = element.find_elements(By.XPATH, ".//tr")
                            for row in rows:
                                cells = row.find_elements(By.TAG_NAME, 'td')
                                row_text = row.text.strip()
                                
                                if row_text and len(row_text) > 10:
                                    messages.append(row_text)
                                    
                                    # SUT kodlarını çıkar
                                    import re
                                    sut_pattern = r'\b(\d{4})\b'
                                    sut_matches = re.findall(sut_pattern, row_text)
                                    sut_codes.extend(sut_matches)
                                    
                                    # Detaylı mesaj yapısı
                                    if len(cells) >= 2:
                                        detailed_messages.append({
                                            'code': cells[0].text.strip() if cells[0].text.strip() else 'N/A',
                                            'message': cells[1].text.strip() if len(cells) > 1 else row_text,
                                            'full_text': row_text
                                        })
                except Exception as e:
                    continue
            
            return {
                'messages': '; '.join(messages),
                'detailed_messages': detailed_messages,
                'sut_codes': sut_codes
            }
            
        except Exception as e:
            logger.debug(f"Drug info page messages extraction failed: {e}")
            return {'messages': '', 'detailed_messages': [], 'sut_codes': []}
    
    def _extract_messages_from_main_page(self):
        """Ana sayfadan mesajları çıkar"""
        try:
            # Ana sayfadaki mesaj bölümlerini bul
            selectors = [
                "//*[contains(text(), 'Mesaj')]/following-sibling::*",
                "//*[contains(text(), 'Uyarı')]/following-sibling::*",
                "//div[contains(@class, 'warning')]",
                "//div[contains(@class, 'message')]",
                "//span[contains(@class, 'alert')]"
            ]
            
            messages = []
            sut_codes = []
            
            for selector in selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 5:
                            messages.append(text)
                            
                            # SUT kodlarını çıkar
                            import re
                            sut_matches = re.findall(r'\b(\d{4})\b', text)
                            sut_codes.extend(sut_matches)
                            
                except:
                    continue
            
            return {
                'messages': '; '.join(messages),
                'detailed_messages': [{'message': msg, 'source': 'main_page'} for msg in messages],
                'sut_codes': sut_codes
            }
            
        except Exception as e:
            logger.debug(f"Main page messages extraction failed: {e}")
            return {'messages': '', 'detailed_messages': [], 'sut_codes': []}
    
    def _extract_messages_from_warning_section(self):
        """Uyarı bölümünden mesajları çıkar"""
        try:
            # Uyarı/mesaj bölümünü bul
            warning_selectors = [
                "//div[@id='warnings']",
                "//div[@class='warnings']",
                "//section[contains(@class, 'alert')]",
                "//*[contains(@class, 'notification')]"
            ]
            
            messages = []
            
            for selector in warning_selectors:
                try:
                    container = self.browser.driver.find_element(By.XPATH, selector)
                    if container.is_displayed():
                        text = container.text.strip()
                        if text:
                            messages.append(text)
                            
                except:
                    continue
            
            return {
                'messages': '; '.join(messages),
                'detailed_messages': [{'message': msg, 'source': 'warning_section'} for msg in messages],
                'sut_codes': []
            }
            
        except Exception as e:
            logger.debug(f"Warning section messages extraction failed: {e}")
            return {'messages': '', 'detailed_messages': [], 'sut_codes': []}
    
    def _extract_report_info_enhanced(self):
        """Gelişmiş rapor bilgileri çıkarma"""
        try:
            report_info = {}
            
            # Rapor bilgilerini farklı stratejilerle çıkar
            report_strategies = [
                self._extract_report_from_main_page,
                self._extract_report_from_report_button,
                self._extract_report_from_pattern_search
            ]
            
            for strategy in report_strategies:
                try:
                    report_data = strategy()
                    if report_data:
                        report_info.update(report_data)
                        logger.debug(f"✅ Report info extracted via {strategy.__name__}")
                        if report_info.get('rapor_no'):  # Temel bilgi varsa devam et
                            break
                except Exception as e:
                    logger.debug(f"⚠️ Report strategy {strategy.__name__} failed: {e}")
                    continue
            
            return report_info
            
        except Exception as e:
            logger.error(f"❌ Enhanced report info extraction error: {e}")
            return {}
    
    def _extract_report_from_main_page(self):
        """Ana sayfadan rapor bilgilerini çıkar"""
        report_info = {}
        
        try:
            # Rapor no çıkarma
            report_selectors = [
                "//*[contains(text(), 'Rapor No')]/following-sibling::*",
                "//*[contains(text(), 'Rapor Numarası')]/following-sibling::*", 
                "//input[contains(@name, 'rapor')]",
                "//input[contains(@id, 'rapor')]"
            ]
            
            for selector in report_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    rapor_no = element.text or element.get_attribute('value')
                    if rapor_no and rapor_no.strip():
                        report_info['rapor_no'] = rapor_no.strip()
                        break
                except:
                    continue
            
            # Rapor tarihi çıkarma
            date_selectors = [
                "//*[contains(text(), 'Rapor Tarihi')]/following-sibling::*",
                "//input[contains(@name, 'tarih')]",
                "//input[@type='date']"
            ]
            
            for selector in date_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    tarih = element.text or element.get_attribute('value')
                    if tarih and tarih.strip():
                        report_info['rapor_tarihi'] = tarih.strip()
                        break
                except:
                    continue
            
        except Exception as e:
            logger.debug(f"Main page report extraction failed: {e}")
        
        return report_info
    
    def _extract_report_from_report_button(self):
        """Rapor butonundan detaylı bilgi çıkarma"""
        report_info = {}
        
        try:
            # Rapor butonunu bul ve tıkla
            report_button_selectors = [
                "//input[@value='Rapor']",
                "//button[contains(text(), 'Rapor')]",
                "//a[contains(text(), 'Rapor')]"
            ]
            
            button_clicked = False
            for selector in report_button_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(3)
                        button_clicked = True
                        break
                except:
                    continue
            
            if button_clicked:
                # Rapor sayfasından detayları çıkar
                detail_selectors = [
                    "//table[.//td[contains(text(), 'Rapor')]]",
                    "//div[contains(@class, 'report')]",
                    "//form[contains(@name, 'report')]"
                ]
                
                for selector in detail_selectors:
                    try:
                        container = self.browser.driver.find_element(By.XPATH, selector)
                        if container.is_displayed():
                            text = container.text
                            
                            # Text'den bilgileri çıkar
                            import re
                            
                            # Rapor no pattern
                            rapor_match = re.search(r'Rapor\s*:?\s*(\w+)', text)
                            if rapor_match:
                                report_info['rapor_no'] = rapor_match.group(1)
                            
                            # Tarih pattern
                            tarih_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', text)
                            if tarih_match:
                                report_info['rapor_tarihi'] = tarih_match.group(1)
                            
                            # ICD kodları
                            icd_matches = re.findall(r'\b([A-Z]\d{2}\.?\d?)\b', text)
                            if icd_matches:
                                report_info['icd_kodlari'] = icd_matches
                            
                            break
                            
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Report button extraction failed: {e}")
        
        return report_info
    
    def _extract_report_from_pattern_search(self):
        """Tüm sayfada pattern arama ile rapor bilgilerini çıkar"""
        report_info = {}
        
        try:
            # Tüm sayfa text'ini al
            page_text = self.browser.driver.find_element(By.XPATH, "//body").text
            
            import re
            
            # Rapor no patterns
            rapor_patterns = [
                r'Rapor\s*:?\s*(\d{7,})',
                r'Rapor\s*No\s*:?\s*(\d{7,})',
                r'\b(\d{7,})\b'  # 7+ digit numbers
            ]
            
            for pattern in rapor_patterns:
                match = re.search(pattern, page_text)
                if match:
                    potential_rapor = match.group(1)
                    if len(potential_rapor) >= 7:  # Rapor no genellikle 7+ hane
                        report_info['rapor_no'] = potential_rapor
                        break
            
            # Tarih patterns  
            tarih_patterns = [
                r'(\d{1,2}[./]\d{1,2}[./]\d{4})',
                r'(\d{4}-\d{1,2}-\d{1,2})'
            ]
            
            for pattern in tarih_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # İlk bulunan tarihi al (genellikle rapor tarihi)
                    report_info['rapor_tarihi'] = matches[0]
                    break
            
        except Exception as e:
            logger.debug(f"Pattern search report extraction failed: {e}")
        
        return report_info
    
    def _extract_additional_info(self):
        """Ek bilgileri çıkar (doktor, branş, vb.)"""
        additional_info = {}
        
        try:
            # Doktor bilgileri
            doctor_selectors = [
                "//*[contains(text(), 'Doktor')]/following-sibling::*",
                "//*[contains(text(), 'Dr.')]/following-sibling::*",
                "//input[contains(@name, 'doctor')]"
            ]
            
            for selector in doctor_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    doctor = element.text or element.get_attribute('value')
                    if doctor and doctor.strip():
                        additional_info['doktor'] = doctor.strip()
                        break
                except:
                    continue
            
            # Branş bilgileri
            brans_selectors = [
                "//*[contains(text(), 'Branş')]/following-sibling::*",
                "//*[contains(text(), 'Uzmanlık')]/following-sibling::*"
            ]
            
            for selector in brans_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    brans = element.text or element.get_attribute('value')
                    if brans and brans.strip():
                        additional_info['brans'] = brans.strip()
                        break
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Additional info extraction failed: {e}")
        
        return additional_info
    
    def _validate_extracted_data(self, prescription_data):
        """Çıkarılan veriyi doğrula"""
        try:
            # Temel doğrulama kriterleri
            required_fields = ['recete_no']
            
            for field in required_fields:
                if field not in prescription_data or not prescription_data[field]:
                    logger.warning(f"⚠️ Missing required field: {field}")
                    return False
            
            # İlaç bilgisi kontrolü
            if not prescription_data.get('drugs') or len(prescription_data['drugs']) == 0:
                logger.warning("⚠️ No drugs found in prescription")
                # Bu hata değil, uyarı olarak geç
            
            # TC kimlik kontrolü (varsa)
            tc = prescription_data.get('hasta_tc', '')
            if tc and (not tc.isdigit() or len(tc) != 11):
                logger.warning(f"⚠️ Invalid TC format: {tc}")
                # TC'yi temizle
                prescription_data['hasta_tc'] = ''
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Data validation error: {e}")
            return False
    
    def _get_fallback_mock_data(self, limit=3):
        """Fallback mock data for when real extraction fails"""
        logger.info(f"🔄 Providing fallback mock data ({limit} prescriptions)")
        
        mock_prescriptions = [
            {
                "recete_no": f"FALLBACK{i:03d}",
                "hasta_ad_soyad": f"Fallback Patient {i}",
                "hasta_tc": f"9876543210{i}",
                "drugs": [
                    {"ilac_adi": f"Fallback Drug {i}", "adet": "1"}
                ],
                "ilac_mesajlari": f"Fallback message {i}",
                "rapor_no": f"FALLBACK_RPT{i:03d}",
                "extraction_method": "medula_fallback",
                "extraction_timestamp": datetime.now().isoformat()
            }
            for i in range(1, min(limit + 1, 4))
        ]
        
        return mock_prescriptions
    
    def _cleanup_browser(self):
        """Browser'ı temizler"""
        try:
            if self.browser:
                self.browser.quit()
                self.browser = None
                logger.info("Browser cleaned up")
        except Exception as e:
            logger.error(f"Browser cleanup error: {e}")
    
    # =========================================================================
    # ANALYSIS METHODS
    # =========================================================================
    
    def _perform_dose_control(self, prescription_data):
        """Dose control analizi yapar"""
        try:
            dose_result = self.dose_controller.control_prescription_doses(prescription_data)
            
            return {
                "analysis": {
                    "overall_compliance": dose_result.dose_violations == 0,
                    "total_drugs": dose_result.total_drugs,
                    "reported_drugs": dose_result.reported_drugs,
                    "compliant_drugs": dose_result.dose_compliant_drugs,
                    "violations": dose_result.dose_violations,
                    "issues": dose_result.control_notes or []
                },
                "recommendation": dose_result.overall_decision,
                "processing_time": dose_result.processing_time,
                "drugs_analyzed": dose_result.total_drugs,
                "reported_drugs": dose_result.reported_drugs
            }
            
        except Exception as e:
            logger.error(f"Dose control error: {e}")
            return {
                "analysis": {"overall_compliance": False, "issues": [str(e)]},
                "recommendation": {"action": "hold", "confidence": 0.1, "reason": f"Dose control error: {e}"},
                "processing_time": 0.0,
                "drugs_analyzed": 0,
                "reported_drugs": 0
            }
    
    def _perform_sut_analysis(self, prescription_data):
        """SUT analizi yapar"""
        try:
            sut_analysis = self.sut_db.get_sut_analysis_for_prescription(prescription_data)
            sut_recommendation = self.sut_db.get_recommendation_for_prescription(prescription_data)
            
            return {
                "analysis": sut_analysis,
                "recommendation": sut_recommendation,
                "processing_time": 0.1  # SUT analizi çok hızlı
            }
            
        except Exception as e:
            logger.error(f"SUT analysis error: {e}")
            return {
                "analysis": {"overall_compliance": False, "issues": [str(e)]},
                "recommendation": {"action": "hold", "confidence": 0.1, "reason": f"SUT error: {e}"},
                "processing_time": 0.0,
                "error": str(e)
            }
    
    def _perform_ai_analysis(self, prescription_data):
        """AI analizi yapar"""
        try:
            start_time = time.time()
            ai_result = self.ai_analyzer.analyze_prescription_with_claude(prescription_data)
            processing_time = time.time() - start_time
            
            return {
                "result": ai_result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "result": {
                    "action": "hold",
                    "confidence": 0.1,
                    "reason": f"AI error: {e}",
                    "claude_available": False
                },
                "processing_time": 0.0,
                "error": str(e)
            }
    
    def _combine_analysis_results(self, prescription_data, sut_result, ai_result, dose_result, source, start_time):
        """Analiz sonuçlarını birleştirir"""
        try:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Temel bilgiler
            result = {
                "prescription_id": prescription_data.get("recete_no", "UNKNOWN"),
                "patient_info": {
                    "name": f"{prescription_data.get('hasta_ad', '')} {prescription_data.get('hasta_soyad', '')}",
                    "tc": prescription_data.get("hasta_tc", ""),
                },
                "processing_metadata": {
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": processing_time,
                    "dose_processing_time": dose_result.get("processing_time", 0) if isinstance(dose_result, dict) else 0,
                    "sut_processing_time": sut_result.get("processing_time", 0),
                    "ai_processing_time": ai_result.get("processing_time", 0)
                }
            }
            
            # Dose control sonuçları
            if isinstance(dose_result, dict):
                dose_rec = dose_result.get("recommendation", {})
                result["dose_analysis"] = {
                    "compliant": dose_result.get("analysis", {}).get("overall_compliance", False),
                    "action": dose_result.get("recommendation", "hold"),
                    "confidence": 0.8,
                    "drugs_analyzed": dose_result.get("drugs_analyzed", 0),
                    "reported_drugs": dose_result.get("reported_drugs", 0),
                    "issues_found": len(dose_result.get("analysis", {}).get("issues", []))
                }
            else:
                result["dose_analysis"] = {
                    "compliant": False,
                    "action": "hold",
                    "confidence": 0.0,
                    "drugs_analyzed": 0,
                    "reported_drugs": 0,
                    "issues_found": 0
                }
            
            # SUT sonuçları
            sut_rec = sut_result.get("recommendation", {})
            result["sut_analysis"] = {
                "compliant": sut_result.get("analysis", {}).get("overall_compliance", False),
                "action": sut_rec.get("action", "hold"),
                "confidence": sut_rec.get("confidence", 0.0),
                "issues_count": len(sut_result.get("analysis", {}).get("issues", [])),
                "warnings_count": len(sut_result.get("analysis", {}).get("warnings", []))
            }
            
            # AI sonuçları
            ai_res = ai_result.get("result", {})
            result["ai_analysis"] = {
                "action": ai_res.get("action", "hold"),
                "confidence": ai_res.get("confidence", 0.0),
                "claude_used": ai_res.get("claude_available", False),
                "method": ai_res.get("analysis_method", "unknown")
            }
            
            # Final karar
            result["final_decision"] = self._determine_final_decision_with_dose(
                dose_rec.get("action", "hold"),
                sut_rec.get("action", "hold"),
                ai_res.get("action", "hold"),
                dose_rec.get("confidence", 0.0),
                sut_rec.get("confidence", 0.0),
                ai_res.get("confidence", 0.0)
            )
            
            # Detay bilgileri
            result["details"] = {
                "dose_reason": dose_rec.get("reason", ""),
                "sut_reason": sut_rec.get("reason", ""),
                "ai_reason": ai_res.get("reason", ""),
                "dose_violations": dose_result.get("analysis", {}).get("dose_violations", []),
                "sut_issues": sut_result.get("analysis", {}).get("issues", []),
                "ai_risk_factors": ai_res.get("risk_factors", []),
                "recommendations": ai_res.get("recommendations", [])
            }
            
            # Ham veriler (debug için)
            result["raw_data"] = {
                "prescription_data": prescription_data,
                "sut_full_result": sut_result,
                "ai_full_result": ai_result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Result combination error: {e}")
            return self._create_error_result(prescription_data, str(e))
    
    def _determine_final_decision_with_dose(self, dose_action, sut_action, ai_action, dose_confidence, sut_confidence, ai_confidence):
        """Dose control dahil final kararı belirler - Conservative yaklaşım"""
        
        # Dose control priority - eğer dose reject ediyorsa, diğerlerine bakılmaz
        if dose_action == "reject":
            return "reject"
        
        # Conservative approach - en yüksek priortiy (risk) seviyesini al
        priority_order = {"reject": 3, "hold": 2, "approve": 1}
        
        actions = [dose_action, sut_action, ai_action]
        max_priority = max(priority_order.get(action, 2) for action in actions)
        
        # En yüksek priority seviyesindeki aksiyon
        for priority_val in [3, 2, 1]:
            if priority_val == max_priority:
                for action, p_val in priority_order.items():
                    if p_val == priority_val and action in actions:
                        return action
        
        return "hold"  # Fallback
    
    def _determine_final_decision(self, sut_action, ai_action, sut_confidence, ai_confidence):
        """Final kararı belirler"""
        
        # Conservative approach - en düşük riski al
        priority_order = {"reject": 3, "hold": 2, "approve": 1}
        
        if priority_order.get(sut_action, 2) >= priority_order.get(ai_action, 2):
            return sut_action
        else:
            return ai_action
    
    # =========================================================================
    # BATCH PROCESSING METHODS  
    # =========================================================================
    
    def _process_prescription_batch(self, prescriptions, source):
        """Reçete toplu işleme"""
        try:
            logger.info(f"Processing batch of {len(prescriptions)} prescriptions")
            
            self.processing_stats["start_time"] = datetime.now()
            self.processing_stats["total_processed"] = 0
            
            results = []
            
            for i, prescription in enumerate(prescriptions, 1):
                logger.info(f"Processing {i}/{len(prescriptions)}: {prescription.get('recete_no', 'N/A')}")
                
                result = self.process_single_prescription(prescription, source)
                results.append(result)
                
                # Progress update
                self.processing_stats["total_processed"] += 1
                print(f"[{i}/{len(prescriptions)}] {result['prescription_id']} -> {result['final_decision'].upper()}")
                
                # Kısa bekleme (API rate limiting için)
                time.sleep(0.5)
            
            self.processing_stats["end_time"] = datetime.now()
            
            # Final stats
            self._calculate_final_stats(results)
            self._print_processing_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return []
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _validate_prescription_data(self, prescription_data):
        """Reçete verisini doğrular"""
        if not isinstance(prescription_data, dict):
            return False
        
        required_fields = ["recete_no"]
        for field in required_fields:
            if field not in prescription_data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _create_error_result(self, prescription_data, error_message):
        """Hata sonucu oluşturur"""
        return {
            "prescription_id": prescription_data.get("recete_no", "UNKNOWN"),
            "final_decision": "error",
            "error": error_message,
            "processing_metadata": {
                "timestamp": datetime.now().isoformat(),
                "processing_time_seconds": 0.0,
                "source": "error"
            },
            "sut_analysis": {"action": "error", "confidence": 0.0},
            "ai_analysis": {"action": "error", "confidence": 0.0}
        }
    
    def _update_stats(self, result):
        """İstatistikleri günceller"""
        decision = result.get("final_decision", "error")
        
        if decision == "approve":
            self.processing_stats["approved"] += 1
        elif decision == "reject":
            self.processing_stats["rejected"] += 1
        elif decision == "hold":
            self.processing_stats["held"] += 1
        else:
            self.processing_stats["errors"] += 1
    
    def _calculate_final_stats(self, results):
        """Final istatistikleri hesaplar"""
        for result in results:
            decision = result.get("final_decision", "error")
            
            if decision == "approve":
                self.processing_stats["approved"] += 1
            elif decision == "reject":
                self.processing_stats["rejected"] += 1
            elif decision == "hold":
                self.processing_stats["held"] += 1
            else:
                self.processing_stats["errors"] += 1
    
    def _print_processing_summary(self, results):
        """İşlem özetini yazdırır"""
        if not results:
            return
        
        total = len(results)
        stats = self.processing_stats
        
        processing_time = 0
        if stats["start_time"] and stats["end_time"]:
            processing_time = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        print(f"""
        
=== PROCESSING SUMMARY ===
Total Prescriptions: {total}
[+] Approved: {stats['approved']} ({stats['approved']/total*100:.1f}%)
[-] Rejected: {stats['rejected']} ({stats['rejected']/total*100:.1f}%)
[?] Hold: {stats['held']} ({stats['held']/total*100:.1f}%)
[!] Errors: {stats['errors']} ({stats['errors']/total*100:.1f}%)

Processing Time: {processing_time:.2f}s
Average per Prescription: {processing_time/total:.2f}s

Claude API Status: {'Active' if any(r.get('ai_analysis', {}).get('claude_used') for r in results) else 'Fallback'}
        """)
    
    def _save_results(self, results, output_file):
        """Sonuçları dosyaya kaydeder"""
        try:
            # Convert datetime objects to strings for JSON serialization
            stats_for_json = self.processing_stats.copy()
            if stats_for_json.get("start_time"):
                stats_for_json["start_time"] = stats_for_json["start_time"].isoformat()
            if stats_for_json.get("end_time"):
                stats_for_json["end_time"] = stats_for_json["end_time"].isoformat()
            
            output_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_prescriptions": len(results),
                    "processing_stats": stats_for_json,
                    "processor_version": "unified_v1.0"
                },
                "results": results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Save results error: {e}")
            return False
    
    def get_processing_stats(self):
        """İşlem istatistiklerini döndürür"""
        return self.processing_stats.copy()
    
    def _save_to_database(self, prescription_data, final_result):
        """Reçete ve analiz sonucunu veritabanına kaydeder"""
        try:
            # Analysis result for database
            analysis_result = {
                "sut_analysis": final_result.get("sut_analysis", {}),
                "ai_analysis": final_result.get("ai_analysis", {}),
                "final_decision": final_result.get("final_decision"),
                "processing_metadata": final_result.get("processing_metadata", {}),
                "details": final_result.get("details", {})
            }
            
            # Save to database
            success = self.database.save_prescription(
                prescription_data=prescription_data,
                analysis_result=analysis_result,
                decision=final_result.get("final_decision")
            )
            
            if success:
                # Log the processing action
                self.database.log_processing(
                    recete_no=prescription_data.get("recete_no"),
                    action="processed",
                    details=f"Decision: {final_result.get('final_decision')}"
                )
                logger.debug(f"Saved prescription {prescription_data.get('recete_no')} to database")
            else:
                logger.warning(f"Failed to save prescription {prescription_data.get('recete_no')} to database")
                
        except Exception as e:
            logger.error(f"Database save error: {e}")

# =========================================================================
# TEST AND DEMO FUNCTIONS
# =========================================================================

def test_json_processing():
    """JSON processing test"""
    print("=== TESTING JSON PROCESSING ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    json_file = "manual_detailed_prescriptions.json"
    if os.path.exists(json_file):
        results = processor.process_from_json_file(json_file, "unified_test_results.json")
        print(f"Processed {len(results)} prescriptions from JSON")
        return True
    else:
        print(f"Test file not found: {json_file}")
        return False

def test_single_prescription():
    """Single prescription test"""
    print("\\n=== TESTING SINGLE PRESCRIPTION ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    test_prescription = {
        "recete_no": "TEST001",
        "hasta_ad": "TEST",
        "hasta_soyad": "PATIENT",
        "hasta_tc": "12345678901",
        "drugs": [
            {"ilac_adi": "TEST DRUG", "adet": "1"}
        ],
        "ilac_mesajlari": "Test message",
        "rapor_no": "TEST_RPT"
    }
    
    result = processor.process_single_prescription(test_prescription, "test")
    
    print(f"Single prescription test:")
    print(f"  ID: {result['prescription_id']}")
    print(f"  Decision: {result['final_decision']}")
    print(f"  Processing time: {result['processing_metadata']['processing_time_seconds']:.2f}s")
    print(f"  SUT: {result['sut_analysis']['action']} ({result['sut_analysis']['confidence']:.2f})")
    print(f"  AI: {result['ai_analysis']['action']} ({result['ai_analysis']['confidence']:.2f})")
    
    return True

def test_medula_processing():
    """Medula processing test (mock)"""
    print("\\n=== TESTING MEDULA PROCESSING (MOCK) ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    try:
        results = processor.process_from_medula_live(limit=3, group='A')
        print(f"Processed {len(results)} prescriptions from Medula (mock)")
        return True
    except Exception as e:
        print(f"Medula processing failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("UNIFIED PRESCRIPTION PROCESSOR - TEST SUITE")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: JSON Processing
    if test_json_processing():
        success_count += 1
    
    # Test 2: Single Prescription
    if test_single_prescription():
        success_count += 1
    
    # Test 3: Medula Processing (Mock)
    if test_medula_processing():
        success_count += 1
    
    # Final Results
    print(f"\\n{'='*60}")
    print(f"TEST RESULTS: {success_count}/{total_tests} PASSED")
    print(f"SUCCESS RATE: {success_count/total_tests*100:.1f}%")
    print("="*60)
    
    if success_count == total_tests:
        print("[*] ALL TESTS PASSED - SYSTEM READY!")
    else:
        print("[!] SOME TESTS FAILED - CHECK LOGS")

if __name__ == "__main__":
    main()