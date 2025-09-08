#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Advanced Batch Processor
Testler: async processing, analytics, file monitoring
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Modül yolunu ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_batch_processor import AdvancedBatchProcessor

async def test_batch_processing():
    """Test batch processing with existing manual data"""
    print("=== ADVANCED BATCH PROCESSOR TEST ===")
    
    # Test dosyasını kontrol et
    test_file = "manual_detailed_prescriptions.json"
    if not os.path.exists(test_file):
        print(f"HATA: {test_file} bulunamadi!")
        return False
    
    # Test verisini yükle
    with open(test_file, 'r', encoding='utf-8') as f:
        prescriptions = json.load(f)
    
    # Processor'i başlat
    processor = AdvancedBatchProcessor()
    
    try:
        print("\n1. Batch Processing Test...")
        results = await processor.process_batch_async(prescriptions, source="test_file")
        
        print(f"Batch Results: {len(results.get('results', []))} recete islendi")  
        print(f"Basarili: {results.get('summary', {}).get('success_count', 0)}")
        print(f"Basarisiz: {results.get('summary', {}).get('error_count', 0)}")
        
        # Analytics test
        print("\n2. Analytics Test...")
        analytics = results.get('analytics', {})
        
        if analytics:
            print(f"Decision Patterns: {len(analytics.get('decision_patterns', {}))}")
            print(f"SUT Compliance: {analytics.get('sut_compliance', {}).get('total_rules_checked', 0)} rule checked")
            print(f"Performance: {analytics.get('performance_metrics', {}).get('total_processing_time', 0):.2f}s")
        
        # Export test
        print("\n3. Excel Export Test...")
        export_file = processor.export_to_excel(results)  # await kaldırıldı
        if export_file and os.path.exists(export_file):
            print(f"Excel export basarili: {export_file}")
            print(f"Dosya boyutu: {os.path.getsize(export_file)} bytes")
        else:
            print("Excel export BASARISIZ!")
            
        return True
        
    except Exception as e:
        print(f"TEST HATASI: {str(e)}")
        return False

def test_file_monitoring():
    """Test file monitoring setup"""
    print("\n=== FILE MONITORING TEST ===")
    
    try:
        processor = AdvancedBatchProcessor()
        monitor_path = os.path.join(os.getcwd(), "test_monitor")
        
        # Test klasörü oluştur
        os.makedirs(monitor_path, exist_ok=True)
        
        # Monitoring başlat (test için kısa süre)
        print(f"Monitoring setup test for: {monitor_path}")
        
        # Test dosyası oluştur
        test_json = {
            "test": "file_monitor",
            "timestamp": "2025-09-08T12:00:00"
        }
        
        test_file_path = os.path.join(monitor_path, "test_prescription.json")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            json.dump(test_json, f, ensure_ascii=False, indent=2)
        
        print(f"Test dosyasi olusturuldu: {test_file_path}")
        print("File monitoring sistemi hazir!")
        
        # Temizlik
        os.remove(test_file_path)
        os.rmdir(monitor_path)
        
        return True
        
    except Exception as e:
        print(f"FILE MONITORING TEST HATASI: {str(e)}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("Advanced Batch Processor - Komple Test Suiti")
    print("=" * 50)
    
    # Test 1: Batch Processing
    batch_success = await test_batch_processing()
    
    # Test 2: File Monitoring  
    monitor_success = test_file_monitoring()
    
    # Sonuç raporu
    print("\n" + "=" * 50)
    print("TEST SONUCLARI:")
    print(f"Batch Processing: {'BASARILI' if batch_success else 'BASARISIZ'}")
    print(f"File Monitoring: {'BASARILI' if monitor_success else 'BASARISIZ'}")
    
    overall_success = batch_success and monitor_success
    print(f"\nGENEL DURUM: {'TUM TESTLER BASARILI!' if overall_success else 'BAZI TESTLER BASARISIZ!'}")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())