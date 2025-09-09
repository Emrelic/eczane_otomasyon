# -*- coding: utf-8 -*-
"""
Complete Unified System Test
DOSE CONTROLLER + SUT + AI integration test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_prescription_processor import UnifiedPrescriptionProcessor
import json

def test_complete_unified_system():
    """Complete unified system test"""
    
    print("=== COMPLETE UNIFIED SYSTEM TEST ===")
    print("Testing: DOSE CONTROLLER + SUT + AI Integration")
    
    # Test prescription with dose violations
    test_prescription = {
        "recete_no": "UNIFIED_TEST_001",
        "hasta_tc": "12345678901", 
        "hasta_ad": "Test",
        "hasta_soyad": "Patient",
        "hasta_dogum_tarihi": "1980-01-01",
        "drugs": [
            {
                "ilac_adi": "TENOFOVIR ALAFENAMID 25mg TABLET",
                "adet": "90",  # High dose - potential violation
                "rapor_kodu": "R123456",
                "msj": "var",
                "mesaj_kodlari": "1013(1), 1301", 
                "etken_madde": "TENOFOVIR ALAFENAMID FUMARAT",
                "kullanim_sekli": "1x1",
                "gun_sayisi": "30"
            },
            {
                "ilac_adi": "PARACETAMOL 500mg TABLET", 
                "adet": "20",
                "rapor_kodu": "",
                "msj": "yok",
                "kullanim_sekli": "1x1",
                "gun_sayisi": "20"
            }
        ],
        "drug_messages": [
            {"kod": "1013", "aciklama": "Doz asimi uyarisi"},
            {"kod": "1301", "aciklama": "Endikasyon uyarisi"}
        ],
        "report_details": {
            "tani_bilgileri": ["B18.1", "K76.9"],
            "doktor_bransi": "Gastroenteroloji",
            "rapor_tarihi": "2025-09-01"
        }
    }
    
    try:
        print("\n--- INITIALIZING UNIFIED PROCESSOR ---")
        processor = UnifiedPrescriptionProcessor()
        
        print("Processor components:")
        print(f"  Dose Controller: {'ACTIVE' if processor.dose_controller else 'MISSING'}")
        print(f"  SUT Database: {'ACTIVE' if processor.sut_db else 'MISSING'}")
        print(f"  AI Analyzer: {'ACTIVE' if processor.ai_analyzer else 'MISSING'}")
        print(f"  Database: {'ACTIVE' if processor.database else 'MISSING'}")
        
        print(f"\nDose controller mode: {processor.dose_controller.control_mode}")
        
        print("\n--- PROCESSING PRESCRIPTION ---")
        print("Starting unified processing with all systems...")
        
        result = processor.process_single_prescription(test_prescription, "unified_test")
        
        print("\n=== PROCESSING COMPLETED! ===")
        
        # Main results
        print(f"\nPRESCRIPTION: {result.get('prescription_id')}")
        print(f"PATIENT: {result.get('patient_info', {}).get('name')}")
        print(f"FINAL DECISION: {result.get('final_decision')}")
        
        # Processing times
        metadata = result.get('processing_metadata', {})
        print(f"\nPROCESSING TIMES:")
        print(f"  Dose Control: {metadata.get('dose_processing_time', 0):.3f}s")
        print(f"  SUT Analysis: {metadata.get('sut_processing_time', 0):.3f}s") 
        print(f"  AI Analysis: {metadata.get('ai_processing_time', 0):.3f}s")
        print(f"  TOTAL: {metadata.get('processing_time_seconds', 0):.3f}s")
        
        # Detailed analysis results
        print(f"\nANALYSIS BREAKDOWN:")
        
        # Dose Analysis
        dose_analysis = result.get('dose_analysis', {})
        print(f"\nDOSE CONTROL:")
        print(f"  Action: {dose_analysis.get('action')}")
        print(f"  Compliant: {dose_analysis.get('compliant')}")
        print(f"  Drugs analyzed: {dose_analysis.get('drugs_analyzed')}")
        print(f"  Reported drugs: {dose_analysis.get('reported_drugs')}")
        print(f"  Issues found: {dose_analysis.get('issues_found')}")
        
        # SUT Analysis
        sut_analysis = result.get('sut_analysis', {})
        print(f"\nSUT ANALYSIS:")
        print(f"  Action: {sut_analysis.get('action')}")
        print(f"  Compliant: {sut_analysis.get('compliant')}")
        print(f"  Issues count: {sut_analysis.get('issues_count')}")
        print(f"  Warnings count: {sut_analysis.get('warnings_count')}")
        
        # AI Analysis
        ai_analysis = result.get('ai_analysis', {})
        print(f"\nAI ANALYSIS:")
        print(f"  Action: {ai_analysis.get('action')}")
        print(f"  Confidence: {ai_analysis.get('confidence'):.2f}")
        print(f"  Claude used: {ai_analysis.get('claude_used')}")
        print(f"  Method: {ai_analysis.get('method')}")
        
        # Decision details
        details = result.get('details', {})
        print(f"\nDECISION DETAILS:")
        if details.get('dose_reason'):
            print(f"  Dose: {details['dose_reason']}")
        if details.get('sut_reason'):
            print(f"  SUT: {details['sut_reason']}")
        if details.get('ai_reason'):
            print(f"  AI: {details['ai_reason']}")
        
        # Violations and warnings
        if details.get('dose_violations'):
            print(f"\nDOSE VIOLATIONS:")
            for violation in details['dose_violations']:
                print(f"    - {violation}")
        
        if details.get('sut_issues'):
            print(f"\nSUT ISSUES:")
            for issue in details['sut_issues'][:3]:  # Show first 3
                print(f"    - {issue}")
        
        # Database save check
        print(f"\nDATABASE:")
        if result.get('database_saved'):
            print("  Results saved to database")
        else:
            print("  Database save status unknown")
        
        print(f"\nTEST ASSESSMENT:")
        
        # Check if all systems worked
        systems_working = 0
        if dose_analysis.get('action') != 'N/A':
            systems_working += 1
            print("  [OK] Dose Controller: Working")
        else:
            print("  [FAIL] Dose Controller: Failed")
            
        if sut_analysis.get('action') != 'N/A':
            systems_working += 1
            print("  [OK] SUT Analysis: Working")
        else:
            print("  [FAIL] SUT Analysis: Failed")
            
        if ai_analysis.get('action') != 'N/A':
            systems_working += 1  
            print("  [OK] AI Analysis: Working")
        else:
            print("  [FAIL] AI Analysis: Failed")
        
        final_decision = result.get('final_decision')
        if final_decision and final_decision != 'unknown':
            systems_working += 1
            print("  [OK] Decision Logic: Working")
        else:
            print("  [FAIL] Decision Logic: Failed")
        
        print(f"\nSYSTEM SCORE: {systems_working}/4 systems operational")
        
        if systems_working >= 3:
            print("UNIFIED SYSTEM TEST: SUCCESS!")
            return True
        else:
            print("UNIFIED SYSTEM TEST: PARTIAL FAILURE")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_unified_system()
    sys.exit(0 if success else 1)