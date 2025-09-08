from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 "Reçete Listesi" linkini arıyorum...')

# "Reçete Listesi" linkini bul
recete_links = browser.driver.find_elements('xpath', "//a[contains(text(), 'Reçete Listesi')]")

if recete_links:
    print(f'✅ {len(recete_links)} adet "Reçete Listesi" linki bulundu!')
    
    for i, link in enumerate(recete_links):
        href = link.get_attribute('href')
        print(f'{i+1}. {link.text} -> {href}')
    
    print('İlk "Reçete Listesi" linkine tıklıyorum...')
    recete_links[0].click()
    
    time.sleep(3)
    
    print('✅ Reçete Listesi sayfasına gidildi!')
    print(f'📍 Yeni URL: {browser.driver.current_url}')
    print(f'📄 Sayfa Başlığı: {browser.driver.title}')
    
    # Reçete tablosunu ara
    print('\n📋 Reçete tablosunu arıyorum...')
    tables = browser.driver.find_elements('xpath', "//table")
    
    for table_index, table in enumerate(tables):
        rows = table.find_elements('xpath', ".//tr")
        if len(rows) > 2:  # En az 3 satır (başlık + veri)
            print(f'\n--- REÇETE TABLOSU {table_index + 1} ---')
            
            # Başlık satırı
            header_row = rows[0] if rows else None
            if header_row:
                headers = header_row.find_elements('xpath', ".//th | .//td")
                header_texts = [h.text.strip() for h in headers if h.text.strip()]
                if header_texts:
                    print('📝 Sütun Başlıkları:')
                    for i, header in enumerate(header_texts):
                        print(f'  {i+1}. {header}')
            
            # İlk 3 veri satırı
            print('📊 İlk 3 reçete kaydı:')
            for row_index, row in enumerate(rows[1:4]):  # 1-3 arası satırlar
                cells = row.find_elements('xpath', ".//td")
                if cells:
                    cell_texts = []
                    for cell in cells:
                        text = cell.text.strip()
                        cell_texts.append(text[:20] if text else "")  # İlk 20 karakter
                    
                    if any(cell_texts):  # En az bir hücre dolu
                        print(f'  Reçete {row_index+1}: {" | ".join(cell_texts)}')
    
else:
    print('❌ "Reçete Listesi" linki bulunamadı')

input('\nAnaliz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()