from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 "Reçete Listesi" tıklama ve frame kontrol...')

try:
    # 1. İlk "Reçete Listesi" elementini bul
    recete_elements = browser.driver.find_elements(By.XPATH, "//*[text()='Reçete Listesi']")
    
    if recete_elements:
        print(f'✅ {len(recete_elements)} adet "Reçete Listesi" bulundu')
        
        target_element = None
        for i, element in enumerate(recete_elements):
            try:
                # Parent elementini kontrol et
                parent = element.find_element(By.XPATH, "./..")
                parent_text = parent.text.strip()
                
                print(f'{i+1}. Element parent: "{parent_text}"')
                
                # Eğer sadece "Reçete Listesi" ise bu bizim hedefimiz
                if parent_text == "Reçete Listesi":
                    target_element = element
                    print(f'🎯 Hedef element bulundu!')
                    break
                    
            except:
                pass
        
        if not target_element:
            target_element = recete_elements[0]  # İlk olanı al
            print('🔄 İlk "Reçete Listesi" elementini kullanıyorum')
        
        # Tıkla
        print('🔗 Element tıklanıyor...')
        browser.driver.execute_script("arguments[0].click();", target_element)
        
        # Bekle
        time.sleep(2)
        
        # Frame'leri kontrol et
        print('🖼️ Frame kontrol ediliyor...')
        frames = browser.driver.find_elements(By.TAG_NAME, "frame")
        iframes = browser.driver.find_elements(By.TAG_NAME, "iframe")
        
        all_frames = frames + iframes
        print(f'📋 Toplam {len(all_frames)} frame bulundu')
        
        # Her frame'i kontrol et
        for frame_index, frame in enumerate(all_frames):
            try:
                print(f'\n--- FRAME {frame_index + 1} ---')
                name = frame.get_attribute('name') or 'NoName'
                src = frame.get_attribute('src') or 'NoSrc'
                
                print(f'Name: {name}')
                print(f'Src: {src}')
                
                # Frame'e geç
                browser.driver.switch_to.frame(frame)
                
                # Frame içeriğini kontrol et
                frame_title = browser.driver.title
                frame_url = browser.driver.current_url
                
                print(f'Frame Title: {frame_title}')
                print(f'Frame URL: {frame_url}')
                
                # Frame içinde tablo var mı?
                tables = browser.driver.find_elements(By.TAG_NAME, "table")
                print(f'Frame içinde {len(tables)} tablo var')
                
                # Reçete verileri için tablolar
                for table_index, table in enumerate(tables):
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 3:  # En az 4 satır
                        print(f'\n  TABLO {table_index + 1} ({len(rows)} satır):')
                        
                        # İlk satır başlık
                        if rows:
                            first_row = rows[0]
                            headers = first_row.find_elements(By.XPATH, ".//th | .//td")
                            header_texts = [h.text.strip()[:15] for h in headers if h.text.strip()]
                            
                            if len(header_texts) > 2:  # En az 3 sütun
                                print(f'    Başlıklar: {" | ".join(header_texts)}')
                                
                                # İlk veri satırı
                                if len(rows) > 1:
                                    data_row = rows[1]
                                    data_cells = data_row.find_elements(By.XPATH, ".//td")
                                    data_texts = [d.text.strip()[:15] for d in data_cells if d.text.strip()]
                                    
                                    if data_texts:
                                        print(f'    İlk veri: {" | ".join(data_texts)}')
                                        print(f'    ✅ REÇETE VERİLERİ BULUNDU!')
                
                # Ana frame'e dön
                browser.driver.switch_to.default_content()
                
            except Exception as e:
                print(f'    Frame {frame_index + 1} hatası: {e}')
                browser.driver.switch_to.default_content()
    
    else:
        print('❌ "Reçete Listesi" elementi bulunamadı')

except Exception as e:
    print(f'❌ Genel hata: {e}')

input('\nFrame analizi tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()