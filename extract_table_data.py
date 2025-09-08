from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('📊 TABLO VERİLERİNİ DETAYLI ÇEKİYORUM...')

# Sayfa kaynak kodunu kontrol et
page_source = browser.driver.page_source
if 'reçete' in page_source.lower():
    print('✅ Sayfada "reçete" kelimesi bulundu!')
else:
    print('❌ Sayfada "reçete" kelimesi bulunamadı')

# Tüm tabloları bul
tables = browser.driver.find_elements('xpath', "//table")
print(f'\n📋 Toplam {len(tables)} tablo bulundu')

for table_index, table in enumerate(tables):
    print(f'\n=== TABLO {table_index + 1} ===')
    
    # Tablo boyutları
    rows = table.find_elements('xpath', ".//tr")
    print(f'📄 {len(rows)} satır var')
    
    if len(rows) == 0:
        print('   (Boş tablo)')
        continue
    
    # Her satırı incele
    for row_index, row in enumerate(rows[:10]):  # İlk 10 satır
        cells = row.find_elements('xpath', ".//td | .//th")
        
        if cells:
            cell_data = []
            for cell_index, cell in enumerate(cells):
                text = cell.text.strip()
                
                # İçinde input var mı?
                inputs = cell.find_elements('xpath', ".//input")
                if inputs:
                    for inp in inputs:
                        inp_type = inp.get_attribute('type')
                        inp_value = inp.get_attribute('value')
                        text += f' [INPUT:{inp_type}={inp_value}]'
                
                # İçinde link var mı?
                links = cell.find_elements('xpath', ".//a")
                if links:
                    for link in links:
                        link_text = link.text.strip()
                        link_href = link.get_attribute('href')
                        if link_text:
                            text += f' [LINK:{link_text}]'
                
                cell_data.append(text[:50])  # İlk 50 karakter
            
            if any(cell_data):  # En az bir hücre dolu
                print(f'  Satır {row_index+1}: {" | ".join(cell_data)}')
    
    print(f'   (Toplam {len(rows)} satır)')

# Herhangi bir form var mı?
forms = browser.driver.find_elements('xpath', "//form")
print(f'\n📝 {len(forms)} form bulundu')

for i, form in enumerate(forms):
    action = form.get_attribute('action')
    method = form.get_attribute('method')
    print(f'  Form {i+1}: method={method} action={action}')

print(f'\n📍 Mevcut URL: {browser.driver.current_url}')
print(f'📄 Sayfa Başlığı: {browser.driver.title}')

input('\nDetaylı analiz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()