from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 TÜM SAYFA LİNKLERİNİ ARIYORUM...')

# 1. Tüm linkleri bul (geniş arama)
all_links = browser.driver.find_elements(By.TAG_NAME, "a")
print(f'🔗 Toplam {len(all_links)} link bulundu')

recete_links = []
print('\n--- REÇETE İLE İLGİLİ LİNKLER ---')

for i, link in enumerate(all_links):
    try:
        text = link.text.strip()
        href = link.get_attribute('href')
        
        if text and 'reçete' in text.lower():
            recete_links.append((text, href, link))
            print(f'{len(recete_links)}. "{text}" -> {href}')
    except:
        pass

if recete_links:
    print(f'\n✅ {len(recete_links)} reçete linki bulundu!')
    
    # Aylık reçete listesini bul
    monthly_link = None
    for text, href, link_element in recete_links:
        if 'listesi' in text.lower() and 'günlük' not in text.lower():
            monthly_link = link_element
            print(f'🎯 AYLIK reçete linki: "{text}"')
            break
    
    if monthly_link:
        print('\n🔗 Aylık reçete listesi linkine tıklıyorum...')
        monthly_link.click()
        time.sleep(5)
        
        print('✅ Reçete listesi sayfası açıldı!')
        print(f'📍 Yeni URL: {browser.driver.current_url}')
        
        # Sayfa içeriğini kontrol et
        print('\n📊 Sayfa tabloları kontrol ediliyor...')
        tables = browser.driver.find_elements(By.TAG_NAME, "table")
        
        for table_index, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 2:  # En az 3 satır olan tablolar
                print(f'\n--- TABLO {table_index + 1} ({len(rows)} satır) ---')
                
                # İlk 3 satırı göster
                for row_index, row in enumerate(rows[:3]):
                    cells = row.find_elements(By.XPATH, ".//td | .//th")
                    if cells and len(cells) > 1:
                        cell_texts = []
                        for cell in cells[:6]:  # İlk 6 sütun
                            text = cell.text.strip()[:25]
                            cell_texts.append(text if text else "-")
                        
                        print(f'  Satır {row_index+1}: {" | ".join(cell_texts)}')
                
                print(f'  ... (toplam {len(rows)} satır)')
    else:
        print('❌ Aylık reçete linki bulunamadı')
        
        # Herhangi bir reçete linkine tıkla
        if recete_links:
            first_link = recete_links[0][2]
            print(f'🔄 İlk reçete linkine tıklanıyor: "{recete_links[0][0]}"')
            first_link.click()
            time.sleep(3)
else:
    print('❌ Hiç reçete linki bulunamadı')
    
    # HTML kaynak kodu kontrolü
    page_source = browser.driver.page_source
    if 'Reçete Listesi' in page_source:
        print('✅ Sayfa kaynağında "Reçete Listesi" var ama link bulunamadı')
        print('🔍 JavaScript ile yükleniyor olabilir')

input('\nDetaylı analiz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()