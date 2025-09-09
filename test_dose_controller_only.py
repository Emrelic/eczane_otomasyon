# -*- coding: utf-8 -*-
"""
Quick Dose Controller Test - JSON data ile
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prescription_dose_controller import PrescriptionDoseController
from unified_prescription_processor import UnifiedPrescriptionProcessor
import json

def test_dose_controller_with_json():
    """JSON data ile dose controller test"""
    
    print("=== DOSE CONTROLLER QUICK TEST ===")
    
    # Test prescription data
    test_prescription = {
        "recete_no": "TEST001",
        "hasta_tc": "12345678901", 
        "hasta_ad": "Test",
        "hasta_soyad": "Patient",
        "drugs": [
            {
                "ilac_adi": "TENOFOVIR ALAFENAMID 25mg",
                "adet": "30",
                "rapor_kodu": "R123456",
                "msj": "var",
                "mesaj_kodlari": "1013(1), 1301",
                "etken_madde": "TENOFOVIR ALAFENAMID FUMARAT"
            },
            {
                "ilac_adi": "PARACETAMOL 500mg", 
                "adet": "20",
                "rapor_kodu": "",
                "msj": "yok"
            }
        ],
        "drug_messages": [
            {"kod": "1013", "aciklama": "Doz asimi uyarisi"},
            {"kod": "1301", "aciklama": "Endikasyon uyarisi"}
        ]
    }
    
    try:
        # 1. Dose controller direkt test
        print("\n--- DOSE CONTROLLER DIRECT TEST ---")
        controller = PrescriptionDoseController(control_mode="detailed")
        controller.setup_cache_tables()
        
        result = controller.control_prescription_doses(test_prescription)
        
        print(f"Prescription ID: {result.prescription_id}")
        print(f"Total drugs: {result.total_drugs}")
        print(f"Reported drugs: {result.reported_drugs}")
        print(f"Processing time: {result.processing_time:.3f}s")
        print(f"Overall decision: {result.overall_decision}")
        
        print("\n--- DRUG DETAILS ---")
        for i, drug in enumerate(result.drug_details, 1):
            print(f"\n{i}. {drug.drug_name}")
            print(f"   Report code: {drug.report_code or 'None'}")
            print(f"   MSJ status: {drug.msj_status}")
            print(f"   Prescription dose: {drug.prescription_dose}")
            if drug.report_code:
                print(f"   Active ingredient: {drug.active_ingredient}")
                print(f"   Report dose: {drug.report_dose}")
                print(f"   Dose compliant: {drug.dose_compliant}")
                print(f"   Details: {drug.dose_check_details}")
        
        print(f"\nAnalysis results: {result.analysis_results}")
        
        # 2. Unified processor test
        print("\n\n--- UNIFIED PROCESSOR WITH DOSE CONTROL ---")
        processor = UnifiedPrescriptionProcessor()
        
        unified_result = processor.process_single_prescription(test_prescription, "json_test")
        
        print(f"Final decision: {unified_result.get('final_decision')}")
        
        # Dose analysis results
        dose_analysis = unified_result.get('dose_analysis', {})
        print(f"\nDOSE ANALYSIS:")
        print(f"  Action: {dose_analysis.get('action')}")
        print(f"  Compliant: {dose_analysis.get('compliant')}")
        print(f"  Drugs analyzed: {dose_analysis.get('drugs_analyzed')}")
        print(f"  Reported drugs: {dose_analysis.get('reported_drugs')}")
        print(f"  Issues found: {dose_analysis.get('issues_found')}")
        
        # Processing times
        metadata = unified_result.get('processing_metadata', {})
        print(f"\nPROCESSING TIMES:")
        print(f"  Dose: {metadata.get('dose_processing_time', 0):.3f}s")
        print(f"  SUT: {metadata.get('sut_processing_time', 0):.3f}s") 
        print(f"  AI: {metadata.get('ai_processing_time', 0):.3f}s")
        print(f"  Total: {metadata.get('processing_time_seconds', 0):.3f}s")
        
        print("\n=== TEST COMPLETED SUCCESSFULLY! ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dose_controller_with_json()
    sys.exit(0 if success else 1)