"""
Reçete Detay Bilgileri Çıkarma Sistemi
Reçete listesindeki her reçetenin detaylarına girerek tüm bilgileri çıkarır
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

class PrescriptionDetailExtractor:
    def __init__(self):
        self.browser = MedulaBrowser(Settings())
        self.wait = None
        self.prescriptions_with_details = []
    
    def start(self):
        """Browser'ı başlat ve giriş yap"""
        print('[BAŞLAT] Detaylı reçete çıkarma sistemi başlatılıyor...')
        success = self.browser.start()
        
        if success:
            self.wait = WebDriverWait(self.browser.driver, 10)
            if self.browser.login():
                print('[BAŞARILI] Medula girişi başarılı!')
                return True
            else:
                print('[HATA] Medula girişi başarısız!')
                return False
        return False
    
    def navigate_to_prescriptions(self):
        """Reçete listesi sayfasına git"""
        try:
            print('[NAVİGASYON] Reçete Listesi sayfasına gidiliyor...')
            
            # Farklı selector'ları dene
            selectors = [
                "//*[text()='Reçete Listesi']",
                "//*[contains(text(), 'Reçete Listesi')]",
                "//*[contains(text(), 'Re')]//ancestor::a",
                "//a[contains(text(), 'Reçete')]",
                "//li[contains(text(), 'Reçete Listesi')]",
                "//*[contains(@href, 'recete') or contains(@href, 'Recete')]"
            ]
            
            recete_link = None
            for selector in selectors:
                try:
                    recete_link = self.browser.driver.find_element(By.XPATH, selector)
                    print(f'[BULUNAN] Reçete Listesi linki bulundu: {selector}')
                    break
                except:
                    continue
            
            if recete_link:
                # JavaScript ile tıkla (daha güvenli)
                self.browser.driver.execute_script("arguments[0].click();", recete_link)
                time.sleep(5)  # Daha fazla bekle
                print('[BAŞARILI] Reçete Listesi sayfası açıldı')
                return True
            else:
                print('[MANUEL] Lütfen sol menüden "Reçete Listesi" linkine tıklayın')
                input('Reçete Listesi sayfası açıldıktan sonra ENTER basın...')
                return True
            
        except Exception as e:
            print(f'[HATA] Reçete listesi sayfasına gidilemedi: {e}')
            print('[MANUEL] Lütfen sol menüden "Reçete Listesi" linkine tıklayın')
            input('Reçete Listesi sayfası açıldıktan sonra ENTER basın...')
            return True
    
    def set_filters_and_search(self, group='A'):
        """Filtreleri ayarla ve arama yap"""
        try:
            print(f'[FİLTRE] {group} Grubu için filtreler ayarlanıyor...')
            
            # Farklı dropdown name'lerini dene
            dropdown_selectors = [
                "faturaTuru",
                "faturaTipi", 
                "fatura_turu",
                "fatura_tipi",
                "group",
                "grubu"
            ]
            
            fatura_dropdown = None
            for selector in dropdown_selectors:
                try:
                    dropdown_element = self.browser.driver.find_element(By.NAME, selector)
                    fatura_dropdown = Select(dropdown_element)
                    print(f'[BULUNAN] Fatura dropdown bulundu: {selector}')
                    break
                except:
                    continue
            
            # CSS selector ile de dene
            if not fatura_dropdown:
                try:
                    dropdown_element = self.browser.driver.find_element(By.CSS_SELECTOR, "select")
                    fatura_dropdown = Select(dropdown_element)
                    print('[BULUNAN] Fatura dropdown CSS ile bulundu')
                except:
                    pass
            
            if fatura_dropdown:
                # Farklı text seçeneklerini dene
                group_options = [f"{group} Grubu", f"{group} GRUBU", f"A Grubu", "A GRUBU"]
                
                for option in group_options:
                    try:
                        fatura_dropdown.select_by_visible_text(option)
                        print(f'[BAŞARILI] {option} seçildi')
                        break
                    except:
                        continue
                
                # Sorgula butonunu bul ve tıkla
                sorgula_selectors = [
                    "//input[@value='Sorgula']",
                    "//input[contains(@value, 'Sorgula')]", 
                    "//button[contains(text(), 'Sorgula')]",
                    "//input[@type='submit']"
                ]
                
                sorgula_button = None
                for selector in sorgula_selectors:
                    try:
                        sorgula_button = self.browser.driver.find_element(By.XPATH, selector)
                        print(f'[BULUNAN] Sorgula butonu bulundu: {selector}')
                        break
                    except:
                        continue
                
                if sorgula_button:
                    sorgula_button.click()
                    time.sleep(5)
                    print(f'[SORGU] {group} Grubu reçeteler sorgulandı')
                    return True
                else:
                    print('[MANUEL] Lütfen "Sorgula" butonuna manuel tıklayın')
                    input('Sorgu tamamlandıktan sonra ENTER basın...')
                    return True
            else:
                print('[MANUEL] Lütfen filtreyi manuel olarak ayarlayın ve sorgulayın')
                input('A Grubu seçip Sorgula butonuna bastıktan sonra ENTER basın...')
                return True
            
        except Exception as e:
            print(f'[HATA] Filtreleme hatası: {e}')
            print('[MANUEL] Lütfen filtreyi manuel olarak ayarlayın')
            input('A Grubu seçip Sorgula butonuna bastıktan sonra ENTER basın...')
            return True
    
    def get_prescription_list(self):
        """Ana listeden reçete satırlarını al"""
        try:
            print('[LİSTE] Reçete listesi alınıyor...')
            
            table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Reçete No')]]")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            prescription_rows = []
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
                            'row_element': row  # Tıklamak için element
                        }
                        prescription_rows.append(prescription_data)
                        
                except Exception as e:
                    print(f'[UYARI] Satır {row_index} işlenirken hata: {e}')
            
            print(f'[BAŞARILI] {len(prescription_rows)} reçete satırı alındı')
            return prescription_rows
            
        except Exception as e:
            print(f'[HATA] Reçete listesi alınırken hata: {e}')
            return []
    
    def click_prescription_row(self, prescription):
        """Reçete satırına tıklayarak detay sayfasına git"""
        try:
            print(f'[TIKLAMA] Reçete {prescription["recete_no"]} detayına giriliyor...')
            
            # Hasta isminin üzerine tıkla (screenshot'tan görüldüğü üzere)
            prescription['row_element'].click()
            time.sleep(3)
            
            # Detay sayfasının yüklendiğini kontrol et
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'T.C. Kimlik No')]")))
            
            print('[BAŞARILI] Reçete detay sayfası açıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Reçete detayına girilemedi: {e}')
            return False
    
    def extract_basic_prescription_info(self):
        """Temel reçete bilgilerini çıkar"""
        try:
            print('[ÇIKARMA] Temel reçete bilgileri çıkarılıyor...')
            
            # Hasta bilgileri
            tc_no = self.browser.driver.find_element(By.XPATH, "//td[text()='T.C. Kimlik No']/following-sibling::td").text.strip()
            hasta_ad_soyad = self.browser.driver.find_element(By.XPATH, "//td[text()='Adı / Soyadı']/following-sibling::td").text.strip()
            cinsiyet = self.browser.driver.find_element(By.XPATH, "//td[text()='Cinsiyeti']/following-sibling::td").text.strip()
            dogum_tarihi = self.browser.driver.find_element(By.XPATH, "//td[text()='Doğum Tarihi']/following-sibling::td").text.strip()
            
            # Reçete bilgileri (üst kısım)
            recete_no = self.browser.driver.find_element(By.XPATH, "//td[contains(text(), 'Reçete No:')]/following-sibling::td").text.strip()
            karekod_durumu = self.browser.driver.find_element(By.XPATH, "//td[contains(text(), 'Karekod Durumu:')]/following-sibling::td").text.strip()
            
            basic_info = {
                'hasta_tc': tc_no,
                'hasta_ad_soyad': hasta_ad_soyad,
                'cinsiyet': cinsiyet,
                'dogum_tarihi': dogum_tarihi,
                'recete_no': recete_no,
                'karekod_durumu': karekod_durumu,
                'extraction_time': datetime.now().isoformat()
            }
            
            print('[BAŞARILI] Temel bilgiler çıkarıldı')
            return basic_info
            
        except Exception as e:
            print(f'[HATA] Temel bilgi çıkarma hatası: {e}')
            return {}
    
    def extract_drug_list(self):
        """İlaç listesini çıkar"""
        try:
            print('[ÇIKARMA] İlaç listesi çıkarılıyor...')
            
            # İlaç tablosunu bul
            drug_table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Barkod')]]")
            drug_rows = drug_table.find_elements(By.TAG_NAME, "tr")
            
            drugs = []
            for row_index, row in enumerate(drug_rows[1:], 1):  # Başlık atla
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 8:  # En az 8 sütun olmalı
                        
                        # Checkbox kontrolü (seçili mi?)
                        checkbox = cells[0].find_element(By.TAG_NAME, "input") if cells[0].find_elements(By.TAG_NAME, "input") else None
                        is_selected = checkbox.is_selected() if checkbox else False
                        
                        drug_data = {
                            'secili': is_selected,
                            'barkod': cells[1].text.strip(),
                            'ilac_adi': cells[2].text.strip(),
                            'adet': cells[3].text.strip().split('/')[0].strip(),  # "3 / 1" formatından 3'ü al
                            'penyol': cells[3].text.strip().split('/')[1].strip() if '/' in cells[3].text else '',
                            'doz': cells[4].text.strip(),
                            'ilac_tutari': cells[5].text.strip(),
                            'fark': cells[6].text.strip(),
                            'rapor': cells[7].text.strip(),
                            'verilebilecegi': cells[8].text.strip() if len(cells) > 8 else '',
                            'mesaj_var': cells[9].text.strip() if len(cells) > 9 else ''
                        }
                        
                        drugs.append(drug_data)
                        
                except Exception as e:
                    print(f'[UYARI] İlaç satırı {row_index} işlenirken hata: {e}')
            
            print(f'[BAŞARILI] {len(drugs)} ilaç bilgisi çıkarıldı')
            return drugs
            
        except Exception as e:
            print(f'[HATA] İlaç listesi çıkarma hatası: {e}')
            return []
    
    def click_ilac_bilgileri_button(self):
        """İlaç Bilgileri butonuna tıkla"""
        try:
            print('[NAVİGASYON] İlaç Bilgileri sayfasına gidiliyor...')
            
            ilac_bilgi_button = self.browser.driver.find_element(By.XPATH, "//input[@value='İlaç Bilgi']")
            ilac_bilgi_button.click()
            time.sleep(2)
            
            print('[BAŞARILI] İlaç Bilgileri sayfası açıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] İlaç Bilgileri sayfasına gidilemedi: {e}')
            return False
    
    def extract_drug_details(self):
        """İlaç detay bilgilerini çıkar"""
        try:
            print('[ÇIKARMA] İlaç detay bilgileri çıkarılıyor...')
            
            # İlaç detay bilgileri
            drug_details = {}
            
            # İlaç bilgileri bölümünden veri çıkar
            detail_fields = [
                'İlaç Adı', 'Ambalaj Miktarı', 'Farmasötik Formu', 
                'Tek Doz Miktarı', 'Kullanım Süresi', 'Yaş Aralığı',
                'Cinsiyet', 'Perakende/Ödenen Fiyat', 'Kamu İndirim Oranı',
                'Reçete Türü', 'Kamukod No', 'Ay Aralığı',
                'Tedavi Seması Gerekli', 'Yatan Reçetesi', 'Ayaktan Reçetesi',
                'Ayaktan Maks. Kul. Doz', 'Yatan Maks. Kul. Doz',
                'Raporlu Maks. Kul. Doz', 'Takipli İlaç Sayısı',
                'Maksimum İlaç Adet', 'Günlük Maks.Kalori Miktarı',
                'Kutu Birim Doz Miktarı', 'Birim Doz Miktarı',
                'Etkin Madde'
            ]
            
            for field in detail_fields:
                try:
                    element = self.browser.driver.find_element(By.XPATH, f"//td[contains(text(), '{field}')]/following-sibling::td")
                    drug_details[field.lower().replace(' ', '_')] = element.text.strip()
                except:
                    pass
            
            print('[BAŞARILI] İlaç detay bilgileri çıkarıldı')
            return drug_details
            
        except Exception as e:
            print(f'[HATA] İlaç detay çıkarma hatası: {e}')
            return {}
    
    def extract_drug_messages(self):
        """İlaç mesajlarını çıkar"""
        try:
            print('[ÇIKARMA] İlaç mesajları çıkarılıyor...')
            
            messages = []
            
            # İlaç Mesaj tablosunu bul
            try:
                message_table = self.browser.driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'İlaç Mesajı')]]")
                message_rows = message_table.find_elements(By.TAG_NAME, "tr")
                
                for row in message_rows[1:]:  # Başlık atla
                    message_text = row.find_element(By.TAG_NAME, "td").text.strip()
                    if message_text:
                        messages.append(message_text)
                        
            except:
                print('[BİLGİ] İlaç mesajı bulunamadı')
            
            print(f'[BAŞARILI] {len(messages)} ilaç mesajı çıkarıldı')
            return messages
            
        except Exception as e:
            print(f'[HATA] İlaç mesajları çıkarma hatası: {e}')
            return []
    
    def click_rapor_button(self):
        """Rapor butonuna tıkla"""
        try:
            print('[NAVİGASYON] Rapor sayfasına gidiliyor...')
            
            rapor_button = self.browser.driver.find_element(By.XPATH, "//input[@value='Rapor']")
            rapor_button.click()
            time.sleep(2)
            
            print('[BAŞARILI] Rapor sayfası açıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Rapor sayfasına gidilemedi: {e}')
            return False
    
    def extract_report_info(self):
        """Rapor bilgilerini çıkar"""
        try:
            print('[ÇIKARMA] Rapor bilgileri çıkarılıyor...')
            
            report_info = {}
            
            # Rapor bilgileri
            report_fields = [
                'Rapor Numarası (*)', 'Rapor Tarihi (*)',
                'Protokol No', 'Düzenleme Türü',
                'Açıklama', 'Kayıt Şekli',
                'Tesis Kodu (*)', 'Rapor Takip No',
                'Tesis Ünvanı', 'Kullanıcı Adı'
            ]
            
            for field in report_fields:
                try:
                    element = self.browser.driver.find_element(By.XPATH, f"//td[contains(text(), '{field}')]/following-sibling::td")
                    clean_field = field.replace('(*)', '').replace(' ', '_').lower().strip()
                    report_info[clean_field] = element.text.strip()
                except:
                    pass
            
            print('[BAŞARILI] Rapor bilgileri çıkarıldı')
            return report_info
            
        except Exception as e:
            print(f'[HATA] Rapor bilgisi çıkarma hatası: {e}')
            return {}
    
    def go_back_to_prescription_list(self):
        """Reçete listesine geri dön"""
        try:
            print('[NAVİGASYON] Reçete listesine geri dönülüyor...')
            
            # Geri Dön butonuna tıkla
            geri_button = self.browser.driver.find_element(By.XPATH, "//input[@value='Geri Dön']")
            geri_button.click()
            time.sleep(2)
            
            print('[BAŞARILI] Reçete listesine geri dönüldü')
            return True
            
        except Exception as e:
            print(f'[HATA] Geri dönüş hatası: {e}')
            return False
    
    def process_all_prescriptions(self, limit=5):
        """Tüm reçeteleri işle (test için limit koy)"""
        try:
            print(f'[İŞLEM] İlk {limit} reçete detayları çıkarılacak...')
            
            # Ana listeyi al
            prescription_list = self.get_prescription_list()
            
            if not prescription_list:
                print('[HATA] Reçete listesi boş!')
                return False
            
            # İlk N reçeteyi işle
            for index, prescription in enumerate(prescription_list[:limit], 1):
                try:
                    print(f'\n[İŞLEM {index}/{limit}] Reçete: {prescription["recete_no"]}')
                    
                    # Reçete detayına gir
                    if not self.click_prescription_row(prescription):
                        continue
                    
                    # Temel bilgileri çıkar
                    basic_info = self.extract_basic_prescription_info()
                    drug_list = self.extract_drug_list()
                    
                    # İlaç bilgilerine git
                    if self.click_ilac_bilgileri_button():
                        drug_details = self.extract_drug_details()
                        drug_messages = self.extract_drug_messages()
                        
                        # Geri dön
                        self.go_back_to_prescription_list()
                        time.sleep(1)
                        
                        # Tekrar detaya gir (rapor için)
                        if self.click_prescription_row(prescription):
                            # Rapor bilgilerine git
                            if self.click_rapor_button():
                                report_info = self.extract_report_info()
                            else:
                                report_info = {}
                        else:
                            report_info = {}
                    else:
                        drug_details = {}
                        drug_messages = []
                        report_info = {}
                    
                    # Tüm bilgileri birleştir
                    complete_prescription = {
                        **prescription,
                        **basic_info,
                        'drug_list': drug_list,
                        'drug_details': drug_details,
                        'drug_messages': drug_messages,
                        'report_info': report_info
                    }
                    
                    # Row element'i JSON'a çevrilemez, kaldır
                    if 'row_element' in complete_prescription:
                        del complete_prescription['row_element']
                    
                    self.prescriptions_with_details.append(complete_prescription)
                    
                    print(f'[BAŞARILI] Reçete {prescription["recete_no"]} tamamlandı')
                    
                    # Liste sayfasına geri dön
                    self.go_back_to_prescription_list()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f'[HATA] Reçete {prescription["recete_no"]} işlenirken hata: {e}')
                    # Hata durumunda ana listeye dön
                    try:
                        self.go_back_to_prescription_list()
                    except:
                        pass
            
            print(f'\\n[TAMAMLANDI] {len(self.prescriptions_with_details)} reçete detayı çıkarıldı')
            return True
            
        except Exception as e:
            print(f'[HATA] Toplu işlem hatası: {e}')
            return False
    
    def save_detailed_prescriptions(self, filename='detailed_prescriptions.json'):
        """Detaylı reçete verilerini dosyaya kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.prescriptions_with_details, f, ensure_ascii=False, indent=2)
            
            print(f'[KAYDET] {len(self.prescriptions_with_details)} detaylı reçete {filename} dosyasına kaydedildi')
            return True
            
        except Exception as e:
            print(f'[HATA] Dosya kaydetme hatası: {e}')
            return False
    
    def close(self):
        """Browser'ı kapat"""
        self.browser.quit()
        print('[KAPAT] Browser kapatıldı')

def main():
    extractor = PrescriptionDetailExtractor()
    
    try:
        # Başlat ve giriş yap
        if not extractor.start():
            return
        
        # Reçete listesine git
        if not extractor.navigate_to_prescriptions():
            return
        
        # A Grubu reçeteler için filtrele ve ara
        if not extractor.set_filters_and_search('A'):
            return
        
        # İlk 3 reçetin detaylarını çıkar (test için)
        if extractor.process_all_prescriptions(limit=3):
            # Detaylı verileri kaydet
            extractor.save_detailed_prescriptions('detailed_a_grubu_receteler.json')
            
            print(f'\\n[ÖZET] İşlem tamamlandı!')
            print(f'- İşlenen reçete sayısı: {len(extractor.prescriptions_with_details)}')
            print(f'- Her reçete için çıkarılan bilgiler:')
            print(f'  * Temel hasta/reçete bilgileri')
            print(f'  * İlaç listesi ve detayları')
            print(f'  * İlaç mesajları')
            print(f'  * Rapor bilgileri')
    
    finally:
        extractor.close()

if __name__ == "__main__":
    main()