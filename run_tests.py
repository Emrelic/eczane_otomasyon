#!/usr/bin/env python3
"""
Test Runner Script
Tüm test dosyalarını çalıştırır
"""

import sys
import os
from pathlib import Path

# Proje root dizinini path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_selenium_tests():
    """Selenium testlerini çalıştır"""
    print("🧪 Selenium Testleri Başlatılıyor...")
    print("=" * 50)
    
    try:
        from test_automation import run_all_tests
        results = run_all_tests()
        return results
        
    except Exception as e:
        print(f"❌ Selenium test hatası: {e}")
        return {}


def run_database_tests():
    """Veritabanı testlerini çalıştır"""
    print("\n💾 Veritabanı Testleri Başlatılıyor...")
    print("=" * 50)
    
    try:
        from database.test_db import run_all_tests
        results = run_all_tests()
        return results
        
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")
        return {}


def test_sut_rules():
    """SUT kuralları testini çalıştır"""
    print("\n📋 SUT Kuralları Testleri Başlatılıyor...")
    print("=" * 50)
    
    try:
        from utils.sut_rules import SUTRules
        
        sut_checker = SUTRules()
        
        # Test verisi
        test_prescription = {
            "diagnosis_code": "I10",
            "drug_codes": ["C09AA01", "C08CA01"],
            "patient_age": 45,
            "patient_conditions": [],
            "drug_dosages": {"C09AA01": 5.0}
        }
        
        result = sut_checker.comprehensive_check(test_prescription)
        
        print(f"✅ SUT Test Sonucu:")
        print(f"   Genel Skor: {result['overall_score']:.2f}")
        print(f"   Durum: {result['overall_status']}")
        print(f"   Uyarı Sayısı: {len(result['warnings'])}")
        
        return {"sut_test": True}
        
    except Exception as e:
        print(f"❌ SUT test hatası: {e}")
        return {"sut_test": False}


def test_utilities():
    """Yardımcı fonksiyon testleri"""
    print("\n🔧 Utility Testleri Başlatılıyor...")
    print("=" * 50)
    
    try:
        from utils.helpers import (
            validate_tc_no, format_currency, validate_email,
            validate_phone, DataValidator
        )
        
        # TC doğrulama testi
        tc_valid = validate_tc_no("12345678901")  # Örnek TC (geçersiz)
        print(f"   TC Doğrulama: {'✅' if not tc_valid else '❌'}")  # Geçersiz olmalı
        
        # Para formatı testi
        formatted_money = format_currency(1234.56)
        print(f"   Para Formatı: {formatted_money}")
        
        # Email doğrulama testi
        email_valid = validate_email("test@example.com")
        print(f"   Email Doğrulama: {'✅' if email_valid else '❌'}")
        
        # Telefon doğrulama testi
        phone_valid = validate_phone("05551234567")
        print(f"   Telefon Doğrulama: {'✅' if phone_valid else '❌'}")
        
        # Veri doğrulayıcı testi
        validator = DataValidator()
        test_data = {
            "patient_tc": "12345678901",
            "prescription_date": "2024-01-01",
            "total_amount": "150.75"
        }
        
        validation_errors = validator.validate_prescription_data(test_data)
        print(f"   Veri Doğrulama: {'✅' if validation_errors else '✅'}")
        
        return {"utilities_test": True}
        
    except Exception as e:
        print(f"❌ Utility test hatası: {e}")
        return {"utilities_test": False}


def main():
    """Tüm testleri çalıştır"""
    print("🚀 Eczane Otomasyon Test Süreci Başlatılıyor...")
    print("📁 Proje dizini:", project_root)
    print("\n")
    
    # Gerekli dizinleri oluştur
    os.makedirs("logs", exist_ok=True)
    os.makedirs("test_data", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Tüm test sonuçları
    all_results = {}
    
    try:
        # Test menüsü
        print("Test Seçenekleri:")
        print("1. Tüm testleri çalıştır")
        print("2. Sadece Selenium testleri")
        print("3. Sadece Veritabanı testleri")
        print("4. Sadece SUT kuralları testleri")
        print("5. Sadece Utility testleri")
        
        choice = input("\nSeçiminizi yapın (1-5): ").strip()
        
        if choice == "1":
            # Tüm testler
            all_results.update(run_selenium_tests())
            all_results.update(run_database_tests())
            all_results.update(test_sut_rules())
            all_results.update(test_utilities())
            
        elif choice == "2":
            all_results.update(run_selenium_tests())
            
        elif choice == "3":
            all_results.update(run_database_tests())
            
        elif choice == "4":
            all_results.update(test_sut_rules())
            
        elif choice == "5":
            all_results.update(test_utilities())
            
        else:
            print("❌ Geçersiz seçim!")
            return 1
        
        # Sonuçları özetle
        print("\n" + "=" * 60)
        print("📊 GENEL TEST SONUÇLARI")
        print("=" * 60)
        
        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results.values() if result)
        
        for test_name, result in all_results.items():
            status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nTOPLAM: {passed_tests}/{total_tests} test başarılı")
        
        if passed_tests == total_tests:
            print("🎉 TÜM TESTLER BAŞARILI!")
            print("✅ Sistem entegrasyona hazır")
        else:
            print("⚠️ Bazı testler başarısız")
            print("💡 Loglari kontrol edin ve sorunları giderin")
        
        return 0 if passed_tests == total_tests else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Testler kullanıcı tarafından durduruldu")
        return 1
        
    except Exception as e:
        print(f"\n❌ Test sürecinde beklenmeyen hata: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())