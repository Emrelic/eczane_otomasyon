from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
print('Kullanici adin: 18342920')
print('Sifrene: 571T03s0')
input('Giris yaptiktan sonra ENTER bas...')
print('Program devam ediyor...')

# Reçete listesini bul ve tıkla
try:
    # Reçete linkini ara
    import time
    time.sleep(2)
    
    # Muhtemel reçete linki
    recete_links = browser.driver.find_elements('xpath', "//a[contains(text(), 'reçete') or contains(text(), 'Reçete') or contains(text(), 'A Grubu')]")
    
    if recete_links:
        print(f'✅ {len(recete_links)} adet reçete linki bulundu!')
        for i, link in enumerate(recete_links):
            print(f'{i+1}. {link.text}')
        
        print('İlk linke tıklıyorum...')
        recete_links[0].click()
        time.sleep(3)
        print('✅ Reçete sayfası açıldı!')
    else:
        print('❌ Reçete linki bulunamadı')
        
    input('Browser kapatmak için ENTER bas...')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    input('Browser kapatmak için ENTER bas...')

browser.quit()