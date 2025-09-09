# -*- coding: utf-8 -*-
"""
Test Real Medula Data Extraction with Dose Controller
Unicode-safe testing including dose control validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_prescription_processor import UnifiedPrescriptionProcessor
from loguru import logger

def test_dose_controller_with_real_medula():
    """Test dose controller with real Medula data"""
    
    print("=== DOSE CONTROLLER TEST WITH REAL MEDULA ===")
    print("Starting unified prescription processor...")
    
    try:
        # Initialize processor
        processor = UnifiedPrescriptionProcessor()
        
        print("Processor initialized successfully!")
        print("Dose controller:", "ACTIVE" if processor.dose_controller else "NOT FOUND")
        
        # Test process - this will use Medula Live mode
        print("\nStarting Medula Live processing...")
        
        results = processor.process_from_medula_live(limit=2, group='A')
        
        if results:
            print(f"\nProcessing completed! Found {len(results)} results")
            
            # Show dose control results for each prescription
            for i, res in enumerate(results, 1):
                print(f"\n--- PRESCRIPTION {i} ---")
                print(f"ID: {res.get('prescription_id', 'N/A')}")
                print(f"Patient: {res.get('patient_info', {}).get('name', 'N/A')}")
                
                # Dose analysis results
                dose_analysis = res.get("dose_analysis", {})
                print(f"\nDOSE CONTROL:")
                print(f"  Action: {dose_analysis.get('action', 'N/A')}")
                print(f"  Compliant: {dose_analysis.get('compliant', False)}")
                print(f"  Drugs Analyzed: {dose_analysis.get('drugs_analyzed', 0)}")
                print(f"  Reported Drugs: {dose_analysis.get('reported_drugs', 0)}")
                print(f"  Issues Found: {dose_analysis.get('issues_found', 0)}")
                
                # Final decision
                print(f"\nFINAL DECISION: {res.get('final_decision', 'N/A')}")
                
                # Processing times
                metadata = res.get("processing_metadata", {})
                print(f"Dose processing time: {metadata.get('dose_processing_time', 0):.3f}s")
                
                # Details if there are issues
                details = res.get("details", {})
                if details.get("dose_violations"):
                    print(f"\nDOSE VIOLATIONS:")
                    for violation in details["dose_violations"]:
                        print(f"  - {violation}")
                
                if details.get("dose_reason"):
                    print(f"Dose reason: {details['dose_reason']}")
        
        else:
            print("No results returned from processing")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"ERROR: {e}")
        return False
    
    print("\n=== TEST COMPLETED ===")
    return True

def test_real_extraction():
    """Legacy test function - kept for compatibility"""
    print("[BASLAT] Testing Real Medula Data Extraction")
    
    processor = UnifiedPrescriptionProcessor()
    
    try:
        print("[TEST] Running real Medula extraction with 2 prescriptions...")
        results = processor.process_from_medula_live(limit=2, group='A')
        
        print(f"[SONUC] Successfully processed {len(results)} prescriptions")
        
        for i, result in enumerate(results, 1):
            prescription_id = result.get("prescription_id", "N/A")
            decision = result.get("final_decision", "unknown")
            extraction_method = result.get("raw_data", {}).get("prescription_data", {}).get("extraction_method", "unknown")
            
            print(f"[{i}] {prescription_id} -> {decision.upper()} ({extraction_method})")
            
            # Processing metadata
            metadata = result.get("processing_metadata", {})
            print(f"    Processing time: {metadata.get('processing_time_seconds', 0):.2f}s")
            print(f"    SUT: {result.get('sut_analysis', {}).get('action', 'N/A')}")
            print(f"    AI: {result.get('ai_analysis', {}).get('action', 'N/A')}")
            
            # NEW: Show dose control results
            dose_analysis = result.get("dose_analysis", {})
            if dose_analysis:
                print(f"    DOSE: {dose_analysis.get('action', 'N/A')} ({dose_analysis.get('drugs_analyzed', 0)} drugs)")
        
        print("[BASARILI] Real Medula extraction test completed!")
        return True
        
    except Exception as e:
        print(f"[HATA] Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run the new dose controller test
    success = test_dose_controller_with_real_medula()
    sys.exit(0 if success else 1)