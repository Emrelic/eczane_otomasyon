from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🎯 HIZLI "Reçete Listesi" arama...')

# Sadece en muhtemel pattern
elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'Reçete Listesi')]")
print(f'✅ {len(elements)} element bulundu')

for i, element in enumerate(elements):
    try:
        text = element.text.strip()
        print(f'{i+1}. "{text}"')
        
        # Tam "Reçete Listesi" (günlük değil)
        if text == 'Reçete Listesi':
            print('🎯 HEDEF BULUNDU!')
            
            # Tıkla
            browser.driver.execute_script("arguments[0].click();", element)
            time.sleep(5)  # Daha fazla bekle
            
            print('✅ Tıklandı!')
            print(f'📍 URL: {browser.driver.current_url}')
            
            # Tabloları göster
            tables = browser.driver.find_elements(By.TAG_NAME, "table")
            print(f'📊 {len(tables)} tablo bulundu')
            
            for table_index, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 3:
                    print(f'\nTablo {table_index+1}: {len(rows)} satır')
                    
                    # İlk satır
                    first_row = rows[0]
                    cells = first_row.find_elements(By.XPATH, ".//td | .//th")
                    cell_texts = [c.text.strip()[:15] for c in cells if c.text.strip()][:6]
                    if cell_texts:
                        print(f'Başlıklar: {" | ".join(cell_texts)}')
            
            break
    except Exception as e:
        print(f'Hata: {e}')

input('İşlem tamamlandı. ENTER bas...')
browser.quit()