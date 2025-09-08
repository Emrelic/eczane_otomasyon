# 🗺️ MEDULA NAVIGATION MAP - COMPLETE GUIDE

## 📊 OVERVIEW: 13 EKRAN + ALT BUTONLAR

---

## 1️⃣ MEDULA ANA SAYFA
**Path:** Login sonrası ilk sayfa  
**Type:** Main Menu

### Navigation Options:
- **a) Reçete Listesi** → Reçete Listesi Sorgulama ekranını açar (aylık)
- **b) Reçete Listesi (Günlük)** → Günlük bazda çalışır
- **c) Reçete Sorgu** → TC ile o hastanın sonlandırılmamış reçetelerini getirir

---

## 2️⃣ REÇETE LİSTESİ SORGULAMA
**Path:** Ana Sayfa → Reçete Listesi  
**Type:** Filter/Search Page

### Interactive Elements:
- **a) Fatura türü Dropdown** → Fatura tipini seç
- **b) Dönem Dropdown** → Tarih aralığı seç  
- **c) Sorgula Butonu** → Reçete Listesi tablosunu açar

---

## 3️⃣ REÇETE LİSTESİ TABLOSU
**Path:** Reçete Listesi Sorgulama → Sorgula  
**Type:** Data Table (Same page, bottom section)

### Interactive Elements:
- **a) İleri Butonu** → Sonraki sayfa
- **b) Geri Butonu** → Önceki sayfa
- **c) Sayfaya Git Butonu** → Specific page
- **d) Tıklanabilir Reçete Satırları** → Reçete sayfasını açar

---

## 4️⃣ REÇETE DETAY SAYFASI
**Path:** Reçete Listesi → Reçete Satırı Tık  
**Type:** Main Prescription Page

### Critical Navigation Buttons:
- **a) İlaç Butonu** → Kullanılan İlaç Listesi (5)
- **b) Rapor Butonu (Üst)** → Rapor Listesi Ekranı (6)  
- **c) End.Dışı (Yeni) Butonu** → Endikasyon Dışı İzin Sorgulama (7)
- **d) İlaç Bilgi Butonu** → İlaç Bilgi Ekranı (8)
- **e) Rapor Butonu (Orta)** → Rapor Görme Ekranı (9)
- **f) Ted.Şema Butonu** → Tedavi Şeması Pencereciği (10)
- **g) Uyarı Kodu (Yeni) Butonu** → Uyarı Kodları Pencereciği (11)
- **h) İlaç Seçme Kutucukları** → İşlem için ilaç seçimi
- **i) E-Reçete Görüntüle Butonu** → E-Reçete Ekranı (12)

---

## 5️⃣ KULLANILAN İLAÇ LİSTESİ EKRANI
**Path:** Reçete → İlaç Butonu  
**Type:** Drug List Page

### Interactive Elements:
- **a) Göz İlaçları Butonu** → Göz ilaçları filter

---

## 6️⃣ RAPOR LİSTESİ EKRANI
**Path:** Reçete → Rapor Butonu (Üst)  
**Type:** Report List Page

### Interactive Elements:
- **a) Bitmiş Raporları da Göster Butonu** → Include expired reports

---

## 7️⃣ ENDİKASYON DIŞI İZİN SORGULAMA EKRANI
**Path:** Reçete → End.Dışı (Yeni) Butonu  
**Type:** Special Permission Page

### Interactive Elements:
- **a) Güncelle Butonu** → Update permissions

---

## 8️⃣ İLAÇ BİLGİ EKRANI
**Path:** Reçete → İlaç Bilgi Butonu  
**Type:** Drug Information Page

### Interactive Elements:
- **a) İlaç Mesaj Satırları** → Tıklanabilir message rows

---

## 9️⃣ RAPOR GÖRME EKRANI
**Path:** Reçete → Rapor Butonu (Orta)  
**Type:** Report View Page

### Features:
- **Detailed report display**
- **ICD codes visible**
- **Doctor information**

---

## 🔟 TEDAVİ ŞEMASI İŞLEMLERİ PENCERECİĞİ
**Path:** Reçete → Ted.Şema Butonu  
**Type:** Modal/Popup

### Interactive Elements:
- **a) Tamam Butonu** → Confirm and close

---

## 1️⃣1️⃣ REÇETE UYARI KODLARI PENCERECİĞİ
**Path:** Reçete → Uyarı Kodu (Yeni) Butonu  
**Type:** Modal/Popup

### Features:
- **Warning code entry**
- **Validation system**

---

## 1️⃣2️⃣ E-REÇETE EKRANI
**Path:** Reçete → E-Reçete Görüntüle Butonu  
**Type:** E-Prescription Viewer

### Features:
- **Digital prescription view**
- **Full prescription data**

---

## 1️⃣3️⃣ İLAÇ MESAJI EKRANI
**Path:** İlaç Bilgi → İlaç Mesaj Satırı Tık  
**Type:** Drug Message Details

### Features:
- **SUT message codes**
- **Detailed explanations**

---

## 🔄 NAVIGATION FLOW SUMMARY:

```
Ana Sayfa (1)
├── Reçete Listesi Sorgulama (2)
│   └── Reçete Listesi Tablosu (3)
│       └── Reçete Detay (4)
│           ├── Kullanılan İlaç Listesi (5)
│           │   └── Göz İlaçları
│           ├── Rapor Listesi (6)
│           │   └── Bitmiş Raporlar
│           ├── Endikasyon Dışı İzin (7)
│           ├── İlaç Bilgi (8)
│           │   └── İlaç Mesajı (13)
│           ├── Rapor Görme (9)
│           ├── Tedavi Şeması (10)
│           ├── Uyarı Kodları (11)
│           └── E-Reçete (12)
├── Reçete Listesi (Günlük)
└── Reçete Sorgu
```

---

## 🎯 SYSTEM REQUIREMENTS:

### 1. **NAVIGATION CAPABILITY:**
- **13 farklı ekran** arasında gezinebilmeli
- **Modal/Popup** handling yapabilmeli  
- **Back button** logic implement etmeli
- **Session stability** sağlamalı

### 2. **DATA EXTRACTION:**
- **Her ekrandan** relevant data çekmeli
- **Table parsing** (Reçete Listesi)
- **Form data reading** (Dropdowns, inputs)
- **Text extraction** (Reports, messages)

### 3. **INTERACTION CAPABILITY:**
- **Button clicking** (Submit, Navigate)
- **Dropdown selection** (Fatura türü, Dönem)  
- **Checkbox handling** (İlaç seçimi)
- **Table row clicking** (Reçete seçimi)

---

**📅 Created:** 08 Eylül 2025, 16:00  
**🎯 Purpose:** Complete navigation testing framework  
**📊 Scope:** 13 screens + sub-elements comprehensive mapping