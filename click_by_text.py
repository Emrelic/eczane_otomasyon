from medula_automation.browser import MedulaBrowser
from config.settings import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 "Reçete Listesi" metnini BULUP TIKLAMA...')

try:
    # 1. Text içeren tüm elementleri bul
    all_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'Reçete') or contains(text(), 'reçete')]")
    
    print(f'📋 "Reçete" içeren {len(all_elements)} element bulundu:')
    
    for i, element in enumerate(all_elements):
        try:
            text = element.text.strip()
            tag_name = element.tag_name
            
            print(f'{i+1}. <{tag_name}> "{text}"')
            
            # TAM OLARAK "Reçete Listesi" (günlük olmayan)
            if text.lower().strip() == 'reçete listesi':
                print(f'🎯 HEDEF BULUNDU: "{text}"')
                
                # Element tıklanabilir mi kontrol et
                if element.is_enabled() and element.is_displayed():
                    print('✅ Element tıklanabilir durumda')
                    
                    # Önce kaydırma
                    browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    # Tıklama deneme 1: Normal click
                    try:
                        element.click()
                        print('🔗 Normal click başarılı')
                        time.sleep(3)
                        break
                    except:
                        print('⚠️ Normal click başarısız, JavaScript deneniyor...')
                        
                        # Tıklama deneme 2: JavaScript click
                        try:
                            browser.driver.execute_script("arguments[0].click();", element)
                            print('🔗 JavaScript click başarılı')
                            time.sleep(3)
                            break
                        except:
                            print('⚠️ JavaScript click başarısız, ActionChains deneniyor...')
                            
                            # Tıklama deneme 3: ActionChains
                            try:
                                actions = ActionChains(browser.driver)
                                actions.move_to_element(element).click().perform()
                                print('🔗 ActionChains click başarılı')
                                time.sleep(3)
                                break
                            except:
                                print('❌ Tüm tıklama yöntemleri başarısız')
                else:
                    print('❌ Element tıklanabilir durumda değil')
        except Exception as e:
            print(f'   Hata: {e}')
    
    # Sayfa değişti mi kontrol et
    current_url = browser.driver.current_url
    print(f'\n📍 Mevcut URL: {current_url}')
    
    if 'liste' in current_url.lower() or browser.driver.title != browser.driver.title:
        print('✅ Sayfa değişti! Reçete listesi açıldı olabilir.')
        
        # Tabloları kontrol et
        tables = browser.driver.find_elements(By.TAG_NAME, "table")
        print(f'📊 {len(tables)} tablo bulundu')
        
        for table_index, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 3:
                print(f'\n--- TABLO {table_index + 1} ---')
                print(f'📄 {len(rows)} satır var')
                
                # İlk satır (başlık)
                if rows:
                    first_row = rows[0]
                    headers = first_row.find_elements(By.XPATH, ".//th | .//td")
                    header_texts = [h.text.strip()[:20] for h in headers if h.text.strip()]
                    if header_texts:
                        print(f'📝 Başlıklar: {" | ".join(header_texts)}')
    else:
        print('❌ Sayfa değişmedi')

except Exception as e:
    print(f'❌ Genel hata: {e}')

input('\nAnaliz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()