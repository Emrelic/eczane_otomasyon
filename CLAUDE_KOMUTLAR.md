# 🤖 CLAUDE İÇİN HIZLI KOMUTLAR REHBERİ

## 🎉 **PRODUCTION READY TEST COMMANDS (09 Eylül 2025, 03:30):**

### 🚀 **Complete Integration Tests (VALIDATED):**
```bash
# Dose Controller Test (100% Success - 0.001-0.004s)
python test_dose_controller_only.py

# Complete Unified System Test (4/4 Systems Operational - 3.52s avg)  
python test_unified_system_complete.py

# Real Medula Workflow Test (Login + Extraction Successful)
python test_real_medula_workflow.py

# Batch Processing Test (5 Prescriptions, 100% Success)
python test_batch_processing.py

# Navigation Integration Test (13 Screens Mapped)
python test_navigation_integration.py
```

### 🎯 **Quick Production Validation:**
```bash
# Run complete system validation (RECOMMENDED)
python test_unified_system_complete.py

# Quick dose control check
python test_dose_controller_only.py

# Full batch processing test
python test_batch_processing.py
```

## 📋 ESKİ TEST KOMUTLARI - İKİ SEÇENEK

### 1️⃣ **Program Test Sistemi**
**KOMUT SATIRI:**
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
python run_tests.py
```
**ÇİFT TIKLAMA:** `Test_Sistemi.bat` dosyasını çift tıkla

---

### 2️⃣ **Browser Testi (Selenium)**
**KOMUT SATIRI:**
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
python test_automation.py
```
**ÇİFT TIKLAMA:** Henüz .bat dosyası yok, komut satırından çalıştır

---

### 3️⃣ **GUI Programı Açma**
**KOMUT SATIRI:**
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
python run_gui.py
```
**ÇİFT TIKLAMA:** `Eczane_Otomasyon_GUI.bat` dosyasını çift tıkla

---

### 4️⃣ **Konsol Programı Açma**
**KOMUT SATIRI:**
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
python main.py
```
**ÇİFT TIKLAMA:** `Eczane_Otomasyon_Konsol.bat` dosyasını çift tıkla

---

## 📁 DOSYA İŞLEMLERİ

### `.env` Dosyası Oluşturma
**KOMUT SATIRI:**
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
copy .env.example .env
notepad .env
```
**ÇİFT TIKLAMA:** 
1. `.env.example` dosyasına sağ tıkla → Kopyala
2. Boş alana sağ tıkla → Yapıştır
3. Kopyalanan dosyayı `.env` olarak yeniden adlandır
4. `.env` dosyasını çift tıklayarak düzenle

---

## 🔧 YARDIMCI KOMUTLAR

### Python Paketlerini Yükleme
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
pip install -r requirements.txt
```

### Logları Görüntüleme
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
type logs\eczane_otomasyon.log
```

### Proje Dosyalarını Listeleme
```bash
cd C:\Users\emrem\AndroidStudioProjects\eczane_otomasyon
dir
```

---

## 🚀 HIZLI BAŞLATMA - HANGİSİNİ KULLAN?

| İhtiyaç | Komut Satırı | Çift Tıklama |
|---------|-------------|---------------|
| **Test yapmak** | `python run_tests.py` | `Test_Sistemi.bat` |
| **GUI açmak** | `python run_gui.py` | `Eczane_Otomasyon_GUI.bat` |
| **Konsol açmak** | `python main.py` | `Eczane_Otomasyon_Konsol.bat` |
| **Browser test** | `python test_automation.py` | Sadece komut satırı |

---

## 📝 NOTLAR
- Komut satırı = öğrenme için ideal ✅
- Çift tıklama = hız için ideal ✅
- Her ikisi de aynı sonucu verir
- Hata durumunda komut satırı daha detaylı bilgi verir

**SON GÜNCELLEME: 2025-09-09 03:30 - PRODUCTION DEPLOYED**