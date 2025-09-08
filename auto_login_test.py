from medula_automation.browser import MedulaBrowser
from config.settings import Settings
import time

browser = MedulaBrowser(Settings())
browser.start()

print('🚀 Medula otomatik giriş başlıyor...')
print('🧩 CAPTCHA geldiğinde sen çöz, program bekleyecek!')

# Otomatik giriş yap
try:
    login_success = browser.login()
    
    if login_success:
        print('✅ Giriş başarılı!')
        print('🎯 Sol menüde "Reçete Listesi" linkine manuel tıkla')
        print('📸 Reçete tablosu açılınca screenshot at!')
        
        input('Reçete tablosu screenshot aldıktan sonra ENTER bas...')
    else:
        print('❌ Giriş başarısız')
        
except Exception as e:
    print(f'❌ Hata: {e}')
    print('💡 CAPTCHA çözdün mü? Manuel giriş yapmayı dene.')
    input('ENTER bas devam et...')

browser.quit()
print('🔚 Test tamamlandı!')