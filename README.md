# 🏥 Eczane Reçete Kontrol Otomasyonu

**Gerçek eczane iş süreçleri için geliştirilmiş profesyonel otomasyon sistemi**

Bu sistem, eczacıların SGK Medula sisteminde manuel olarak yaptığı reçete kontrol işlemlerini otomatikleştirir. SUT (Sağlık Uygulama Tebliği) kurallarına uygunluk kontrolü yaparak ay sonu SGK faturalandırmasında hata riskini minimize eder.

## 🎯 İş Problemi

**Manuel Süreç:**
1. Eczacı Medula sistemine girer
2. A grubu reçete listesini inceler  
3. Her reçete için rapor detaylarını kontrol eder
4. SUT kurallarına göre uygunluk değerlendirmesi yapar
5. Ay sonunda SGK'ya faturalar
6. SGK SUT uygunsuzluk nedeniyle ödeme yapmayabilir

**Otomatik Çözüm:**
- Program Medula'ya otomatik giriş yapar
- Reçeteleri AI ile SUT kurallarına göre analiz eder  
- Hasta/ilaç geçmişini hafızada tutar
- Karar verir: Uygun/Uygunsuz/Şüpheli

## 🚀 Özellikler

- **Web Automation**: Selenium ile Medula sistemine otomatik giriş
- **AI Karar Verme**: OpenAI API ile reçete analizi ve otomatik karar
- **Güvenlik Kontrolleri**: Yüksek riskli durumlar için ek güvenlik önlemleri
- **Loglama**: Detaylı işlem kayıtları
- **Screenshot**: Hata durumlarında otomatik ekran görüntüsü
- **Modüler Yapı**: Kolay genişletilebilir mimari

## 📁 Proje Yapısı

```
eczane_otomasyon/
├── main.py                    # Ana konsol uygulaması
├── run_gui.py                 # GUI uygulaması başlatıcı
├── run_tests.py               # Test çalıştırıcı
├── test_automation.py         # Selenium testleri
├── requirements.txt           # Python bağımlılıkları
├── .env.example               # Örnek ayar dosyası
├── config/                    # Konfigürasyon
│   ├── __init__.py
│   └── settings.py
├── medula_automation/         # Web automation
│   ├── __init__.py
│   └── browser.py
├── ai_analyzer/              # AI karar verme
│   ├── __init__.py
│   └── decision_engine.py
├── database/                 # Veritabanı işlemleri
│   ├── __init__.py
│   ├── models.py
│   └── test_db.py
├── gui/                      # Grafik arayüz
│   ├── __init__.py
│   └── main_window.py
└── utils/                    # Yardımcı fonksiyonlar
    ├── __init__.py
    ├── helpers.py
    └── sut_rules.py
```

## ⚙️ Kurulum

### 1. Gerekli Python paketlerini yükleyin:

```bash
pip install -r requirements.txt
```

### 2. Ortam değişkenlerini ayarlayın:

`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli bilgileri girin:

```bash
cp .env.example .env
```

`.env` dosyasındaki değerleri düzenleyin:
```
MEDULA_USERNAME=sizin_kullanici_adiniz
MEDULA_PASSWORD=sizin_sifreniz
OPENAI_API_KEY=sizin_openai_api_anahtariniz
```

## 🏃 Kullanım

### 🖥️ Konsol Uygulaması
Komut satırından çalıştırmak için:

```bash
python main.py
```

### 🖼️ Grafik Arayüz (Önerilen)
Modern GUI ile çalıştırmak için:

```bash
python run_gui.py
```

### 🧪 Testleri Çalıştırma
Tüm testleri çalıştırmak için:

```bash
python run_tests.py
```

### Konsol Menü Seçenekleri:

1. **Reçete kontrolü başlat**: Otomatik reçete kontrol sürecini başlatır
2. **Ayarları görüntüle**: Mevcut konfigürasyon ayarlarını gösterir
3. **Çıkış**: Programdan çıkar

### GUI Özellikleri:

- 📊 **Dashboard**: Anlık istatistikler ve son işlemler
- 📋 **Reçete Yönetimi**: Reçete listesi ve filtreleme
- 🤖 **Otomasyon Kontrolü**: Başlat/durdur, test işlemleri
- 💾 **Veritabanı Yönetimi**: Veri görüntüleme ve yönetim
- ⚙️ **Ayar Paneli**: Konfigürasyon düzenleme
- 📝 **Log Görüntüleme**: Detaylı işlem kayıtları

## 🔧 Konfigürasyon

### Browser Ayarları
- `BROWSER_TYPE`: chrome, firefox, edge (varsayılan: chrome)
- `HEADLESS`: Tarayıcıyı görünmez modda çalıştırır (true/false)
- `PAGE_LOAD_TIMEOUT`: Sayfa yüklenme timeout süresi (saniye)

### AI Ayarları
- `OPENAI_MODEL`: Kullanılacak GPT model (varsayılan: gpt-4)
- `OPENAI_TEMPERATURE`: AI yanıt çeşitliliği (0.0-1.0)
- `AUTO_APPROVE_THRESHOLD`: Otomatik onay güven eşiği (0.0-1.0)

### Güvenlik Ayarları
- `ENABLE_SCREENSHOTS`: Hata durumlarında screenshot alma
- `MAX_RETRY_ATTEMPTS`: Maksimum yeniden deneme sayısı

## 🤖 AI Karar Mantığı

AI sistemi **SUT (Sağlık Uygulama Tebliği)** kurallarına göre değerlendirir:

### 📋 Kontrol Kriterleri:
1. **İlaç-Tanı Uyumluluğu**: ICD-10 tanı kodları ile ATC ilaç kodları eşleştirmesi
2. **Yaş Kısıtlamaları**: Pediatrik/geriatrik ilaç uygunluğu
3. **Dozaj Kontrolleri**: Günlük maksimum doz sınırları
4. **İlaç Etkileşimleri**: Major etkileşim uyarıları
5. **Rapor Gereklilikleri**: Raporlu ilaçlar için geçerli rapor kontrolü
6. **Kontrendikasyonlar**: Hasta durumuna göre yasak ilaçlar

### 🎯 Karar Türleri:
- **ONAY (Approve)**: SUT'a tam uyumlu, güvenle faturalanabilir
- **RED (Reject)**: SUT ihlali var, faturalanmamalı  
- **BEKLET (Hold)**: Manuel inceleme gerekli, belirsiz durum

### 🧠 Öğrenme Sistemi:
- Geçmiş kararlardan öğrenme
- Sık kullanılan ilaç-tanı kombinasyonları hafızada tutma
- Eczacı geri bildirimlerini değerlendirme

## 📊 Loglama

Sistem tüm işlemleri detaylı olarak loglar:

- **INFO**: Genel işlem bilgileri
- **SUCCESS**: Başarılı işlemler
- **WARNING**: Uyarı durumları
- **ERROR**: Hata durumları

Log dosyaları `logs/` klasöründe saklanır.

## 🔒 Güvenlik

- Hassas bilgiler `.env` dosyasında saklanır
- Yüksek riskli durumlar için ek kontrol mekanizmaları
- Screenshot ile işlem kanıtları
- Detaylı audit log kayıtları

## ⚠️ Önemli Uyarılar ve Yasal Bilgiler

### 🚨 YASAL SORUMLULUK
1. **Eczacı Sorumluluğu**: Tüm nihai kararlar eczacı tarafından onaylanmalıdır
2. **SGK İzni**: Medula sistemini otomatik kullanım için SGK'dan yazılı izin alınması önerilir
3. **KVKK Uyumluluğu**: Hasta verilerinin işlenmesinde KVKK kurallarına uyulmalıdır
4. **Professional Lisans**: Bu sistem professional kullanım içindir

### 🔧 TEKNİK GEREKLER
1. **İnternet Bağlantısı**: Sürekli stabil internet bağlantısı gerekli
2. **Medula Erişimi**: Geçerli Medula kullanıcı hesabı zorunlu
3. **OpenAI API**: ChatGPT/GPT-4 erişimi için ücretli API anahtarı
4. **Windows**: Windows 10/11 işletim sistemi önerilir

### 💰 MALİYET TAHMİNİ
- **OpenAI API**: ~$20-50/ay (kullanıma göre değişir)
- **Sistem Bakımı**: Periodic güncelleme gereksinimi
- **Donanım**: Minimum 8GB RAM, SSD disk önerilir

## 🐛 Sorun Giderme

### Yaygın Sorunlar:

1. **Browser başlatılamıyor**:
   - Chrome/Firefox/Edge güncel sürümde olduğundan emin olun
   - İnternet bağlantınızı kontrol edin

2. **Medula'ya giriş yapılamıyor**:
   - Kullanıcı adı/şifre doğruluğunu kontrol edin
   - Medula sisteminin erişilebilir olduğunu kontrol edin

3. **AI kararları alınamıyor**:
   - OpenAI API anahtarınızın geçerli olduğunu kontrol edin
   - API kullanım limitinizi kontrol edin

## 🤝 Katkıda Bulunma

Bu proje açık kaynak olarak geliştirilmektedir. Katkılarınız memnuniyetle karşılanır.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**⚠️ UYARI**: Bu sistem yalnızca yardımcı bir araçtır. Tüm reçete kararları mutlaka yetkili bir eczacı tarafından kontrol edilmelidir.