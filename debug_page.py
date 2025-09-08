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

print('📄 Sayfa HTML içeriğini analiz ediyorum...')

# Tüm linkler
all_links = browser.driver.find_elements('xpath', "//a")
print(f'\n🔗 Toplam {len(all_links)} link bulundu:')
for i, link in enumerate(all_links[:10]):  # İlk 10 link
    try:
        text = link.text.strip()
        href = link.get_attribute('href')
        if text:  # Boş olmayan linkler
            print(f'{i+1}. "{text}" -> {href}')
    except:
        pass

# Tüm butonlar
all_buttons = browser.driver.find_elements('xpath', "//input[@type='button'] | //button")
print(f'\n🔘 Toplam {len(all_buttons)} buton bulundu:')
for i, button in enumerate(all_buttons):
    try:
        text = button.text or button.get_attribute('value')
        if text:
            print(f'{i+1}. "{text}"')
    except:
        pass

# Sayfa başlığı ve URL
print(f'\n📋 Sayfa Başlığı: {browser.driver.title}')
print(f'🔗 Mevcut URL: {browser.driver.current_url}')

input('\nAnaliz tamamlandı. Browser kapatmak için ENTER bas...')
browser.quit()