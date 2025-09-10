# 🎯 OVERLAY ÇERÇEVE SİSTEM MİMARİSİ

## 📅 TARİH: 10 Eylül 2025
## 👥 STAKEHOLDERS: Emre (Domain Expert) + Claude Code

---

## 🏗️ GENEL MİMARİ KONSEPT:

Medula sayfasının üstüne bir çerçeve giydirilerek hibrit sistem oluşturulacak:
- **Medula**: İçeride normal şekilde çalışır
- **Çerçeve**: Üstte kontrol butonları ve renk kodlu bayraklar
- **Core Engine**: Mevcut unified_processor.py kullanılır (%70 yeniden kullanım)

---

## 📋 6 ANA BÖLÜM ARKİTEKTÜRÜ:

### 1️⃣ **DIŞ KAPI - GİRİŞ EKRANI** ⚠️ *EN SON GELİŞTİRİLECEK*
```
┌─────── PROGRAM GİRİŞ EKRANI ────────┐
│  🏥 ECZANE OTOMASYON SİSTEMİ        │
│                                     │
│  Kullanıcı Adı: [_____________]     │
│  Şifre:        [_____________]      │
│                                     │
│  [Giriş Yap] [Yeni Üyelik]         │
│  [Kullanım Sözleşmesi]              │
│  [Mail Onay] [Şifremi Unuttum]     │
└─────────────────────────────────────┘
```

**Özellikler:**
- Kullanıcı adı/şifre kontrolü
- Yeni üyelik sistemi
- Kullanım sözleşmesi onayı
- Mail onay mekanizması
- Şifre sıfırlama

### 2️⃣ **İÇ KAPI - ANA AYARLAR SAYFASI** 🎯 *İLK GELİŞTİRİLECEK*
```
┌────── ANA KONTROL PANELİ ───────┐
│  ⚙️ İLK AYARLAR                │
│  Medula Kullanıcı: [_______]   │
│  Medula Şifre:     [_______]   │
│  Claude API Key:   [_______]   │
│  [Ayarları Kaydet]             │
│                                │
│  🚀 [MEDULAYA GİRİŞ YAP]       │
└────────────────────────────────┘
```

**Özellikler:**
- Medula credential ayarları
- API key konfigürasyonu
- Medula'ya geçiş butonu
- İki navigasyon modu: Manuel + Otomatik

### 3️⃣ **TEK REÇETE KONTROL** 🔬 *MİKRO İŞLEM*
```
┌─── REÇETE DETAY SAYFASI ────────────────────┐
│  🔴 [BU REÇETEYİ KONTROL ET]                │
│ ┌─── MEDULA REÇETE EKRANI ────────────────┐ │
│ │  Reçete No: 3GP25RF                    │ │
│ │  Hasta: YALÇIN DURDAĞI                 │ │
│ │  İlaçlar: PANTO 40 MG...               │ │
│ │                                        │ │
│ └────────────────────────────────────────┘ │
│  🟢 UYGUN | 🔴 UYGUN DEĞİL | 🟡 ŞÜPHELİ    │
│  🟠 EK KONTROL | 🔵 KONTROLSİZ              │
└─────────────────────────────────────────────┘
```

**Bayrak Sistemi:**
- 🟢 **Yeşil**: UYGUN (SUT'a uygun)
- 🔴 **Kırmızı**: UYGUN DEĞİL (SUT ihlali)
- 🟡 **Sarı**: ŞÜPHELİ (Manuel inceleme gerekli)
- 🟠 **Turuncu**: EK KONTROL (Ek doküman gerekli)
- 🔵 **Açık Mavi**: KONTROLSİZ (Henüz işlenmemiş)

### 4️⃣ **GÜNLÜK TOPLU KONTROL** 📅 *GÜNLÜK İŞLEM*
```
┌─── GÜNLÜK REÇETE LİSTESİ ───────────────────┐
│  🎯 [TÜM GÜNLÜKLERİ KONTROL ET]            │
│                                             │
│ ┌─── MEDULA GÜNLÜK LİSTE ─────────────────┐ │
│ │  □ Reçete 1  [🔵]                       │ │
│ │  □ Reçete 2  [🔵]                       │ │
│ │  □ Reçete 3  [🔵]                       │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│  Grup Seçiliyse: [SADECE X GRUBUNU İNCELE] │
└─────────────────────────────────────────────┘
```

**Kontrol Sırası:**
1. **C Grubu** (Sıralı dağıtım)
2. **A Grubu** (Raporlu ilaçlar) 
3. **Geçici Koruma** (Mülteci)
4. **B Grubu** (Normal)
5. **C Grubu - Kan Ürünü**

### 5️⃣ **AYLIK TOPLU KONTROL** 📊 *AYLIK İŞLEM*
```
┌─── AYLIK REÇETE LİSTESİ ────────────────────┐
│  🎯 [TÜM AYLIGI KONTROL ET]                │
│                                             │
│ ┌─── MEDULA AYLIK LİSTE ──────────────────┐ │
│ │  Sayfa: [<] 1/25 [>]                   │ │
│ │  □ Reçete 1  [🔵] □ Reçete 2  [🔵]     │ │
│ │  □ Reçete 3  [🔵] □ Reçete 4  [🔵]     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│  [SADECE X GRUBUNU İNCELE] (varsa)         │
└─────────────────────────────────────────────┘
```

**Özellikler:**
- Aynen günlük algoritma, daha geniş kapsamlı
- Sayfalama desteği
- Grup bazlı filtreleme

### 6️⃣ **REÇETE SORGU KONTROL** 🔍 *SORGU İŞLEMİ*
```
┌─── REÇETE SORGU EKRANI ─────────────────────┐
│ ┌─── MEDULA SORGU ─────────────────────────┐ │
│ │  TC/Reçete No: [___________] [SORGULA] │ │
│ │                                        │ │
│ │  ┌─ SONUÇLAR ─────────────────────────┐ │ │
│ │  │ Reçete 1: 3GP25RF [🔵]            │ │ │
│ │  │ Reçete 2: 4HT36QW [🔵]            │ │ │
│ │  └─────────────────────────────────────┘ │ │
│ └────────────────────────────────────────┘ │
│                                             │
│  🎯 [REÇETELERİ KONTROL ET]                │
└─────────────────────────────────────────────┘
```

**Özellikler:**
- TC kimlik veya reçete no ile arama
- Sonuçları listeler
- Toplu kontrol butonu

---

## 🔧 TEKNİK İMPLEMENTASYON PLANI:

### **PHASE 1: CORE OVERLAY FRAMEWORK**
```python
# 1. Embedded browser (WebView2/CEF)
# 2. Overlay window (tkinter/PyQt)  
# 3. Button injection system
# 4. Status flag system
```

### **PHASE 2: NAVIGATION AUTOMATION**
```python
# 1. Auto-pilot navigation
# 2. Page detection
# 3. Element interaction
# 4. Session management
```

### **PHASE 3: CONTROL ALGORITHMS**
```python
# 1. Single prescription analysis
# 2. Batch processing
# 3. Progress tracking
# 4. Result storage
```

---

## 🎨 RENK KODLU BAYRAK SİSTEMİ:

### **Status Colors:**
- **🟢 #28a745** - UYGUN (SUT Compliant)
- **🔴 #dc3545** - UYGUN DEĞİL (SUT Violation)
- **🟡 #ffc107** - ŞÜPHELİ (Requires Review)
- **🟠 #fd7e14** - EK KONTROL (Additional Documentation)
- **🔵 #17a2b8** - KONTROLSİZ (Not Processed)

### **Visual Implementation:**
```python
status_colors = {
    'uygun': '#28a745',
    'uygun_degil': '#dc3545', 
    'supheli': '#ffc107',
    'ek_kontrol': '#fd7e14',
    'kontrolsuz': '#17a2b8'
}
```

---

## 🔄 WORKFLOW AKIŞI:

1. **Program Başlatma** → İç Kapı (Ayarlar)
2. **Medula Giriş** → Embedded Browser
3. **Page Detection** → Uygun butonları inject et
4. **User Action** → Kontrol algoritması çalıştır
5. **Analysis** → Core engine (unified_processor)
6. **Result** → Bayrak güncelle + Database kaydet

---

## 📊 MEVCUT SİSTEM ENTEGRASYONU:

### **%70 Yeniden Kullanım:**
- `unified_prescription_processor.py` → Core engine
- `prescription_dose_controller.py` → Dose analysis
- `database/` → Data persistence
- `ai_analyzer/` → Claude API integration

### **%30 Yeni Geliştirme:**
- Overlay GUI framework
- Embedded browser integration
- Button injection system
- Flag visualization system

---

**📅 Created:** 10 Eylül 2025  
**🎯 Priority:** İç Kapı → Overlay Framework → Control Algorithms  
**🚀 Goal:** Hibrit manuel+otomatik sistem