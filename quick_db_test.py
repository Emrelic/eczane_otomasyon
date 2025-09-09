#!/usr/bin/env python3
"""
Quick Database Test - Unicode Safe
Windows console uyumlu test
"""

import sys
import os
from pathlib import Path

# Proje root dizinini path'e ekle
sys.path.append(str(Path(__file__).parent))

def quick_db_test():
    """Hızlı unicode-safe database testi"""
    try:
        # Console encoding ayarla
        if sys.platform.startswith('win'):
            os.system('chcp 65001 > nul')
        
        print("[TEST] Veritabani hizli testi baslatiliyor...")
        
        # Database import test
        from database.models import get_db_manager
        print("[OK] Database models imported")
        
        # Database manager test  
        db = get_db_manager()
        print("[OK] Database manager created")
        
        # Quick stats test
        stats = db.get_statistics()
        print(f"[OK] Stats retrieved: {stats['total_prescriptions']} prescriptions")
        
        # Test data insert
        test_patient = db.add_patient(
            tc_no="11111111111",
            name="Test Patient",
            birth_date="1990-01-01",
            phone="05551234567",
            address="Test Address"
        )
        
        if test_patient:
            print("[OK] Test patient added successfully")
        else:
            print("[INFO] Test patient already exists")
            
        print("[SUCCESS] All database tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = quick_db_test()
    if result:
        print("[RESULT] Database is working properly!")
    else:
        print("[RESULT] Database has issues - check logs")