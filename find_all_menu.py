from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()
browser.driver.get('https://medeczane.sgk.gov.tr/eczane/')
print('Browser acik - manuel giris yap!')
input('Ana sayfaya girip ENTER bas...')

print('🔍 TÜM menü linklerini tarıyorum...')

# Tüm linkleri bul
all_links = browser.driver.find_elements('xpath', "//a")

print(f'📋 Toplam {len(all_links)} link bulundu:')
print('\n--- REÇETE İLE İLGİLİ LİNKLER ---')

recete_related = []
for i, link in enumerate(all_links):
    try:
        text = link.text.strip()
        href = link.get_attribute('href')
        
        if text and ('reçete' in text.lower() or 'recete' in text.lower()):
            recete_related.append((text, href))
            print(f'✅ "{text}" -> {href}')
    except:
        pass

if not recete_related:
    print('❌ Reçete ile ilgili link bulunamadı')
    
    print('\n--- TÜM MENÜ LİNKLERİ ---')
    for i, link in enumerate(all_links[:20]):  # İlk 20 link
        try:
            text = link.text.strip()
            href = link.get_attribute('href')
            
            if text and href and 'javascript' not in href.lower():
                print(f'{i+1}. "{text}" -> {href}')
        except:
            pass

print('\n--- FRAME/IFRAME KONTROLÜ ---')
# Frame'leri kontrol et
frames = browser.driver.find_elements('xpath', "//frame | //iframe")
if frames:
    print(f'🖼️ {len(frames)} frame bulundu')
    for i, frame in enumerate(frames):
        src = frame.get_attribute('src')
        name = frame.get_attribute('name')
        print(f'Frame {i+1}: name="{name}" src="{src}"')
        
        # Frame'e geç ve içeriğini kontrol et
        try:
            browser.driver.switch_to.frame(frame)
            frame_links = browser.driver.find_elements('xpath', "//a")
            print(f'  Frame içinde {len(frame_links)} link var')
            
            for link in frame_links[:5]:  # İlk 5 link
                try:
                    text = link.text.strip()
                    if text and 'reçete' in text.lower():
                        href = link.get_attribute('href') 
                        print(f'    ✅ "{text}" -> {href}')
                except:
                    pass
            
            browser.driver.switch_to.default_content()  # Ana frame'e dön
        except:
            browser.driver.switch_to.default_content()
            print(f'  Frame {i+1} erişim hatası')
else:
    print('❌ Frame bulunamadı')

input('\nTüm analiz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()