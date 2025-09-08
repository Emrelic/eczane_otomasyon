from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 TÜM TÜRKÇE VARYASYONLARI ARANACAK...')

# Türkçe karakter varyasyonları
search_terms = [
    'Reçete Listesi',
    'Recete Listesi', 
    'ReÃ§ete Listesi',
    'Re&ccedil;ete Listesi',
    'REÇETE LİSTESİ',
    'reçete listesi'
]

print(f'📋 {len(search_terms)} farklı varyasyon aranacak')

found_elements = []

for search_term in search_terms:
    print(f'\n🔍 Aranan: "{search_term}"')
    
    # XPath ile ara
    xpath_patterns = [
        f"//*[text()='{search_term}']",
        f"//*[contains(text(), '{search_term}')]",
        f"//span[text()='{search_term}']",
        f"//td[text()='{search_term}']",
        f"//a[text()='{search_term}']"
    ]
    
    for pattern in xpath_patterns:
        try:
            elements = browser.driver.find_elements(By.XPATH, pattern)
            if elements:
                print(f'  ✅ {len(elements)} element bulundu: {pattern}')
                for element in elements:
                    if element not in found_elements:
                        found_elements.append(element)
        except:
            pass

print(f'\n📊 TOPLAM {len(found_elements)} benzersiz element bulundu')

# Her elementi dene
for i, element in enumerate(found_elements):
    try:
        text = element.text.strip()
        tag = element.tag_name
        
        print(f'\n{i+1}. <{tag}> "{text}"')
        
        # Bu element tam "Reçete Listesi" mi?
        if ('reçete listesi' in text.lower() or 'recete listesi' in text.lower()) and 'günlük' not in text.lower():
            print(f'🎯 HEDEF: "{text}"')
            
            # Kaydır
            browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Tıkla
            print('🔗 Tıklanıyor...')
            try:
                element.click()
                print('  ✅ Normal click')
            except:
                try:
                    browser.driver.execute_script("arguments[0].click();", element)
                    print('  ✅ JavaScript click')
                except:
                    print('  ❌ Tıklama başarısız')
                    continue
            
            time.sleep(3)
            
            # URL değişti mi?
            current_url = browser.driver.current_url
            print(f'📍 Yeni URL: {current_url}')
            
            # Sayfa kaynağında reçete var mı?
            page_source = browser.driver.page_source
            if 'hasta' in page_source.lower() or 'ilaç' in page_source.lower() or 'tc' in page_source.lower():
                print('✅ Sayfa içeriğinde reçete terimleri var!')
                
                # Tabloları kontrol et
                tables = browser.driver.find_elements(By.TAG_NAME, "table")
                print(f'📊 {len(tables)} tablo bulundu')
                
                for table_index, table in enumerate(tables):
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 2:
                        print(f'\n--- TABLO {table_index + 1} ({len(rows)} satır) ---')
                        
                        # İlk satır
                        if rows:
                            first_row = rows[0]
                            cells = first_row.find_elements(By.XPATH, ".//td | .//th")
                            if cells:
                                cell_texts = [c.text.strip()[:20] for c in cells if c.text.strip()]
                                print(f'Başlıklar: {" | ".join(cell_texts)}')
                
                print('🎉 REÇETE VERİLERİ BULUNDU!')
                break
            else:
                print('❌ Reçete verileri bulunamadı')
    
    except Exception as e:
        print(f'  Hata: {e}')

input('\nTürkçe karakter analizi tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()