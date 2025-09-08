"""
Gelişmiş Reçete Detay Çıkarma Sistemi
Tüm screenshot analizine göre otomatik veri çıkarma
"""

from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json
from datetime import datetime
import sys
import os

# Windows konsol için UTF-8 encoding ayarla
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')

class AdvancedPrescriptionExtractor:
    def __init__(self):
        self.browser = MedulaBrowser(Settings())
        self.wait = None
        self.prescriptions_with_full_details = []
    
    def start(self):
        """Browser'ı başlat ve giriş yap"""
        print('[BAŞLAT] Gelişmiş reçete çıkarma sistemi başlatılıyor...')
        success = self.browser.start()
        
        if success:
            self.wait = WebDriverWait(self.browser.driver, 30)
            if self.browser.login():
                print('[BAŞARILI] Medula girişi başarılı!')
                return True
            else:
                print('[HATA] Medula girişi başarısız!')
                return False
        return False
    
    def navigate_to_prescriptions_auto(self):
        """Otomatik reçete listesine gitme"""
        try:
            print('[NAVİGASYON] Reçete Listesi sayfasına gidiliyor...')
            
            # Farklı selector'ları dene
            selectors = [
                "//*[text()='Reçete Listesi']",
                "//*[contains(text(), 'Reçete Listesi')]",
                "//a[contains(text(), 'Reçete')]",
                "//li[contains(text(), 'Reçete Listesi')]"
            ]
            
            for selector in selectors:
                try:
                    recete_link = self.browser.driver.find_element(By.XPATH, selector)
                    self.browser.driver.execute_script("arguments[0].click();", recete_link)
                    time.sleep(5)
                    print('[BAŞARILI] Reçete Listesi sayfası açıldı')
                    return True
                except:
                    continue
            
            print('[MANUEL GEREKLİ] Reçete Listesi linkine manuel tıklayın')
            input('Devam etmek için ENTER basın...')
            return True
            
        except Exception as e:
            print(f'[HATA] Navigation hatası: {e}')
            return False
    
    def set_filters_auto(self, group='A'):
        """Otomatik filtre ayarlama"""
        try:
            print(f'[FİLTRE] {group} Grubu filtresi ayarlanıyor...')
            
            # Fatura türü dropdown'ını bul
            dropdown_selectors = ["select[name*='fatur']", "select", "[name='faturaTuru']"]
            
            for selector in dropdown_selectors:
                try:
                    dropdown_element = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    dropdown = Select(dropdown_element)
                    
                    # A Grubu seçeneklerini dene
                    group_options = [f"{group} Grubu", f"{group} GRUBU"]
                    
                    for option in group_options:
                        try:
                            dropdown.select_by_visible_text(option)
                            print(f'[BAŞARILI] {option} seçildi')
                            break
                        except:
                            continue
                    break
                except:
                    continue
            
            # Sorgula butonuna bas
            sorgula_selectors = [
                "//input[@value='Sorgula']",
                "//button[contains(text(), 'Sorgula')]",
                "//input[@type='submit']"
            ]
            
            for selector in sorgula_selectors:
                try:
                    sorgula_button = self.browser.driver.find_element(By.XPATH, selector)
                    sorgula_button.click()
                    time.sleep(5)
                    print(f'[SORGU] {group} Grubu reçeteler sorgulandı')
                    return True
                except:
                    continue
            
            print('[MANUEL] Filtreyi manuel ayarlayın')
            input('A Grubu seçip sorgula butonuna bastıktan sonra ENTER basın...')
            return True
            
        except Exception as e:
            print(f'[HATA] Filtre hatası: {e}')
            return False
    
    def extract_prescription_list_auto(self):
        """Otomatik reçete listesi çıkarma"""
        try:
            print('[ÇIKARMA] Reçete listesi otomatik çıkarılıyor...')
            
            # Reçete tablosunu bul
            table_selectors = [
                "//table[.//th[contains(text(), 'Reçete No')]]",
                "//table[.//td[contains(text(), '3G')]]",  # Reçete numarası pattern'i
                "table"
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    table = self.browser.driver.find_element(By.XPATH, selector if selector != "table" else "//table")
                    break
                except:
                    continue
            
            if not table:
                print('[HATA] Reçete tablosu bulunamadı')
                return []
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            prescriptions = []
            
            for row_index, row in enumerate(rows[1:], 1):  # Başlık satırını atla
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 7:
                        prescription_data = {
                            'list_index': row_index,
                            'recete_no': cells[0].text.strip(),
                            'son_guncelleme': cells[1].text.strip(),
                            'recete_tarihi': cells[2].text.strip(),
                            'hasta_ad': cells[3].text.strip(),
                            'hasta_soyad': cells[4].text.strip(),
                            'kapsam': cells[5].text.strip(),
                            'sonlandirildi': cells[6].text.strip(),
                            'row_element': row
                        }
                        prescriptions.append(prescription_data)
                        
                        if row_index <= 3:
                            print(f'[LİSTE] {row_index}. {prescription_data["recete_no"]} - {prescription_data["hasta_ad"]} {prescription_data["hasta_soyad"]}')
                            
                except Exception as e:
                    print(f'[UYARI] Satır {row_index} işlenirken hata: {e}')
                    
            print(f'[BAŞARILI] {len(prescriptions)} reçete listesi çıkarıldı')
            return prescriptions
            
        except Exception as e:
            print(f'[HATA] Liste çıkarma hatası: {e}')
            return []
    
    def click_prescription_detail(self, prescription):
        """Reçete detayına git"""
        try:
            print(f'[DETAY] {prescription["recete_no"]} detayına giriliyor...')
            
            # Hasta adına tıkla
            prescription['row_element'].click()
            time.sleep(3)
            
            # Detay sayfasının yüklendiğini kontrol et
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'T.C. Kimlik')]")))
            
            print('[BAŞARILI] Reçete detay sayfası açıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Detay açma hatası: {e}')
            return False
    
    def extract_patient_info_auto(self):
        """Hasta bilgilerini otomatik çıkar"""
        try:
            print('[ÇIKARMA] Hasta bilgileri çıkarılıyor...')
            
            patient_info = {}
            
            # Hasta bilgileri alanlarını çıkar
            field_mappings = {
                'hasta_tc': ["T.C. Kimlik No", "T.C. Kimlik Numarası"],
                'hasta_ad_soyad': ["Adı / Soyadı", "Ad / Soyad"],
                'cinsiyet': ["Cinsiyeti", "Cinsiyet"],
                'dogum_tarihi': ["Doğum Tarihi"],
                'teslim_alan_tc': ["Teslim Alan T.C."],
                'provizyon_tipi': ["Provizyon Tipi"],
                'protokol_no': ["Protokol No"],
                'tesis_kodu': ["Tesis Kodu"],
                'e_recete_no': ["e-Reçete No"],
                'hasta_turu': ["Hasta Türü"],
                'recete_tarihi': ["Reçete Tarihi"],
                'recete_turu': ["Reçete Türü"],
                'dip_tesc_no': ["Dip.Tesc.No"],
                'hekim': ["Hekim"],
                'dr_dip_no': ["Dr.Dip.No", "Dr. Ad/Soyad"],
                'brans': ["Branş"]
            }
            
            for key, field_names in field_mappings.items():
                for field_name in field_names:
                    try:
                        xpath = f"//td[contains(text(), '{field_name}')]/following-sibling::td"
                        element = self.browser.driver.find_element(By.XPATH, xpath)
                        patient_info[key] = element.text.strip()
                        break
                    except:
                        continue
                
                if key not in patient_info:
                    patient_info[key] = ""
            
            print(f'[BAŞARILI] Hasta bilgileri çıkarıldı: {patient_info.get("hasta_ad_soyad", "N/A")}')
            return patient_info
            
        except Exception as e:
            print(f'[HATA] Hasta bilgisi çıkarma hatası: {e}')
            return {}
    
    def extract_drug_table_auto(self):
        """İlaç tablosunu otomatik çıkar"""
        try:
            print('[ÇIKARMA] İlaç tablosu çıkarılıyor...')
            
            # İlaç tablosunu bul
            drug_table_selectors = [
                "//table[.//th[contains(text(), 'Barkod')]]",
                "//table[.//td[contains(text(), '869951')]]",  # Barkod pattern'i
                "//div[contains(@class, 'ilac')]//table"
            ]
            
            drug_table = None
            for selector in drug_table_selectors:
                try:
                    drug_table = self.browser.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if not drug_table:
                print('[UYARI] İlaç tablosu bulunamadı')
                return []
            
            rows = drug_table.find_elements(By.TAG_NAME, "tr")
            drugs = []
            
            for row_index, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 8:
                        
                        # Checkbox kontrolü
                        checkbox = None
                        try:
                            checkbox = cells[0].find_element(By.TAG_NAME, "input")
                            is_selected = checkbox.is_selected()
                        except:
                            is_selected = False
                        
                        drug_data = {
                            'secili': is_selected,
                            'barkod': cells[1].text.strip() if len(cells) > 1 else '',
                            'ilac_adi': cells[2].text.strip() if len(cells) > 2 else '',
                            'adet_penyol_doz': cells[3].text.strip() if len(cells) > 3 else '',
                            'tutar': cells[4].text.strip() if len(cells) > 4 else '',
                            'fark': cells[5].text.strip() if len(cells) > 5 else '',
                            'rapor': cells[6].text.strip() if len(cells) > 6 else '',
                            'verilebilecegi': cells[7].text.strip() if len(cells) > 7 else '',
                            'mesaj': cells[8].text.strip() if len(cells) > 8 else ''
                        }
                        
                        drugs.append(drug_data)
                        
                        if row_index <= 3:
                            print(f'[İLAÇ] {row_index}. {drug_data["ilac_adi"]} - {drug_data["barkod"]}')
                            
                except Exception as e:
                    print(f'[UYARI] İlaç satırı {row_index} işlenirken hata: {e}')
            
            print(f'[BAŞARILI] {len(drugs)} ilaç çıkarıldı')
            return drugs
            
        except Exception as e:
            print(f'[HATA] İlaç tablosu çıkarma hatası: {e}')
            return []
    
    def navigate_to_drug_details(self):
        """İlaç bilgileri sayfasına git"""
        try:
            print('[NAVİGASYON] İlaç Bilgileri sayfasına gidiliyor...')
            
            # İlaç Bilgi butonunu bul
            button_selectors = [
                "//input[@value='İlaç Bilgi']",
                "//button[contains(text(), 'İlaç Bilgi')]",
                "//a[contains(text(), 'İlaç Bilgi')]"
            ]
            
            for selector in button_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(3)
                    print('[BAŞARILI] İlaç Bilgileri sayfası açıldı')
                    return True
                except:
                    continue
                    
            print('[UYARI] İlaç Bilgi butonu bulunamadı')
            return False
            
        except Exception as e:
            print(f'[HATA] İlaç bilgisi navigation hatası: {e}')
            return False
    
    def extract_drug_details_auto(self):
        """İlaç detay bilgilerini otomatik çıkar"""
        try:
            print('[ÇIKARMA] İlaç detay bilgileri çıkarılıyor...')
            
            drug_details = {}
            
            # İlaç detay alanları
            detail_fields = {
                'ilac_adi': ['İlaç Adı'],
                'ambalaj_miktari': ['Ambalaj Miktarı'],  
                'farmasotik_formu': ['Farmasötik Formu'],
                'tek_doz_miktari': ['Tek Doz Miktarı'],
                'kullanim_suresi': ['Kullanım Süresi'],
                'yas_araligi': ['Yaş Aralığı'],
                'cinsiyet_kisiti': ['Cinsiyet'],
                'perakende_odenen_fiyat': ['Perakende/Ödenen Fiyat'],
                'kamu_indirim_orani': ['Kamu İndirim Oranı'],
                'recete_turu': ['Reçete Türü'],
                'kamukod_no': ['Kamukod No'],
                'ay_araligi': ['Ay Aralığı'],
                'tedavi_semasi_gerekli': ['Tedavi Seması Gerekli'],
                'yatan_recetesi': ['Yatan Reçetesi'],
                'ayaktan_recetesi': ['Ayaktan Reçetesi'],
                'ayaktan_maks_kul_doz': ['Ayaktan Maks. Kul. Doz'],
                'yatan_maks_kul_doz': ['Yatan Maks. Kul. Doz'],
                'raporlu_maks_kul_doz': ['Raporlu Maks. Kul. Doz'],
                'takipli_ilac_sayisi': ['Takipli İlaç Sayısı'],
                'maksimum_ilac_adet': ['Maksimum İlaç Adet'],
                'gunluk_maks_kalori': ['Günlük Maks.Kalori Miktarı'],
                'kutu_birim_doz_miktari': ['Kutu Birim Doz Miktarı'],
                'birim_doz_miktari': ['Birim Doz Miktarı'],
                'etkin_madde': ['Etkin Madde']
            }
            
            for key, field_names in detail_fields.items():
                for field_name in field_names:
                    try:
                        xpath = f"//td[contains(text(), '{field_name}')]/following-sibling::td"
                        element = self.browser.driver.find_element(By.XPATH, xpath)
                        drug_details[key] = element.text.strip()
                        break
                    except:
                        continue
                
                if key not in drug_details:
                    drug_details[key] = ""
            
            # İlaç mesajları çıkar
            drug_details['ilac_mesajlari'] = self.extract_drug_messages_auto()
            
            print('[BAŞARILI] İlaç detay bilgileri çıkarıldı')
            return drug_details
            
        except Exception as e:
            print(f'[HATA] İlaç detayı çıkarma hatası: {e}')
            return {}
    
    def extract_drug_messages_auto(self):
        """İlaç mesajlarını otomatik çıkar"""
        try:
            messages = []
            
            # İlaç mesaj tablosunu bul
            message_selectors = [
                "//table[.//th[contains(text(), 'İlaç Mesajı')]]//td",
                "//div[contains(text(), '1013')]",  # Mesaj kodu pattern'i
                "//div[contains(text(), '1301')]"
            ]
            
            for selector in message_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and ('1013' in text or '1301' in text or '1038' in text or '1002' in text):
                            messages.append(text)
                except:
                    continue
            
            return messages
            
        except Exception as e:
            print(f'[HATA] İlaç mesajları çıkarma hatası: {e}')
            return []
    
    def navigate_to_report(self):
        """Rapor sayfasına git"""
        try:
            print('[NAVİGASYON] Rapor sayfasına gidiliyor...')
            
            # Geri Dön butonuna bas (ilaç bilgilerinden çık)
            geri_selectors = [
                "//input[@value='Geri Dön']",
                "//button[contains(text(), 'Geri')]",
                "//a[contains(text(), 'Geri')]"
            ]
            
            for selector in geri_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(2)
                    break
                except:
                    continue
            
            # Rapor butonunu bul
            rapor_selectors = [
                "//input[@value='Rapor']",
                "//button[contains(text(), 'Rapor')]",
                "//a[contains(text(), 'Rapor')]"
            ]
            
            for selector in rapor_selectors:
                try:
                    button = self.browser.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(3)
                    print('[BAŞARILI] Rapor sayfası açıldı')
                    return True
                except:
                    continue
                    
            print('[UYARI] Rapor butonu bulunamadı')
            return False
            
        except Exception as e:
            print(f'[HATA] Rapor navigation hatası: {e}')
            return False
    
    def extract_report_details_auto(self):
        """Rapor detaylarını otomatik çıkar"""
        try:
            print('[ÇIKARMA] Rapor detayları çıkarılıyor...')
            
            report_details = {}
            
            # Temel rapor bilgileri
            report_fields = {
                'rapor_numarasi': ['Rapor Numarası', 'Rapor No'],
                'rapor_tarihi': ['Rapor Tarihi'],
                'protokol_no': ['Protokol No'],
                'duzenleme_turu': ['Düzenleme Türü'],
                'aciklama': ['Açıklama'],
                'kayit_sekli': ['Kayıt Şekli'],
                'tesis_kodu': ['Tesis Kodu'],
                'rapor_takip_no': ['Rapor Takip No'],
                'tesis_unvani': ['Tesis Ünvanı'],
                'kullanici_adi': ['Kullanıcı Adı']
            }
            
            for key, field_names in report_fields.items():
                for field_name in field_names:
                    try:
                        xpath = f"//td[contains(text(), '{field_name}')]/following-sibling::td"
                        element = self.browser.driver.find_element(By.XPATH, xpath)
                        report_details[key] = element.text.strip()
                        break
                    except:
                        continue
                
                if key not in report_details:
                    report_details[key] = ""
            
            # Tanı bilgilerini çıkar (ICD kodları)
            report_details['tani_bilgileri'] = self.extract_diagnosis_info_auto()
            
            # Doktor bilgilerini çıkar
            report_details['doktor_bilgileri'] = self.extract_doctor_info_auto()
            
            # Rapor etkin madde bilgilerini çıkar
            report_details['etkin_madde_bilgileri'] = self.extract_report_drug_info_auto()
            
            print('[BAŞARILI] Rapor detayları çıkarıldı')
            return report_details
            
        except Exception as e:
            print(f'[HATA] Rapor detayı çıkarma hatası: {e}')
            return {}
    
    def extract_diagnosis_info_auto(self):
        """Tanı bilgilerini (ICD kodları) çıkar"""
        try:
            diagnosis_info = []
            
            # Tanı tablosunu bul
            diagnosis_selectors = [
                "//table[.//th[contains(text(), 'Tanı')]]//tr",
                "//td[contains(text(), '06.01')]",  # ICD kod pattern'i
                "//td[contains(text(), 'Hepatit')]"
            ]
            
            # Tanı tablosunu çıkar
            try:
                table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Tanı')]]")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[1:]:  # Başlık atla
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        diagnosis = {
                            'tani_kodu': cells[0].text.strip(),
                            'baslangic_tarihi': cells[1].text.strip(),
                            'bitis_tarihi': cells[2].text.strip()
                        }
                        diagnosis_info.append(diagnosis)
                        
            except:
                # Alternatif yöntemle ICD kodlarını bul
                icd_patterns = ["06.01", "B18.1", "KRONİK VİRAL HEPATİT"]
                for pattern in icd_patterns:
                    try:
                        elements = self.browser.driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
                        for element in elements:
                            diagnosis_info.append({
                                'tani_kodu': pattern,
                                'aciklama': element.text.strip()
                            })
                    except:
                        continue
            
            return diagnosis_info
            
        except Exception as e:
            print(f'[HATA] Tanı bilgisi çıkarma hatası: {e}')
            return []
    
    def extract_doctor_info_auto(self):
        """Doktor bilgilerini çıkar"""
        try:
            doctor_info = {}
            
            # Doktor tablosunu bul
            doctor_fields = {
                'dr_diploma_no': ['Dr. Diploma No'],
                'dip_tescil_no': ['Dip. Tescil No'],
                'brans': ['Branş'],
                'adi': ['Adı'],
                'soyadi': ['Soyadı']
            }
            
            for key, field_names in doctor_fields.items():
                for field_name in field_names:
                    try:
                        xpath = f"//td[contains(text(), '{field_name}')]/following-sibling::td"
                        element = self.browser.driver.find_element(By.XPATH, xpath)
                        doctor_info[key] = element.text.strip()
                        break
                    except:
                        continue
                
                if key not in doctor_info:
                    doctor_info[key] = ""
            
            return doctor_info
            
        except Exception as e:
            print(f'[HATA] Doktor bilgisi çıkarma hatası: {e}')
            return {}
    
    def extract_report_drug_info_auto(self):
        """Rapor etkin madde bilgilerini çıkar"""
        try:
            drug_info = []
            
            # Rapor etkin madde tablosunu bul
            try:
                table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Kodu')]]")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[1:]:  # Başlık atla
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 5:
                        drug = {
                            'kodu': cells[0].text.strip(),
                            'adi': cells[1].text.strip(), 
                            'form': cells[2].text.strip(),
                            'tedavi_semasi': cells[3].text.strip(),
                            'ekleme_zamani': cells[4].text.strip()
                        }
                        drug_info.append(drug)
                        
            except:
                # Alternatif yöntem
                try:
                    etkin_madde_element = self.browser.driver.find_element(By.XPATH, "//*[contains(text(), 'TENOFOVIR')]")
                    drug_info.append({
                        'adi': etkin_madde_element.text.strip()
                    })
                except:
                    pass
            
            return drug_info
            
        except Exception as e:
            print(f'[HATA] Rapor ilaç bilgisi çıkarma hatası: {e}')
            return []
    
    def go_back_to_prescription_list(self):
        """Reçete listesine geri dön"""
        try:
            print('[NAVİGASYON] Reçete listesine geri dönülüyor...')
            
            geri_selectors = [
                "//input[@value='Geri Dön']",
                "//button[contains(text(), 'Geri')]"
            ]
            
            # İki kez geri dön (rapor -> detay -> liste)
            for _ in range(2):
                for selector in geri_selectors:
                    try:
                        button = self.browser.driver.find_element(By.XPATH, selector)
                        button.click()
                        time.sleep(2)
                        break
                    except:
                        continue
            
            print('[BAŞARILI] Reçete listesine geri dönüldü')
            return True
            
        except Exception as e:
            print(f'[HATA] Geri dönüş hatası: {e}')
            return False
    
    def process_prescription_fully_auto(self, prescription, index, total):
        """Tek bir reçetin tüm detaylarını otomatik çıkar"""
        try:
            print(f'\\n[İŞLEM {index}/{total}] {prescription["recete_no"]} tam otomatik işleniyor...')
            
            # Reçete detayına git
            if not self.click_prescription_detail(prescription):
                return None
            
            # Temel hasta bilgilerini çıkar
            patient_info = self.extract_patient_info_auto()
            
            # İlaç tablosunu çıkar
            drugs = self.extract_drug_table_auto()
            
            # İlaç detay bilgilerine git
            drug_details = {}
            drug_messages = []
            if self.navigate_to_drug_details():
                drug_details = self.extract_drug_details_auto()
                drug_messages = drug_details.get('ilac_mesajlari', [])
            
            # Rapor bilgilerine git
            report_details = {}
            if self.navigate_to_report():
                report_details = self.extract_report_details_auto()
            
            # Tüm bilgileri birleştir
            complete_prescription = {
                **prescription,
                **patient_info,
                'drugs': drugs,
                'drug_details': drug_details,
                'drug_messages': drug_messages,
                'report_details': report_details,
                'extraction_time': datetime.now().isoformat(),
                'extraction_method': 'full_auto'
            }
            
            # Row element'i kaldır (JSON serialize edilemez)
            if 'row_element' in complete_prescription:
                del complete_prescription['row_element']
            
            print(f'[TAMAMLANDI] {prescription["recete_no"]} tam veri çıkarıldı')
            
            # Ana listeye geri dön
            self.go_back_to_prescription_list()
            
            return complete_prescription
            
        except Exception as e:
            print(f'[HATA] {prescription["recete_no"]} işlenirken hata: {e}')
            # Hata durumunda ana listeye dön
            try:
                self.go_back_to_prescription_list()
            except:
                pass
            return None
    
    def process_all_prescriptions_auto(self, limit=3):
        """Tüm reçeteleri otomatik işle"""
        try:
            print(f'[OTOMATIK] İlk {limit} reçete tam otomatik çıkarılacak...')
            
            # Reçete listesini çıkar
            prescription_list = self.extract_prescription_list_auto()
            
            if not prescription_list:
                print('[HATA] Reçete listesi boş!')
                return False
            
            # İlk N reçeteyi işle
            for index, prescription in enumerate(prescription_list[:limit], 1):
                complete_prescription = self.process_prescription_fully_auto(prescription, index, limit)
                
                if complete_prescription:
                    self.prescriptions_with_full_details.append(complete_prescription)
                    print(f'[BAŞARILI] {index}/{limit} reçete tamamlandı')
                else:
                    print(f'[ATLANDI] {index}/{limit} reçete atlandı')
                
                # Kısa bekleme
                time.sleep(1)
            
            print(f'\\n[TAMAMLANDI] {len(self.prescriptions_with_full_details)} reçete tam detayları ile çıkarıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Toplu işlem hatası: {e}')
            return False
    
    def save_full_prescriptions(self, filename='full_detailed_prescriptions.json'):
        """Tam detaylı reçete verilerini kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.prescriptions_with_full_details, f, ensure_ascii=False, indent=2)
            
            print(f'[KAYDET] {len(self.prescriptions_with_full_details)} tam detaylı reçete {filename} dosyasına kaydedildi')
            
            # Özet bilgi
            self.print_extraction_summary()
            
            return True
            
        except Exception as e:
            print(f'[HATA] Dosya kaydetme hatası: {e}')
            return False
    
    def print_extraction_summary(self):
        """Çıkarma özeti yazdır"""
        if not self.prescriptions_with_full_details:
            return
            
        print(f'\\n[ÖZET] ÇIKARILAN VERİLER:')
        print(f'=' * 50)
        
        for i, prescription in enumerate(self.prescriptions_with_full_details, 1):
            print(f'\\n{i}. REÇETE: {prescription.get("recete_no", "N/A")}')
            print(f'  Hasta: {prescription.get("hasta_ad_soyad", "N/A")}')
            print(f'  TC: {prescription.get("hasta_tc", "N/A")}')
            print(f'  İlaç Sayısı: {len(prescription.get("drugs", []))}')
            print(f'  Rapor No: {prescription.get("report_details", {}).get("rapor_numarasi", "N/A")}')
            print(f'  ICD Kodları: {len(prescription.get("report_details", {}).get("tani_bilgileri", []))}')
            print(f'  İlaç Mesajları: {len(prescription.get("drug_messages", []))}')
    
    def close(self):
        """Browser'ı kapat"""
        self.browser.quit()
        print('[KAPAT] Browser kapatıldı')

def main():
    extractor = AdvancedPrescriptionExtractor()
    
    try:
        # Başlat ve giriş yap
        if not extractor.start():
            return
        
        print('\\n[BİLGİ] Otomatik navigasyon başlıyor...')
        input('Hazırlanmak için ENTER basın...')
        
        # Reçete listesine git
        if not extractor.navigate_to_prescriptions_auto():
            return
        
        # Filtreleri ayarla
        if not extractor.set_filters_auto('A'):
            return
        
        # Tüm reçeteleri otomatik işle
        if extractor.process_all_prescriptions_auto(limit=3):
            # Verileri kaydet
            extractor.save_full_prescriptions('advanced_prescriptions.json')
            
            print(f'\\n[BAŞARILI] Gelişmiş reçete çıkarma tamamlandı!')
            print(f'Dosya: advanced_prescriptions.json')
        else:
            print('\\n[HATA] Otomatik işlem başarısız!')
    
    finally:
        input('İncelemek için ENTER basın...')
        extractor.close()

if __name__ == "__main__":
    main()