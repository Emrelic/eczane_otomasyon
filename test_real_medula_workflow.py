# -*- coding: utf-8 -*-
"""
Real Medula Workflow Test
Complete test with real Medula data extraction + full processing pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_prescription_processor import UnifiedPrescriptionProcessor
from loguru import logger
import json
from datetime import datetime

def test_real_medula_complete_workflow():
    """Complete workflow test with real Medula data"""
    
    print("=== REAL MEDULA WORKFLOW TEST ===")
    print("Complete pipeline: Medula Login -> Data Extraction -> Processing -> Decision")
    
    try:
        print("\n--- PHASE 1: INITIALIZING PROCESSOR ---")
        processor = UnifiedPrescriptionProcessor()
        
        print("System components status:")
        print(f"  Dose Controller: {'ACTIVE' if processor.dose_controller else 'MISSING'}")
        print(f"  SUT Database: {'ACTIVE' if processor.sut_db else 'MISSING'}")
        print(f"  AI Analyzer: {'ACTIVE' if processor.ai_analyzer else 'MISSING'}")
        print(f"  Database: {'ACTIVE' if processor.database else 'MISSING'}")
        
        # Set dose controller to detailed mode for real Medula
        if processor.dose_controller:
            processor.dose_controller.control_mode = "detailed"
            print(f"  Dose mode: {processor.dose_controller.control_mode}")
        
        print("\n--- PHASE 2: MEDULA CONNECTION ---")
        print("Starting Medula live extraction...")
        print("This will:")
        print("  1. Open browser and login to Medula")
        print("  2. Navigate to prescription list") 
        print("  3. Extract 2 prescriptions from Group A")
        print("  4. Apply full analysis pipeline")
        
        print("\nNote: Manual CAPTCHA solving will be required...")
        
        start_time = datetime.now()
        
        # Process from Medula Live (this includes browser login)
        results = processor.process_from_medula_live(limit=2, group='A')
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"\n=== WORKFLOW COMPLETED IN {total_time:.1f} SECONDS ===")
        
        if not results:
            print("No results returned - check Medula connection or data availability")
            return False
        
        print(f"\nExtracted and processed {len(results)} prescriptions")
        
        # Analyze results
        print(f"\n--- PHASE 3: RESULTS ANALYSIS ---")
        
        for i, result in enumerate(results, 1):
            print(f"\n=== PRESCRIPTION {i} ===")
            print(f"ID: {result.get('prescription_id', 'N/A')}")
            print(f"Patient: {result.get('patient_info', {}).get('name', 'N/A')}")
            print(f"FINAL DECISION: {result.get('final_decision', 'N/A')}")
            
            # Processing times
            metadata = result.get('processing_metadata', {})
            print(f"\nPROCESSING TIMES:")
            print(f"  Dose Control: {metadata.get('dose_processing_time', 0):.3f}s")
            print(f"  SUT Analysis: {metadata.get('sut_processing_time', 0):.3f}s")
            print(f"  AI Analysis: {metadata.get('ai_processing_time', 0):.3f}s")
            print(f"  Total: {metadata.get('processing_time_seconds', 0):.3f}s")
            
            # Dose control results  
            dose_analysis = result.get('dose_analysis', {})
            print(f"\nDOSE CONTROL:")
            print(f"  Action: {dose_analysis.get('action', 'N/A')}")
            print(f"  Drugs analyzed: {dose_analysis.get('drugs_analyzed', 0)}")
            print(f"  Reported drugs: {dose_analysis.get('reported_drugs', 0)}")
            print(f"  Issues found: {dose_analysis.get('issues_found', 0)}")
            
            # SUT analysis results
            sut_analysis = result.get('sut_analysis', {})
            print(f"\nSUT ANALYSIS:")
            print(f"  Action: {sut_analysis.get('action', 'N/A')}")
            print(f"  Compliant: {sut_analysis.get('compliant', False)}")
            print(f"  Issues: {sut_analysis.get('issues_count', 0)}")
            
            # AI analysis results
            ai_analysis = result.get('ai_analysis', {})
            print(f"\nAI ANALYSIS:")
            print(f"  Action: {ai_analysis.get('action', 'N/A')}")
            print(f"  Confidence: {ai_analysis.get('confidence', 0):.2f}")
            print(f"  Claude used: {ai_analysis.get('claude_used', False)}")
            
            # Show any issues/warnings
            details = result.get('details', {})
            if details.get('dose_violations'):
                print(f"\nDOSE VIOLATIONS:")
                for violation in details['dose_violations']:
                    print(f"  - {violation}")
            
            if details.get('sut_issues'):
                print(f"\nSUT ISSUES:")
                for issue in details['sut_issues'][:2]:  # Show first 2
                    print(f"  - {issue}")
            
            # Source information
            source_data = result.get('raw_data', {}).get('prescription_data', {})
            extraction_method = source_data.get('extraction_method', 'unknown')
            print(f"\nDATA SOURCE: {extraction_method}")
        
        # Overall assessment
        print(f"\n--- PHASE 4: WORKFLOW ASSESSMENT ---")
        
        approve_count = len([r for r in results if r.get('final_decision') == 'approve'])
        hold_count = len([r for r in results if r.get('final_decision') == 'hold'])
        reject_count = len([r for r in results if r.get('final_decision') == 'reject'])
        
        print(f"\nDECISION DISTRIBUTION:")
        print(f"  Approved: {approve_count}")
        print(f"  Hold: {hold_count}")
        print(f"  Rejected: {reject_count}")
        
        # Check if all systems worked on real data
        systems_working = 0
        all_dose_working = all(r.get('dose_analysis', {}).get('action') != 'N/A' for r in results)
        all_sut_working = all(r.get('sut_analysis', {}).get('action') != 'N/A' for r in results)
        all_ai_working = all(r.get('ai_analysis', {}).get('action') != 'N/A' for r in results)
        all_decisions_valid = all(r.get('final_decision') in ['approve', 'hold', 'reject'] for r in results)
        
        if all_dose_working:
            systems_working += 1
            print("  [OK] Dose Controller: Working on real data")
        else:
            print("  [FAIL] Dose Controller: Issues with real data")
            
        if all_sut_working:
            systems_working += 1
            print("  [OK] SUT Analysis: Working on real data")
        else:
            print("  [FAIL] SUT Analysis: Issues with real data")
            
        if all_ai_working:
            systems_working += 1
            print("  [OK] AI Analysis: Working on real data")
        else:
            print("  [FAIL] AI Analysis: Issues with real data")
            
        if all_decisions_valid:
            systems_working += 1
            print("  [OK] Decision Logic: Valid decisions")
        else:
            print("  [FAIL] Decision Logic: Invalid decisions")
        
        avg_processing_time = sum(r.get('processing_metadata', {}).get('processing_time_seconds', 0) for r in results) / len(results)
        print(f"\nPERFORMANCE:")
        print(f"  Average processing time: {avg_processing_time:.2f}s per prescription")
        print(f"  Total workflow time: {total_time:.1f}s (including Medula navigation)")
        
        print(f"\nREAL MEDULA WORKFLOW SCORE: {systems_working}/4 systems working")
        
        # Save results for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"real_medula_workflow_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\nResults saved to: {results_file}")
        
        if systems_working >= 3 and len(results) > 0:
            print("\nREAL MEDULA WORKFLOW TEST: SUCCESS!")
            return True
        else:
            print("\nREAL MEDULA WORKFLOW TEST: PARTIAL SUCCESS")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up browser
        try:
            if processor and hasattr(processor, 'browser') and processor.browser:
                processor._cleanup_browser()
                print("\nBrowser cleaned up")
        except:
            pass

if __name__ == "__main__":
    print("WARNING: This test requires manual CAPTCHA solving and Medula login.")
    print("Make sure you have valid Medula credentials ready.")
    print("\nStarting real Medula workflow test automatically...")
    
    success = test_real_medula_complete_workflow()
    sys.exit(0 if success else 1)