"""
Prescription Dose Control Algorithm
Reçete dozları vs Rapor dozları karşılaştırma sistemi
"""

import json
import os
import sys
import re
import time
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from database.sqlite_handler import SQLiteHandler
from medula_automation.browser import MedulaBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@dataclass
class DrugInfo:
    """İlaç bilgi yapısı"""
    drug_name: str
    active_ingredient: str = ""
    prescription_dose: str = ""
    report_dose: str = ""
    report_code: str = ""
    msj_status: str = ""
    dose_compliant: Optional[bool] = None
    dose_check_details: str = ""

@dataclass
class DoseControlResult:
    """Doz kontrol sonuç yapısı"""
    prescription_id: str
    total_drugs: int = 0
    reported_drugs: int = 0
    dose_compliant_drugs: int = 0
    dose_violations: int = 0
    processing_time: float = 0.0
    overall_decision: str = "pending"
    drug_details: List[DrugInfo] = None
    control_timestamp: str = ""
    control_notes: List[str] = None
    
    def __post_init__(self):
        if self.drug_details is None:
            self.drug_details = []
        if self.control_notes is None:
            self.control_notes = []

class PrescriptionDoseController:
    """Reçete doz kontrol sistemi"""
    
    def __init__(self, control_mode: str = "detailed"):
        self.database = SQLiteHandler()
        self.browser = None
        self.wait = None
        
        # Control mode: "fast" or "detailed"
        self.control_mode = control_mode
        
        # Cache systems
        self.active_ingredient_cache = {}  # İlaç adı -> Etken madde
        self.report_dose_cache = {}        # Rapor kodu + etken madde -> Doz
        self.message_cache = {}            # İlaç adı -> Mesaj kodları
        
        logger.info(f"Prescription Dose Controller initialized (mode: {control_mode})")
    
    def initialize_browser(self, browser_instance=None):
        """Browser'ı başlat"""
        try:
            if browser_instance:
                self.browser = browser_instance
                self.wait = WebDriverWait(self.browser.driver, 30)
                logger.info("✅ Browser instance received")
                return True
            else:
                logger.warning("⚠️ No browser instance provided")
                return False
        except Exception as e:
            logger.error(f"❌ Browser initialization error: {e}")
            return False
    
    # =========================================================================
    # MAIN DOSE CONTROL METHODS
    # =========================================================================
    
    def control_prescription_doses(self, prescription_data: Dict) -> DoseControlResult:
        """Ana reçete doz kontrol fonksiyonu"""
        try:
            start_time = time.time()
            prescription_id = prescription_data.get('recete_no', 'UNKNOWN')
            logger.info(f"🔍 Starting dose control for prescription: {prescription_id}")
            
            # Sonuç yapısını başlat
            result = DoseControlResult(
                prescription_id=prescription_id,
                control_timestamp=datetime.now().isoformat()
            )
            
            # İlaç listesini al
            drugs = prescription_data.get('drugs', [])
            if not drugs:
                result.control_notes.append("⚠️ No drugs found in prescription")
                return result
            
            result.total_drugs = len(drugs)
            logger.info(f"📊 Found {len(drugs)} drugs to analyze")
            
            # Her ilaç için kontrol yap
            for drug_dict in drugs:
                try:
                    if self.control_mode == "fast":
                        drug_info = self._analyze_single_drug_fast(drug_dict, prescription_data)
                    else:  # detailed mode
                        drug_info = self._analyze_single_drug(drug_dict, prescription_data)
                    
                    result.drug_details.append(drug_info)
                    
                    # İstatistikleri güncelle
                    if drug_info.report_code:
                        result.reported_drugs += 1
                        
                        if drug_info.dose_compliant is True:
                            result.dose_compliant_drugs += 1
                        elif drug_info.dose_compliant is False:
                            result.dose_violations += 1
                            result.control_notes.append(
                                f"❌ DOSE VIOLATION: {drug_info.drug_name} - {drug_info.dose_check_details}"
                            )
                            
                except Exception as e:
                    logger.error(f"❌ Drug analysis error: {e}")
                    result.control_notes.append(f"⚠️ Analysis error for drug: {str(e)}")
            
            # Processing time hesapla
            result.processing_time = time.time() - start_time
            
            # Overall decision belirle
            if result.dose_violations > 0:
                result.overall_decision = "reject"
            elif result.reported_drugs > 0 and result.dose_compliant_drugs == result.reported_drugs:
                result.overall_decision = "approve"
            else:
                result.overall_decision = "hold"
            
            # Final özet
            logger.info(f"✅ Dose control completed for {prescription_id}:")
            logger.info(f"  📊 Total drugs: {result.total_drugs}")
            logger.info(f"  📋 Reported drugs: {result.reported_drugs}")
            logger.info(f"  ✅ Compliant: {result.dose_compliant_drugs}")
            logger.info(f"  ❌ Violations: {result.dose_violations}")
            logger.info(f"  ⏱️ Processing time: {result.processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prescription dose control error: {e}")
            return DoseControlResult(prescription_id=prescription_data.get('recete_no', 'ERROR'))
    
    def _analyze_single_drug(self, drug_dict: Dict, prescription_data: Dict) -> DrugInfo:
        """Tek ilaç analizi"""
        try:
            drug_name = drug_dict.get('ilac_adi', '').strip()
            logger.debug(f"🔍 Analyzing drug: {drug_name}")
            
            # Temel bilgileri al
            drug_info = DrugInfo(
                drug_name=drug_name,
                prescription_dose=drug_dict.get('adet', '1')
            )
            
            # 1. Rapor kodu kontrolü
            drug_info.report_code = self._extract_report_code(drug_dict)
            
            # 2. MSJ durumu kontrolü
            drug_info.msj_status = self._extract_msj_status(drug_dict)
            
            # 3. Eğer raporlu ilaç ise doz kontrolü yap
            if drug_info.report_code:
                logger.debug(f"📋 Drug {drug_name} has report code: {drug_info.report_code}")
                
                # Etken madde al (cache'den veya Medula'dan)
                drug_info.active_ingredient = self._get_active_ingredient(drug_name)
                
                # Rapor dozunu al
                drug_info.report_dose = self._get_report_dose(
                    drug_info.report_code, 
                    drug_info.active_ingredient,
                    prescription_data
                )
                
                # Doz karşılaştırması yap
                drug_info.dose_compliant, drug_info.dose_check_details = self._compare_doses(
                    drug_info.prescription_dose,
                    drug_info.report_dose,
                    drug_name
                )
                
            else:
                drug_info.dose_check_details = "Raporlu ilaç değil - doz kontrolü gerekli değil"
            
            # 4. İlaç mesajlarını extract et
            drug_messages = self._extract_drug_messages(drug_dict, prescription_data)
            if drug_messages:
                logger.debug(f"📨 Messages found for {drug_name}: {drug_messages}")
            
            # 5. Warning kodlarını validate et
            warning_codes = self._validate_warning_codes(drug_dict, prescription_data)
            if warning_codes:
                logger.debug(f"⚠️ Warnings for {drug_name}: {warning_codes}")
                
            return drug_info
            
        except Exception as e:
            logger.error(f"❌ Single drug analysis error: {e}")
            return DrugInfo(drug_name=drug_dict.get('ilac_adi', 'UNKNOWN'))
    
    def _analyze_single_drug_fast(self, drug_dict: Dict, prescription_data: Dict) -> DrugInfo:
        """Hızlı ilaç analizi - sadece cache kullan, Medula'ya gitme"""
        try:
            drug_name = drug_dict.get('ilac_adi', '').strip()
            logger.debug(f"⚡ Fast analyzing drug: {drug_name}")
            
            # Temel bilgileri al
            drug_info = DrugInfo(
                drug_name=drug_name,
                prescription_dose=drug_dict.get('adet', '1')
            )
            
            # 1. Rapor kodu kontrolü
            drug_info.report_code = self._extract_report_code(drug_dict)
            
            # 2. MSJ durumu kontrolü  
            drug_info.msj_status = self._extract_msj_status(drug_dict)
            
            # 3. Sadece cache'den etken madde ve doz kontrolü
            if drug_info.report_code:
                # Cache'den etken madde al (Medula'ya gitme)
                drug_info.active_ingredient = self._get_cached_active_ingredient(drug_name) or "Bilinmiyor"
                
                if drug_info.active_ingredient != "Bilinmiyor":
                    # Cache'den rapor dozu al
                    drug_info.report_dose = self._get_cached_report_dose(
                        drug_info.report_code, 
                        drug_info.active_ingredient
                    ) or "Bilinmiyor"
                    
                    if drug_info.report_dose != "Bilinmiyor":
                        # Doz karşılaştırması yap
                        drug_info.dose_compliant, drug_info.dose_check_details = self._compare_doses(
                            drug_info.prescription_dose,
                            drug_info.report_dose,
                            drug_name
                        )
                    else:
                        drug_info.dose_check_details = "⚡ Fast mode: Rapor dozu cache'de bulunamadı"
                else:
                    drug_info.dose_check_details = "⚡ Fast mode: Etken madde cache'de bulunamadı"
            else:
                drug_info.dose_check_details = "Raporlu ilaç değil"
                
            return drug_info
            
        except Exception as e:
            logger.error(f"❌ Fast drug analysis error: {e}")
            return DrugInfo(drug_name=drug_dict.get('ilac_adi', 'UNKNOWN'))
    
    # =========================================================================
    # REPORT CODE AND MSJ DETECTION
    # =========================================================================
    
    def _extract_report_code(self, drug_dict: Dict) -> str:
        """İlaçtan rapor kodunu çıkar"""
        try:
            # Farklı alanlardan rapor kodunu bul
            possible_fields = ['rapor_kodu', 'report_code', 'rapor', 'kod']
            
            for field in possible_fields:
                if field in drug_dict and drug_dict[field]:
                    code = str(drug_dict[field]).strip()
                    if code and code.lower() != 'none':
                        logger.debug(f"✅ Report code found in {field}: {code}")
                        return code
            
            # Drug name'den rapor kodu pattern'ı ara
            drug_name = drug_dict.get('ilac_adi', '')
            report_patterns = [
                r'\\b(R\\d{6,})\\b',     # R123456 formatı
                r'\\b(\\d{6,})\\b',      # 6+ digit numbers
                r'\\(([A-Z]\\d+)\\)',    # (R123) formatı
            ]
            
            for pattern in report_patterns:
                match = re.search(pattern, drug_name)
                if match:
                    code = match.group(1)
                    logger.debug(f"✅ Report code found in drug name: {code}")
                    return code
            
            logger.debug(f"⚠️ No report code found for drug: {drug_name}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Report code extraction error: {e}")
            return ""
    
    def _extract_msj_status(self, drug_dict: Dict) -> str:
        """MSJ durumunu çıkar"""
        try:
            # MSJ alanlarını kontrol et
            msj_fields = ['msj', 'message', 'mesaj', 'msg']
            
            for field in msj_fields:
                if field in drug_dict:
                    msj_value = str(drug_dict[field]).strip().lower()
                    if msj_value in ['var', 'yes', 'true', '1']:
                        return 'var'
                    elif msj_value in ['yok', 'no', 'false', '0']:
                        return 'yok'
            
            # Default olarak 'yok'
            return 'yok'
            
        except Exception as e:
            logger.error(f"❌ MSJ status extraction error: {e}")
            return 'yok'
    
    # =========================================================================
    # ACTIVE INGREDIENT EXTRACTION
    # =========================================================================
    
    def _get_active_ingredient(self, drug_name: str) -> str:
        """Etken madde al (cache'den veya Medula'dan)"""
        try:
            # Cache'de var mı kontrol et
            if drug_name in self.active_ingredient_cache:
                logger.debug(f"📦 Active ingredient from cache: {drug_name}")
                return self.active_ingredient_cache[drug_name]
            
            # Database'den kontrol et
            cached_ingredient = self._get_cached_active_ingredient(drug_name)
            if cached_ingredient:
                self.active_ingredient_cache[drug_name] = cached_ingredient
                return cached_ingredient
            
            # Medula'dan çek
            if self.browser:
                ingredient = self._extract_active_ingredient_from_medula(drug_name)
                if ingredient:
                    # Cache'e ve database'e kaydet
                    self.active_ingredient_cache[drug_name] = ingredient
                    self._save_active_ingredient_to_cache(drug_name, ingredient)
                    return ingredient
            
            logger.warning(f"⚠️ Could not find active ingredient for: {drug_name}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Active ingredient extraction error: {e}")
            return ""
    
    def _get_cached_active_ingredient(self, drug_name: str) -> Optional[str]:
        """Database'den cached etken madde al"""
        try:
            # SQLite'dan etken madde sorgula
            query = """
            SELECT active_ingredient FROM drug_cache 
            WHERE drug_name = ? AND active_ingredient IS NOT NULL
            """
            
            result = self.database.execute_query(query, (drug_name,))
            if result and len(result) > 0:
                ingredient = result[0][0]
                logger.debug(f"📦 Active ingredient from database: {drug_name} -> {ingredient}")
                return ingredient
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Cached active ingredient query error: {e}")
            return None
    
    def _extract_active_ingredient_from_medula(self, drug_name: str) -> str:
        """Medula İlaç Bilgileri'nden etken madde çıkar"""
        try:
            if not self.browser:
                return ""
            
            logger.info(f"🔍 Extracting active ingredient from Medula for: {drug_name}")
            
            # İlaç Bilgileri butonunu bul ve tıkla
            drug_info_selectors = [
                "//input[@value='İlaç Bilgileri']",
                "//button[contains(text(), 'İlaç Bilgileri')]",
                "//a[contains(text(), 'İlaç Bilgileri')]"
            ]
            
            button_clicked = False
            for selector in drug_info_selectors:
                try:
                    button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    button.click()
                    logger.debug("✅ İlaç Bilgileri button clicked")
                    button_clicked = True
                    break
                except:
                    continue
            
            if not button_clicked:
                logger.warning("⚠️ İlaç Bilgileri button not found")
                return ""
            
            # Sayfanın yüklenmesini bekle
            time.sleep(3)
            
            # Etken madde bilgisini ara
            ingredient_selectors = [
                "//td[contains(text(), 'Etken Madde')]/following-sibling::td",
                "//span[contains(text(), 'Etken Madde')]/following::span[1]",
                "//label[contains(text(), 'Etken Madde')]/following::span[1]",
                "//*[contains(text(), 'ETKEN MADDE')]/following-sibling::*"
            ]
            
            for selector in ingredient_selectors:
                try:
                    element = self.browser.driver.find_element(By.XPATH, selector)
                    ingredient = element.text.strip()
                    
                    if ingredient and len(ingredient) > 2:
                        logger.info(f"✅ Active ingredient found: {drug_name} -> {ingredient}")
                        return ingredient
                        
                except:
                    continue
            
            # Pattern-based extraction (son çare)
            page_source = self.browser.driver.page_source
            ingredient_patterns = [
                r'Etken\\s*Madde[:\\s]*([A-ZÇĞİÖŞÜ\\s]{3,})',
                r'ETKİN\\s*MADDE[:\\s]*([A-ZÇĞİÖŞÜ\\s]{3,})',
                r'Active\\s*Ingredient[:\\s]*([A-Za-z\\s]{3,})'
            ]
            
            for pattern in ingredient_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    ingredient = match.group(1).strip()
                    logger.info(f"✅ Active ingredient found via pattern: {drug_name} -> {ingredient}")
                    return ingredient
            
            logger.warning(f"⚠️ Active ingredient not found for: {drug_name}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Medula active ingredient extraction error: {e}")
            return ""
        finally:
            # Geri git
            try:
                self.browser.driver.back()
                time.sleep(2)
            except:
                pass
    
    def _save_active_ingredient_to_cache(self, drug_name: str, active_ingredient: str):
        """Etken maddeyi database cache'ine kaydet"""
        try:
            query = """
            INSERT OR REPLACE INTO drug_cache (drug_name, active_ingredient, cache_date)
            VALUES (?, ?, ?)
            """
            
            self.database.execute_query(query, (drug_name, active_ingredient, datetime.now().isoformat()))
            logger.debug(f"💾 Active ingredient cached: {drug_name} -> {active_ingredient}")
            
        except Exception as e:
            logger.error(f"❌ Active ingredient cache save error: {e}")
    
    # =========================================================================
    # REPORT DOSE EXTRACTION
    # =========================================================================
    
    def _get_report_dose(self, report_code: str, active_ingredient: str, prescription_data: Dict) -> str:
        """Rapor dozunu al"""
        try:
            cache_key = f"{report_code}_{active_ingredient}"
            
            # Cache'de var mı
            if cache_key in self.report_dose_cache:
                return self.report_dose_cache[cache_key]
            
            # Database'den kontrol et
            cached_dose = self._get_cached_report_dose(report_code, active_ingredient)
            if cached_dose:
                self.report_dose_cache[cache_key] = cached_dose
                return cached_dose
            
            # Medula'dan çek
            if self.browser:
                dose = self._extract_report_dose_from_medula(report_code, active_ingredient)
                if dose:
                    self.report_dose_cache[cache_key] = dose
                    self._save_report_dose_to_cache(report_code, active_ingredient, dose)
                    return dose
            
            logger.warning(f"⚠️ Could not find report dose for: {report_code} - {active_ingredient}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Report dose extraction error: {e}")
            return ""
    
    def _get_cached_report_dose(self, report_code: str, active_ingredient: str) -> Optional[str]:
        """Database'den cached rapor dozu al"""
        try:
            query = """
            SELECT report_dose FROM report_dose_cache 
            WHERE report_code = ? AND active_ingredient = ? AND report_dose IS NOT NULL
            """
            
            result = self.database.execute_query(query, (report_code, active_ingredient))
            if result and len(result) > 0:
                return result[0][0]
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Cached report dose query error: {e}")
            return None
    
    def _extract_report_dose_from_medula(self, report_code: str, active_ingredient: str) -> str:
        """Medula rapor sayfasından doz çıkar"""
        try:
            logger.info(f"🔍 Extracting report dose: {report_code} - {active_ingredient}")
            
            # Rapor butonunu bul ve tıkla
            report_selectors = [
                "//input[@value='Rapor']",
                "//button[contains(text(), 'Rapor')]",
                "//a[contains(text(), 'Rapor')]"
            ]
            
            button_clicked = False
            for selector in report_selectors:
                try:
                    button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    button.click()
                    logger.debug("✅ Rapor button clicked")
                    button_clicked = True
                    break
                except:
                    continue
            
            if not button_clicked:
                logger.warning("⚠️ Rapor button not found")
                return ""
            
            # Rapor sayfasının yüklenmesini bekle
            time.sleep(3)
            
            # Etken madde ve dozunu ara
            dose_selectors = [
                f"//td[contains(text(), '{active_ingredient}')]/following-sibling::td",
                f"//span[contains(text(), '{active_ingredient}')]/following::*[contains(text(), 'mg') or contains(text(), 'ml') or contains(text(), 'adet')]",
                "//td[contains(text(), 'Doz')]/following-sibling::td",
                "//td[contains(text(), 'Miktar')]/following-sibling::td"
            ]
            
            for selector in dose_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        dose_text = element.text.strip()
                        
                        # Doz pattern'ı kontrol et
                        dose_patterns = [
                            r'(\d+(?:\.\d+)?)\s*(?:mg|ML|MG|ml)',
                            r'(\d+(?:\.\d+)?)\s*(?:adet|ADET|tablet|TABLET)',
                            r'(\d+(?:\.\d+)?)'
                        ]
                        
                        for pattern in dose_patterns:
                            match = re.search(pattern, dose_text)
                            if match:
                                dose = match.group(1)
                                logger.info(f"✅ Report dose found: {report_code} - {active_ingredient} -> {dose}")
                                return dose
                                
                except:
                    continue
            
            # Page source'dan pattern araması (son çare)
            page_source = self.browser.driver.page_source
            dose_patterns = [
                f'{re.escape(active_ingredient)}[\\s\\S]*?(\\d+(?:\\.\\d+)?)\\s*(?:mg|ml|adet)',
                r'Günlük\\s*Doz[:\\s]*(\\d+(?:\\.\\d+)?)\\s*(?:mg|ml)',
                r'Maksimum\\s*Doz[:\\s]*(\\d+(?:\\.\\d+)?)\\s*(?:mg|ml)'
            ]
            
            for pattern in dose_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    dose = matches[0]
                    logger.info(f"✅ Report dose found via pattern: {report_code} - {active_ingredient} -> {dose}")
                    return dose
            
            logger.warning(f"⚠️ Report dose not found: {report_code} - {active_ingredient}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Medula report dose extraction error: {e}")
            return ""
        finally:
            # Geri git
            try:
                self.browser.driver.back()
                time.sleep(2)
            except:
                pass
    
    def _save_report_dose_to_cache(self, report_code: str, active_ingredient: str, dose: str):
        """Rapor dozunu cache'e kaydet"""
        try:
            query = """
            INSERT OR REPLACE INTO report_dose_cache 
            (report_code, active_ingredient, report_dose, cache_date)
            VALUES (?, ?, ?, ?)
            """
            
            self.database.execute_query(query, 
                (report_code, active_ingredient, dose, datetime.now().isoformat()))
            logger.debug(f"💾 Report dose cached: {report_code} - {active_ingredient} -> {dose}")
            
        except Exception as e:
            logger.error(f"❌ Report dose cache save error: {e}")
    
    # =========================================================================
    # DOSE COMPARISON
    # =========================================================================
    
    def _compare_doses(self, prescription_dose: str, report_dose: str, drug_name: str) -> Tuple[Optional[bool], str]:
        """Dozları karşılaştır"""
        try:
            logger.debug(f"⚖️ Comparing doses for {drug_name}: prescription={prescription_dose}, report={report_dose}")
            
            # Boş değerler kontrolü
            if not report_dose or report_dose.strip() == "":
                return None, "Rapor dozu bulunamadı"
            
            if not prescription_dose or prescription_dose.strip() == "":
                return None, "Reçete dozu bulunamadı"
            
            # Numeric değerleri çıkar
            prescription_numeric = self._extract_numeric_dose(prescription_dose)
            report_numeric = self._extract_numeric_dose(report_dose)
            
            if prescription_numeric is None:
                return None, f"Reçete dozu parse edilemedi: {prescription_dose}"
            
            if report_numeric is None:
                return None, f"Rapor dozu parse edilemedi: {report_dose}"
            
            # Karşılaştırma
            if prescription_numeric <= report_numeric:
                return True, f"UYGUN: Reçete dozu ({prescription_numeric}) ≤ Rapor dozu ({report_numeric})"
            else:
                return False, f"İHLAL: Reçete dozu ({prescription_numeric}) > Rapor dozu ({report_numeric})"
            
        except Exception as e:
            logger.error(f"❌ Dose comparison error: {e}")
            return None, f"Doz karşılaştırma hatası: {str(e)}"
    
    def _extract_numeric_dose(self, dose_str: str) -> Optional[float]:
        """String'den numeric doz değerini çıkar"""
        try:
            if not dose_str:
                return None
            
            # Sayısal değeri çıkar
            numeric_patterns = [
                r'(\d+(?:\.\d+)?)',  # Decimal number
                r'(\d+)',            # Integer
            ]
            
            for pattern in numeric_patterns:
                match = re.search(pattern, str(dose_str).replace(',', '.'))
                if match:
                    return float(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Numeric dose extraction error: {e}")
            return None
    
    # =========================================================================
    # DRUG MESSAGE EXTRACTION
    # =========================================================================
    
    def _extract_drug_messages(self, drug_dict: Dict, prescription_data: Dict) -> List[str]:
        """Extract drug message codes (1013, 1301, 1038, 1002, etc.)"""
        try:
            messages = []
            
            # Check standard message fields
            message_fields = ['mesaj_kodlari', 'message_codes', 'mesajlar', 'messages', 'ilac_mesajlari']
            
            for field in message_fields:
                if field in drug_dict and drug_dict[field]:
                    field_messages = self._parse_message_codes(drug_dict[field])
                    messages.extend(field_messages)
            
            # Check if there are message details in prescription data
            if 'drug_messages' in prescription_data:
                for message in prescription_data['drug_messages']:
                    if isinstance(message, dict) and 'kod' in message:
                        messages.append(message['kod'])
                    elif isinstance(message, str):
                        parsed = self._parse_message_codes(message)
                        messages.extend(parsed)
            
            # Remove duplicates and filter known codes
            unique_messages = list(set(messages))
            filtered_messages = [msg for msg in unique_messages if self._is_valid_message_code(msg)]
            
            logger.debug(f"📨 Messages found: {filtered_messages}")
            return filtered_messages
            
        except Exception as e:
            logger.error(f"❌ Message extraction error: {e}")
            return []
    
    def _parse_message_codes(self, message_data) -> List[str]:
        """Parse message codes from various formats"""
        try:
            messages = []
            
            if isinstance(message_data, str):
                # Extract codes like "1013(1)", "1301", "1038", "1002"
                import re
                pattern = r'\b(\d{4})\b'
                matches = re.findall(pattern, message_data)
                messages.extend(matches)
                
            elif isinstance(message_data, list):
                for item in message_data:
                    if isinstance(item, str):
                        messages.extend(self._parse_message_codes(item))
                    elif isinstance(item, dict) and 'kod' in item:
                        messages.append(str(item['kod']))
                        
            elif isinstance(message_data, dict):
                for key, value in message_data.items():
                    if 'kod' in key.lower() or 'message' in key.lower():
                        messages.extend(self._parse_message_codes(value))
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Message parsing error: {e}")
            return []
    
    def _is_valid_message_code(self, code: str) -> bool:
        """Check if message code is valid (4 digits)"""
        try:
            # Known message codes
            known_codes = ['1013', '1301', '1038', '1002', '1020', '1021', '1022', '1023']
            
            if code in known_codes:
                return True
            
            # Generic 4-digit code validation
            if len(code) == 4 and code.isdigit():
                return True
                
            return False
            
        except:
            return False
    
    def _get_cached_drug_messages(self, drug_name: str) -> Optional[List[str]]:
        """Get cached drug messages"""
        try:
            query = "SELECT message_codes FROM drug_message_cache WHERE drug_name = ?"
            result = self.database.execute_query(query, (drug_name,))
            
            if result:
                message_str = result[0][0]
                return message_str.split(',') if message_str else []
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Cached message retrieval error: {e}")
            return None
    
    def _save_drug_messages_to_cache(self, drug_name: str, messages: List[str]):
        """Save drug messages to cache"""
        try:
            message_str = ','.join(messages) if messages else ''
            
            query = """
            INSERT OR REPLACE INTO drug_message_cache 
            (drug_name, message_codes, created_at) 
            VALUES (?, ?, datetime('now'))
            """
            
            self.database.execute_query(query, (drug_name, message_str))
            logger.debug(f"💾 Drug messages cached: {drug_name} -> {messages}")
            
        except Exception as e:
            logger.error(f"❌ Message cache save error: {e}")
    
    # =========================================================================
    # WARNING CODE VALIDATION  
    # =========================================================================
    
    def _validate_warning_codes(self, drug_dict: Dict, prescription_data: Dict) -> List[str]:
        """Validate warning codes between prescription and report data"""
        try:
            warnings = []
            
            # Get drug messages
            drug_messages = self._extract_drug_messages(drug_dict, prescription_data)
            
            # Check critical message codes
            critical_codes = {
                '1013': 'Doz aşımı uyarısı',
                '1301': 'Endikasyon uyarısı', 
                '1038': 'Yaş kısıtlama uyarısı',
                '1002': 'Etkileşim uyarısı'
            }
            
            for code in drug_messages:
                if code in critical_codes:
                    warnings.append(f"⚠️ {critical_codes[code]} ({code})")
            
            # Additional validation based on prescription data
            if self._check_age_restrictions(drug_dict, prescription_data):
                warnings.append("⚠️ Yaş kısıtlaması kontrolü gerekli")
            
            if self._check_interaction_warnings(drug_dict, prescription_data):
                warnings.append("⚠️ İlaç etkileşimi kontrolü gerekli")
                
            return warnings
            
        except Exception as e:
            logger.error(f"❌ Warning validation error: {e}")
            return []
    
    def _check_age_restrictions(self, drug_dict: Dict, prescription_data: Dict) -> bool:
        """Check age-related restrictions"""
        try:
            # This would check patient age against drug restrictions
            # Implementation depends on available patient data
            return False
            
        except Exception as e:
            logger.error(f"❌ Age restriction check error: {e}")
            return False
    
    def _check_interaction_warnings(self, drug_dict: Dict, prescription_data: Dict) -> bool:
        """Check drug interaction warnings"""
        try:
            # This would check for drug interactions
            # Implementation depends on drug database
            return False
            
        except Exception as e:
            logger.error(f"❌ Interaction check error: {e}")
            return False
    
    # =========================================================================
    # DATABASE CACHE SETUP
    # =========================================================================
    
    def setup_cache_tables(self):
        """Cache tablolarını oluştur"""
        try:
            # Drug cache table
            drug_cache_query = """
            CREATE TABLE IF NOT EXISTS drug_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_name TEXT UNIQUE NOT NULL,
                active_ingredient TEXT,
                cache_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Report dose cache table
            report_dose_query = """
            CREATE TABLE IF NOT EXISTS report_dose_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_code TEXT NOT NULL,
                active_ingredient TEXT NOT NULL,
                report_dose TEXT,
                cache_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(report_code, active_ingredient)
            )
            """
            
            # Drug message cache table
            message_cache_query = """
            CREATE TABLE IF NOT EXISTS drug_message_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_name TEXT UNIQUE NOT NULL,
                message_codes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            self.database.execute_query(drug_cache_query)
            self.database.execute_query(report_dose_query)
            self.database.execute_query(message_cache_query)
            
            logger.info("✅ Cache tables created successfully (drugs, report_doses, messages)")
            
        except Exception as e:
            logger.error(f"❌ Cache table setup error: {e}")

# =========================================================================
# TEST FUNCTIONS
# =========================================================================

def test_dose_controller():
    """Doz kontrolcusu testi"""
    print("=== TESTING PRESCRIPTION DOSE CONTROLLER ===")
    
    controller = PrescriptionDoseController()
    controller.setup_cache_tables()
    
    # Test prescription data
    test_prescription = {
        "recete_no": "TEST_DOSE_001",
        "hasta_ad_soyad": "Test Hasta",
        "drugs": [
            {
                "ilac_adi": "PANTO 40 MG 28 TABLET",
                "adet": "2",
                "rapor_kodu": "R123456",
                "msj": "var"
            },
            {
                "ilac_adi": "ASPIRIN 100 MG",
                "adet": "1",
                "rapor_kodu": "",  # Raporlu degil
                "msj": "yok"
            }
        ]
    }
    
    # Test dose control
    result = controller.control_prescription_doses(test_prescription)
    
    print("[OK] Dose control test completed:")
    print(f"  Prescription ID: {result.prescription_id}")
    print(f"  Total drugs: {result.total_drugs}")
    print(f"  Reported drugs: {result.reported_drugs}")
    print(f"  Dose violations: {result.dose_violations}")
    print(f"  Control notes: {len(result.control_notes)}")
    
    for note in result.control_notes:
        print(f"    - {note}")
    
    return True

if __name__ == "__main__":
    test_dose_controller()