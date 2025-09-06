#!/usr/bin/env python3
"""
Veritabanı Test Script
SQLite veritabanı fonksiyonlarını test eder
"""

import os
import sys
from pathlib import Path

# Proje root dizinini path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

from database.models import DatabaseManager, get_db_manager
from datetime import datetime, date
import json


def test_database_creation():
    """Veritabanı oluşturma testi"""
    print("🔧 Veritabanı oluşturma testi...")
    
    try:
        # Test veritabanı oluştur
        db = DatabaseManager("test_data/test_db.db")
        print("✅ Veritabanı başarıyla oluşturuldu")
        return True
    except Exception as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        return False


def test_patient_operations():
    """Hasta işlemleri testi"""
    print("\n👤 Hasta işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        # Yeni hasta ekle
        patient_id = db.add_patient(
            tc_no="12345678901",
            name="Test Hasta",
            birth_date="1990-01-01",
            phone="05551234567",
            address="Test Adres",
            medical_history="Hipertansiyon, diyabet"
        )
        
        if patient_id:
            print("✅ Hasta başarıyla eklendi")
        else:
            print("⚠️ Hasta zaten mevcut")
        
        # Hasta bilgilerini getir
        patient = db.get_patient("12345678901")
        if patient:
            print(f"✅ Hasta bilgileri getirildi: {patient['name']}")
        else:
            print("❌ Hasta bulunamadı")
        
        # Hasta bilgilerini güncelle
        updated = db.update_patient("12345678901", phone="05559876543")
        if updated:
            print("✅ Hasta bilgileri güncellendi")
        
        return True
        
    except Exception as e:
        print(f"❌ Hasta işlemleri hatası: {e}")
        return False


def test_doctor_operations():
    """Doktor işlemleri testi"""
    print("\n👨‍⚕️ Doktor işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        # Yeni doktor ekle
        doctor_id = db.add_doctor(
            diploma_no="DOC123456",
            name="Dr. Test Doktor",
            specialty="Dahiliye",
            hospital="Test Hastanesi",
            phone="02121234567"
        )
        
        if doctor_id:
            print("✅ Doktor başarıyla eklendi")
        else:
            print("⚠️ Doktor zaten mevcut")
        
        # Doktor bilgilerini getir
        doctor = db.get_doctor("DOC123456")
        if doctor:
            print(f"✅ Doktor bilgileri getirildi: {doctor['name']}")
        else:
            print("❌ Doktor bulunamadı")
        
        return True
        
    except Exception as e:
        print(f"❌ Doktor işlemleri hatası: {e}")
        return False


def test_prescription_operations():
    """Reçete işlemleri testi"""
    print("\n📋 Reçete işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        # Yeni reçete ekle
        prescription_id = db.add_prescription(
            prescription_id="RX2024001",
            patient_tc="12345678901",
            doctor_diploma_no="DOC123456",
            hospital="Test Hastanesi",
            prescription_date="2024-01-01",
            diagnosis_code="I10",
            diagnosis_description="Hipertansiyon",
            total_amount=150.75
        )
        
        if prescription_id:
            print("✅ Reçete başarıyla eklendi")
        else:
            print("⚠️ Reçete zaten mevcut")
        
        # Reçete bilgilerini getir
        prescription = db.get_prescription("RX2024001")
        if prescription:
            print(f"✅ Reçete bilgileri getirildi: {prescription['prescription_id']}")
            print(f"   Hasta: {prescription['patient_name']}")
            print(f"   Doktor: {prescription['doctor_name']}")
        else:
            print("❌ Reçete bulunamadı")
        
        # Reçete durumunu güncelle
        updated = db.update_prescription_status("RX2024001", "approved")
        if updated:
            print("✅ Reçete durumu güncellendi")
        
        return True
        
    except Exception as e:
        print(f"❌ Reçete işlemleri hatası: {e}")
        return False


def test_medication_operations():
    """İlaç işlemleri testi"""
    print("\n💊 İlaç işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        # Yeni ilaç ekle
        medication_id = db.add_medication(
            barcode="8699123456789",
            name="Parol 500mg Tablet",
            active_ingredient="Parasetamol",
            dosage="500mg",
            form="Tablet",
            manufacturer="Atabay",
            sut_code="SUT001",
            price=15.50
        )
        
        if medication_id:
            print("✅ İlaç başarıyla eklendi")
        else:
            print("⚠️ İlaç zaten mevcut")
        
        # İlaç bilgilerini getir
        medication = db.get_medication("8699123456789")
        if medication:
            print(f"✅ İlaç bilgileri getirildi: {medication['name']}")
        else:
            print("❌ İlaç bulunamadı")
        
        return True
        
    except Exception as e:
        print(f"❌ İlaç işlemleri hatası: {e}")
        return False


def test_ai_decision_operations():
    """AI karar işlemleri testi"""
    print("\n🤖 AI karar işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        # AI kararı kaydet
        decision_id = db.save_ai_decision(
            prescription_id="RX2024001",
            decision="approve",
            reason="Tüm SUT kurallarına uygun",
            confidence=0.95,
            risk_factors=["Yok"],
            recommendations=["Normal tedavi sürecine devam"],
            ai_model="gpt-4"
        )
        
        if decision_id:
            print("✅ AI kararı başarıyla kaydedildi")
        
        # AI kararını getir
        decision = db.get_ai_decision("RX2024001")
        if decision:
            print(f"✅ AI kararı getirildi: {decision['decision']}")
            print(f"   Güven skoru: {decision['confidence']}")
        else:
            print("❌ AI kararı bulunamadı")
        
        return True
        
    except Exception as e:
        print(f"❌ AI karar işlemleri hatası: {e}")
        return False


def test_statistics():
    """İstatistik işlemleri testi"""
    print("\n📊 İstatistik işlemleri testi...")
    
    db = get_db_manager()
    
    try:
        stats = db.get_statistics()
        
        print("✅ İstatistikler:")
        print(f"   Toplam reçete: {stats['total_prescriptions']}")
        print(f"   Durum dağılımı: {stats['prescriptions_by_status']}")
        print(f"   AI kararlar: {stats['ai_decisions']}")
        print(f"   Ortalama güven: {stats['average_confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ İstatistik işlemleri hatası: {e}")
        return False


def test_system_logging():
    """Sistem loglama testi"""
    print("\n📝 Sistem loglama testi...")
    
    db = get_db_manager()
    
    try:
        # Test log kaydı
        db.log_system_event(
            level="INFO",
            module="test_module",
            message="Test log mesajı",
            data={"test": True, "value": 123}
        )
        
        print("✅ Sistem log kaydı başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Sistem loglama hatası: {e}")
        return False


def cleanup_test_data():
    """Test verilerini temizle"""
    test_db_path = Path("test_data/test_db.db")
    if test_db_path.exists():
        os.remove(test_db_path)
        print("🧹 Test verileri temizlendi")


def run_all_tests():
    """Tüm veritabanı testlerini çalıştır"""
    print("🚀 Veritabanı Test Süreci Başlatılıyor...")
    print("=" * 50)
    
    test_results = {}
    
    # Test dizinini oluştur
    os.makedirs("test_data", exist_ok=True)
    
    # Testleri çalıştır
    tests = [
        ("Database Creation", test_database_creation),
        ("Patient Operations", test_patient_operations),
        ("Doctor Operations", test_doctor_operations),
        ("Prescription Operations", test_prescription_operations),
        ("Medication Operations", test_medication_operations),
        ("AI Decision Operations", test_ai_decision_operations),
        ("Statistics", test_statistics),
        ("System Logging", test_system_logging),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} testi sırasında hata: {e}")
            test_results[test_name] = False
    
    # Sonuçları özetle
    print("\n" + "=" * 50)
    print("📊 VERİTABANI TEST SONUÇLARI:")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name}: {status}")
    
    print(f"\nTOPLAM: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm veritabanı testleri başarılı!")
    else:
        print("⚠️ Bazı testler başarısız.")
    
    # Temizlik
    cleanup_test_data()
    
    return test_results


if __name__ == "__main__":
    run_all_tests()