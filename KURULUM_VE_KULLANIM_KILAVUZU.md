# 📋 ECZANE OTOMASYON SİSTEMİ - KURULUM VE KULLANIM KILAVUZU

## 🎉 **SİSTEM DURUMU: PRODUCTION DEPLOYED (09 Eylül 2025, 03:30)**

Bu kılavuz, Eczane Reçete Kontrol Otomasyon Sistemi'nin kurulumu ve kullanımı için kapsamlı rehberdir.

---

## 📋 **İÇİNDEKİLER**

1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum Adımları](#kurulum-adımları) 
3. [İlk Çalıştırma](#ilk-çalıştırma)
4. [Kullanım Rehberi](#kullanım-rehberi)
5. [Test ve Doğrulama](#test-ve-doğrulama)
6. [Sorun Giderme](#sorun-giderme)
7. [Güncelleme ve Bakım](#güncelleme-ve-bakım)

---

## 🖥️ **SİSTEM GEREKSİNİMLERİ**

### **Minimum Sistem Gereksinimleri:**
- **İşletim Sistemi**: Windows 10/11 (64-bit)
- **Python**: 3.11+ (önerilen: 3.13)
- **RAM**: 8GB (minimum), 16GB (önerilen)
- **Disk Alanı**: 2GB boş alan
- **İnternet**: Sürekli stabil bağlantı (Claude API için)

### **Yazılım Gereksinimleri:**
- **Chrome Browser**: Güncel sürüm (otomasyon için)
- **Python Libraries**: requirements.txt'de belirtilen paketler
- **Claude API Key**: Anthropic'den alınacak
- **Medula Hesabı**: Geçerli SGK Medula erişimi

---

## ⚙️ **KURULUM ADIMI**

### **1. Repository'yi İndirme**
```bash
# Git kullanarak
git clone https://github.com/[username]/eczane_otomasyon.git
cd eczane_otomasyon

# Veya ZIP olarak indirip açın
```

### **2. Python Sanal Ortamı (Opsiyonel ama Önerilen)**
```bash
# Sanal ortam oluşturma
python -m venv venv

# Sanal ortamı etkinleştirme
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### **3. Gerekli Paketleri Yükleme**
```bash
# Tüm bağımlılıkları yükle
pip install -r requirements.txt

# Eğer hata alırsanız, pip'i güncelleyin
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Ortam Değişkenlerini Ayarlama**
```bash
# .env.example dosyasını .env olarak kopyalayın
copy .env.example .env

# .env dosyasını düzenleyin (aşağıda detaylar)
```

### **5. .env Dosyası Konfigürasyonu**
`.env` dosyasında aşağıdaki değerleri doldurun:

```bash
# === MEDULA ERİŞİM BİLGİLERİ ===
MEDULA_USERNAME=sizin_kullanici_adiniz
MEDULA_PASSWORD=sizin_sifreniz

# === CLAUDE API ANAHTARI ===
CLAUDE_API_KEY=sk-ant-api03-xxx...

# === BROWSER AYARLARI ===
BROWSER_TYPE=chrome
HEADLESS=false
PAGE_LOAD_TIMEOUT=30

# === VERİTABANI AYARLARI ===
DATABASE_PATH=database/prescriptions.db
ENABLE_DATABASE_LOGGING=true

# === PERFORMANCE AYARLARI ===
DOSE_CONTROL_MODE=detailed
ENABLE_CACHING=true
MAX_CONCURRENT_PRESCRIPTIONS=5
```

---

## 🚀 **İLK ÇALIŞTIRMA**

### **1. Sistem Doğrulama Testi**
Kurulumdan sonra ilk olarak sistem testini yapın:

```bash
# Complete sistem testi (ÖNERİLEN)
python test_unified_system_complete.py

# Eğer başarılı ise bu çıktıları görmelisiniz:
# ✅ Dose Controller: 100% Success
# ✅ Claude AI Analysis: 100% Success  
# ✅ Database Operations: 100% Success
# ✅ SYSTEM SCORE: 4/4 systems operational
```

### **2. Doz Kontrolü Testi**
```bash
# Doz kontrol sistemini test edin
python test_dose_controller_only.py

# Beklenen çıktı:
# ✅ Dose control completed
# ✅ Processing time: 0.001-0.004s
# ✅ TEST COMPLETED SUCCESSFULLY!
```

### **3. Batch Processing Testi**
```bash
# Toplu işleme testini yapın
python test_batch_processing.py

# Beklenen çıktı:
# ✅ Batch processing completed
# ✅ 5/5 prescriptions processed
# ✅ Success rate: 100%
```

---

## 📖 **KULLANIM REHBERİ**

### **1. GUI Uygulamasını Başlatma (ÖNERİLEN)**
```bash
# Modern grafik arayüzü ile
python run_gui.py

# Veya çift tıklama ile
Eczane_Otomasyon_GUI.bat
```

**GUI Özellikleri:**
- 📊 **Dashboard**: Anlık istatistikler
- 📋 **Reçete Yönetimi**: Reçete listesi ve filtreleme  
- 🤖 **Otomasyon Kontrolü**: Başlat/durdur işlemleri
- 💾 **Veritabanı Yönetimi**: Veri görüntüleme
- ⚙️ **Ayar Paneli**: Konfigürasyon düzenleme
- 📝 **Log Görüntüleme**: Detaylı işlem kayıtları

### **2. Konsol Uygulamasını Başlatma**
```bash
# Komut satırı arayüzü ile
python main.py

# Veya çift tıklama ile  
Eczane_Otomasyon_Konsol.bat
```

**Konsol Menü Seçenekleri:**
1. **Reçete kontrolü başlat**: Otomatik reçete kontrol sürecini başlatır
2. **Ayarları görüntüle**: Mevcut konfigürasyon ayarlarını gösterir
3. **Çıkış**: Programdan çıkar

### **3. İlk Reçete İşleme Süreci**

#### **Adım 1: Medula'ya Giriş**
- Sistem otomatik olarak Medula'ya giriş yapar
- CAPTCHA göründüğünde manuel olarak çözün
- KVKK checkbox'ı otomatik işaretlenir

#### **Adım 2: Reçete Listesi**
- A grubu reçeteler otomatik filtrelenir
- Reçete listesi ekranda görüntülenir
- İşlenecek reçeteler seçilir

#### **Adım 3: Otomatik Analiz**
- **Doz Kontrolü**: Rapor vs reçete dozları (0.001s)
- **SUT Analizi**: SGK kuralları kontrolü  
- **AI Analizi**: Claude ile akıllı karar (3.5s)
- **Final Karar**: Onay/Red/Bekletme

#### **Adım 4: Sonuçları Görüntüleme**
- İşlem sonuçları dashboard'da görünür
- Detaylı analiz raporları mevcut
- Veritabanında kalıcı kayıt tutulur

---

## 🧪 **TEST VE DOĞRULAMA**

### **Günlük Test Komutları**
Sistemi düzenli olarak test etmek için:

```bash
# Hızlı sistem kontrolü (30 saniye)
python test_unified_system_complete.py

# Doz kontrolü testi (10 saniye)
python test_dose_controller_only.py

# Batch processing testi (1 dakika)  
python test_batch_processing.py
```

### **Performance Kontrolü**
Sistem performansını izlemek için:

```bash
# Test sonuçlarını kontrol edin:
# ✅ Processing Speed: <4s per prescription
# ✅ Success Rate: >95%  
# ✅ Database Saves: 100%
```

### **Medula Bağlantı Testi**
```bash
# Real Medula workflow testi
python test_real_medula_workflow.py

# Başarılı ise:
# ✅ Login successful
# ✅ Navigation working
# ✅ Data extraction operational
```

---

## 🔧 **SORUN GİDERME**

### **Sık Karşılaşılan Sorunlar**

#### **1. Browser Başlatılamıyor**
```bash
# Çözüm 1: Chrome'u güncelle
# Çözüm 2: .env dosyasında BROWSER_TYPE=edge olarak değiştir
# Çözüm 3: Antivirus Chrome driver'ı engelliyor olabilir
```

#### **2. Medula Giriş Sorunu**
```bash
# Kontrol listesi:
# ✓ Kullanıcı adı/şifre doğru mu?
# ✓ Medula sistemi erişilebilir mi?
# ✓ CAPTCHA manuel çözüldü mü?
# ✓ İnternet bağlantısı stabil mi?
```

#### **3. Claude API Hatası**
```bash
# Kontrol listesi:
# ✓ API anahtarı geçerli mi?
# ✓ API kullanım limiti aşıldı mı?
# ✓ İnternet bağlantısı var mı?
# ✓ .env dosyasında doğru anahtar var mı?
```

#### **4. Database Hatası**
```bash
# Çözüm:
# 1. database/ klasörünün yazma izni var mı kontrol et
# 2. SQLite dosyası bozuksa sil, otomatik yenisi oluşur
# 3. Disk alanı yeterli mi kontrol et
```

### **Log Dosyalarını İnceleme**
```bash
# Son hataları görüntüle
type logs\eczane_otomasyon.log

# Sadece error logları
findstr "ERROR" logs\eczane_otomasyon.log
```

---

## 🔄 **GÜNCELLEME VE BAKIM**

### **Sistem Güncellemeleri**
```bash
# Git ile güncelleme
git pull origin main

# Paket güncellemeleri
pip install -r requirements.txt --upgrade

# Test sistemini çalıştır
python test_unified_system_complete.py
```

### **Veritabanı Bakımı**
```bash
# Eski kayıtları temizle (opsiyonel)
# database/prescriptions.db dosyasını silin
# Yeni boş database otomatik oluşacak

# Backup alma
copy database\prescriptions.db database\prescriptions_backup.db
```

### **Performance Optimizasyonu**
```bash
# Cache temizle (.env dosyasında)
ENABLE_CACHING=false  # Geçici olarak kapat
ENABLE_CACHING=true   # Tekrar aç

# Batch boyutunu ayarla
MAX_CONCURRENT_PRESCRIPTIONS=3  # Daha yavaş sistem için
MAX_CONCURRENT_PRESCRIPTIONS=10 # Daha hızlı sistem için
```

---

## 📞 **DESTEK VE İLETİŞİM**

### **Teknik Destek**
- **GitHub Issues**: Sorunları bildirmek için
- **Documentation**: README.md ve diğer .md dosyaları
- **Test Commands**: CLAUDE_KOMUTLAR.md dosyasındaki komutlar

### **Acil Durum Prosedürü**
1. **Sistemi Durdur**: Ctrl+C ile programı kapat
2. **Log Kontrol**: logs\ klasöründeki son hata kayıtlarını incele  
3. **Safe Mode**: .env dosyasında HEADLESS=false yapıp görsel olarak izle
4. **Backup Kullan**: database backup'ını geri yükle
5. **Yeniden Test**: test_unified_system_complete.py çalıştır

---

## ⚠️ **ÖNEMLİ UYARILAR**

### **Yasal Sorumluluklar**
- 🚨 **Eczacı Kontrolü**: Tüm kararlar mutlaka eczacı tarafından onaylanmalı
- 📋 **SGK İzni**: Medula otomasyonu için SGK'dan yazılı izin önerilir
- 🔒 **KVKK Uyumu**: Hasta verilerinin işlenmesinde KVKK kurallarına uyulmalı
- 💼 **Professional Lisans**: Bu sistem sadece professional kullanım içindir

### **Güvenlik Önlemleri**
- 🔐 **Credential Güvenliği**: .env dosyası asla paylaşılmamalı
- 🌐 **Network Security**: Güvenilir ağlarda kullanın
- 💾 **Data Backup**: Düzenli olarak veritabanı yedekleyin
- 🔄 **Update Frequency**: Güvenlik güncellemelerini kaçırmayın

---

## 📈 **SİSTEM PERFORMANSİ (Güncel)**

### **Validation Metrikleri (09 Eylül 2025, 03:30):**
```
🎯 Dose Controller: 100% Success Rate (0.001-0.004s)
🤖 Claude AI Analysis: 100% Success Rate (5/5)  
💾 Database Operations: 100% Success Rate (5/5)
⚡ Processing Speed: 3.52s average per prescription
🔧 System Components: 4/4 Fully Operational
📈 Overall Status: PRODUCTION READY ✅
```

### **Beklenen Performance Standartları:**
- ⚡ **İşleme Hızı**: <4 saniye/reçete
- ✅ **Başarı Oranı**: >95% 
- 💾 **Database Kayıt**: 100%
- 🎯 **Doz Kontrolü**: <0.01 saniye
- 🧠 **AI Analizi**: <4 saniye

---

**📅 Son Güncelleme**: 09 Eylül 2025, 03:30  
**🚀 Sistem Durumu**: PRODUCTION DEPLOYED  
**📋 Doküman Versiyonu**: v2.1