from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 Sol menüde "Reçete Listesi" linkini arıyorum...')

# Sol menü linklerini ara
try:
    # Sol menüdeki linkleri bul
    menu_links = browser.driver.find_elements(By.XPATH, "//td[@bgcolor='#FFFFFF']//a")
    
    print(f'📋 Sol menüde {len(menu_links)} link bulundu:')
    
    recete_listesi_link = None
    
    for i, link in enumerate(menu_links):
        try:
            text = link.text.strip()
            href = link.get_attribute('href')
            print(f'{i+1}. "{text}" -> {href}')
            
            # AYLIK reçete listesi (günlük değil)
            if 'reçete listesi' in text.lower() and 'günlük' not in text.lower():
                recete_listesi_link = link
                print(f'   ✅ Bu AYLIK "Reçete Listesi" linki!')
        except Exception as e:
            print(f'   Hata: {e}')
    
    if recete_listesi_link:
        print('\n🎯 "Reçete Listesi" linkine tıklıyorum...')
        recete_listesi_link.click()
        
        time.sleep(3)
        
        print('✅ Reçete Listesi sayfasına gidildi!')
        print(f'📍 Yeni URL: {browser.driver.current_url}')
        print(f'📄 Sayfa Başlığı: {browser.driver.title}')
        
        # Reçete tablosunu kontrol et
        print('\n📊 Reçete tablosunu kontrol ediyorum...')
        tables = browser.driver.find_elements(By.XPATH, "//table")
        
        for table_index, table in enumerate(tables):
            rows = table.find_elements(By.XPATH, ".//tr")
            if len(rows) > 1:  # En az 2 satır
                print(f'\n--- TABLO {table_index + 1} ({len(rows)} satır) ---')
                
                # İlk 5 satır
                for row_index, row in enumerate(rows[:5]):
                    cells = row.find_elements(By.XPATH, ".//td | .//th")
                    if cells:
                        cell_texts = []
                        for cell in cells:
                            text = cell.text.strip()[:30]  # İlk 30 karakter
                            cell_texts.append(text)
                        
                        print(f'Satır {row_index+1}: {" | ".join(cell_texts)}')
    else:
        print('❌ "Reçete Listesi" linki bulunamadı')
        
        # Alternatif: İlk reçete linkine tıkla
        for link in menu_links:
            text = link.text.strip().lower()
            if 'reçete' in text and 'listesi' in text:
                print(f'🔄 Alternatif link denenecek: "{link.text}"')
                link.click()
                time.sleep(3)
                break

except Exception as e:
    print(f'❌ Hata oluştu: {e}')

input('\nİşlem tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()