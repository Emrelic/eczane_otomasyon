from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🎯 "Reçete Listesi" tıklama ve uzun bekleme...')

elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'Reçete Listesi')]")
print(f'✅ {len(elements)} element bulundu')

for i, element in enumerate(elements):
    try:
        text = element.text.strip()
        print(f'{i+1}. "{text}"')
        
        if text == 'Reçete Listesi':
            print('🎯 HEDEF: "Reçete Listesi"')
            
            # URL'i kaydet
            old_url = browser.driver.current_url
            print(f'📍 Eski URL: {old_url}')
            
            # Tıkla
            browser.driver.execute_script("arguments[0].click();", element)
            print('🔗 Tıklandı!')
            
            # Uzun bekle ve kontrol et
            for wait_time in range(1, 11):  # 10 saniyeye kadar bekle
                time.sleep(1)
                current_url = browser.driver.current_url
                
                print(f'⏱️  {wait_time}s - URL: {current_url}')
                
                # URL değişti mi?
                if current_url != old_url:
                    print(f'✅ URL DEĞİŞTİ! Yeni: {current_url}')
                    break
                
                # Sayfa içeriği değişti mi?
                page_source = browser.driver.page_source
                if 'reçete no' in page_source.lower() or 'hasta ad' in page_source.lower():
                    print('✅ SAYFA İÇERİĞİ DEĞİŞTİ!')
                    break
            
            # Final kontrol
            print('\n📊 SON DURUM:')
            print(f'URL: {browser.driver.current_url}')
            print(f'Title: {browser.driver.title}')
            
            # Tüm tabloları detaylı kontrol
            tables = browser.driver.find_elements(By.TAG_NAME, "table")
            print(f'\n📋 {len(tables)} tablo analizi:')
            
            for table_index, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 0:
                    print(f'\n--- TABLO {table_index + 1} ({len(rows)} satır) ---')
                    
                    # İlk 3 satır
                    for row_index, row in enumerate(rows[:3]):
                        cells = row.find_elements(By.XPATH, ".//td | .//th")
                        if cells:
                            cell_texts = []
                            for cell in cells[:8]:  # İlk 8 sütun
                                text = cell.text.strip()[:25]
                                if text:
                                    cell_texts.append(text)
                            
                            if cell_texts and len(cell_texts) > 1:
                                print(f'  Satır {row_index+1}: {" | ".join(cell_texts)}')
                    
                    # Reçete benzeri veriler var mı?
                    table_text = table.text.lower()
                    if any(keyword in table_text for keyword in ['tc', 'hasta', 'ilaç', 'reçete no', 'tutar']):
                        print(f'  ⭐ Bu tablo reçete verileri içerebilir!')
            
            break
    except Exception as e:
        print(f'Hata: {e}')

input('\nDetaylı analiz tamamlandı. ENTER bas...')
browser.quit()