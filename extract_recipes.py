from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('📋 Reçete verilerini çekiyorum...')

# Tablo verilerini bul
tables = browser.driver.find_elements('xpath', "//table")
print(f'📊 {len(tables)} tablo bulundu')

for table_index, table in enumerate(tables):
    print(f'\n--- TABLO {table_index + 1} ---')
    
    # Tablo başlıkları
    headers = table.find_elements('xpath', ".//th")
    if headers:
        print('📝 Başlıklar:')
        for i, header in enumerate(headers):
            print(f'  {i+1}. {header.text.strip()}')
    
    # Tablo satırları (ilk 5 satır)
    rows = table.find_elements('xpath', ".//tr")
    print(f'📄 {len(rows)} satır bulundu (ilk 5 tanesi):')
    
    for row_index, row in enumerate(rows[:5]):
        cells = row.find_elements('xpath', ".//td | .//th")
        if cells:
            cell_texts = []
            for cell in cells:
                text = cell.text.strip()
                if text:
                    cell_texts.append(text[:30])  # İlk 30 karakter
            
            if cell_texts:
                print(f'  Satır {row_index+1}: {" | ".join(cell_texts)}')

print('\nReçete veri analizi tamamlandı!')
input('Browser kapatmak için ENTER bas...')
browser.quit()