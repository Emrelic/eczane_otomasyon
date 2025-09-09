# -*- coding: utf-8 -*-
"""
Batch Processing Test
Test multiple prescriptions processing with dose controller + SUT + AI pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_prescription_processor import UnifiedPrescriptionProcessor
import json
from datetime import datetime

def create_test_batch():
    """Create test batch of multiple prescriptions with different scenarios"""
    
    return [
        # Test Case 1: High dose potential violation
        {
            "recete_no": "BATCH_001",
            "hasta_tc": "11111111111", 
            "hasta_ad": "Ali",
            "hasta_soyad": "Yilmaz",
            "hasta_dogum_tarihi": "1980-01-01",
            "drugs": [
                {
                    "ilac_adi": "TENOFOVIR ALAFENAMID 25mg TABLET",
                    "adet": "120",  # High dose
                    "rapor_kodu": "R100001",
                    "msj": "var",
                    "mesaj_kodlari": "1013(1), 1301", 
                    "etken_madde": "TENOFOVIR ALAFENAMID FUMARAT"
                }
            ],
            "drug_messages": [{"kod": "1013", "aciklama": "Doz asimi"}],
            "report_details": {"tani_bilgileri": ["B18.1"], "doktor_bransi": "Gastroenteroloji"}
        },
        
        # Test Case 2: Normal prescription - should approve  
        {
            "recete_no": "BATCH_002",
            "hasta_tc": "22222222222",
            "hasta_ad": "Ayse", 
            "hasta_soyad": "Demir",
            "hasta_dogum_tarihi": "1985-06-15",
            "drugs": [
                {
                    "ilac_adi": "PARACETAMOL 500mg TABLET",
                    "adet": "20",
                    "rapor_kodu": "",
                    "msj": "yok"
                }
            ],
            "drug_messages": [],
            "report_details": {"tani_bilgileri": ["J06.9"], "doktor_bransi": "Aile Hekimligi"}
        },
        
        # Test Case 3: Multiple drugs with mixed report status
        {
            "recete_no": "BATCH_003",
            "hasta_tc": "33333333333",
            "hasta_ad": "Mehmet",
            "hasta_soyad": "Kaya", 
            "hasta_dogum_tarihi": "1975-03-20",
            "drugs": [
                {
                    "ilac_adi": "INSULIN GLARGINE 100IU/ml",
                    "adet": "5",
                    "rapor_kodu": "R200002", 
                    "msj": "var",
                    "mesaj_kodlari": "1038",
                    "etken_madde": "INSULIN GLARGINE"
                },
                {
                    "ilac_adi": "METFORMIN 500mg TABLET",
                    "adet": "60",
                    "rapor_kodu": "",
                    "msj": "yok"
                }
            ],
            "drug_messages": [{"kod": "1038", "aciklama": "Yas kisitlama"}],
            "report_details": {"tani_bilgileri": ["E11.9"], "doktor_bransi": "Endokrinoloji"}
        },
        
        # Test Case 4: SUT compliance issue
        {
            "recete_no": "BATCH_004", 
            "hasta_tc": "44444444444",
            "hasta_ad": "Fatma",
            "hasta_soyad": "Ozturk",
            "hasta_dogum_tarihi": "1990-12-10",
            "drugs": [
                {
                    "ilac_adi": "EXPENSIVE_DRUG_TEST 250mg",
                    "adet": "30", 
                    "rapor_kodu": "R300003",
                    "msj": "var",
                    "mesaj_kodlari": "1002",
                    "etken_madde": "TEST_COMPOUND"
                }
            ],
            "drug_messages": [{"kod": "1002", "aciklama": "Etkilesim uyarisi"}],
            "report_details": {"tani_bilgileri": ["Z99.9"], "doktor_bransi": "Test_Brans"}
        },
        
        # Test Case 5: Complex case for AI analysis
        {
            "recete_no": "BATCH_005",
            "hasta_tc": "55555555555", 
            "hasta_ad": "Hasan",
            "hasta_soyad": "Celik",
            "hasta_dogum_tarihi": "1965-08-25",
            "drugs": [
                {
                    "ilac_adi": "ADALIMUMAB 40mg/0.8ml", 
                    "adet": "2",
                    "rapor_kodu": "R400004",
                    "msj": "var",
                    "mesaj_kodlari": "1301, 1013, 1038",
                    "etken_madde": "ADALIMUMAB"
                },
                {
                    "ilac_adi": "PREDNISOLON 5mg TABLET",
                    "adet": "30", 
                    "rapor_kodu": "",
                    "msj": "yok"
                }
            ],
            "drug_messages": [
                {"kod": "1301", "aciklama": "Endikasyon uyarisi"},
                {"kod": "1013", "aciklama": "Doz asimi"},
                {"kod": "1038", "aciklama": "Yas kisitlama"}
            ],
            "report_details": {"tani_bilgileri": ["M05.9", "M79.3"], "doktor_bransi": "Romatoloji"}
        }
    ]

def test_batch_processing():
    """Test batch processing with multiple prescriptions"""
    
    print("=== BATCH PROCESSING TEST ===")
    print("Testing multiple prescriptions with diverse scenarios")
    
    try:
        print("\n--- PHASE 1: CREATING TEST BATCH ---")
        test_batch = create_test_batch()
        print(f"Created test batch with {len(test_batch)} prescriptions:")
        
        for i, prescription in enumerate(test_batch, 1):
            print(f"  {i}. {prescription['recete_no']} - {prescription['hasta_ad']} {prescription['hasta_soyad']}")
            drugs_count = len(prescription.get('drugs', []))
            reported_drugs = len([d for d in prescription.get('drugs', []) if d.get('rapor_kodu')])
            print(f"     Drugs: {drugs_count}, Reported: {reported_drugs}")
        
        print(f"\n--- PHASE 2: INITIALIZING UNIFIED PROCESSOR ---")
        processor = UnifiedPrescriptionProcessor()
        
        # Set fast mode for batch processing
        if processor.dose_controller:
            processor.dose_controller.control_mode = "fast"
            print(f"Dose controller mode: {processor.dose_controller.control_mode}")
        
        print("System status:")
        print(f"  Dose Controller: {'ACTIVE' if processor.dose_controller else 'MISSING'}")
        print(f"  SUT Database: {'ACTIVE' if processor.sut_db else 'MISSING'}")
        print(f"  AI Analyzer: {'ACTIVE' if processor.ai_analyzer else 'MISSING'}")
        
        print(f"\n--- PHASE 3: BATCH PROCESSING ---")
        print("Processing prescriptions sequentially...")
        
        start_time = datetime.now()
        results = []
        
        for i, prescription in enumerate(test_batch, 1):
            print(f"\nProcessing {i}/{len(test_batch)}: {prescription['recete_no']}")
            
            try:
                result = processor.process_single_prescription(prescription, "batch_test")
                results.append(result)
                
                # Show immediate results
                decision = result.get('final_decision', 'unknown')
                processing_time = result.get('processing_metadata', {}).get('processing_time_seconds', 0)
                print(f"  Result: {decision.upper()} ({processing_time:.2f}s)")
                
            except Exception as e:
                print(f"  ERROR processing {prescription['recete_no']}: {e}")
                results.append({
                    "prescription_id": prescription['recete_no'],
                    "error": str(e),
                    "final_decision": "error"
                })
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"\n=== BATCH PROCESSING COMPLETED ===")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"Average time per prescription: {total_time/len(test_batch):.2f}s")
        
        # Analyze results
        print(f"\n--- PHASE 4: RESULTS ANALYSIS ---")
        
        approve_count = len([r for r in results if r.get('final_decision') == 'approve'])
        hold_count = len([r for r in results if r.get('final_decision') == 'hold'])  
        reject_count = len([r for r in results if r.get('final_decision') == 'reject'])
        error_count = len([r for r in results if r.get('final_decision') == 'error'])
        
        print(f"\nDECISION SUMMARY:")
        print(f"  Approved: {approve_count}")
        print(f"  Hold: {hold_count}")
        print(f"  Rejected: {reject_count}")
        print(f"  Errors: {error_count}")
        
        # Detailed results for each prescription
        print(f"\nDETAILED RESULTS:")
        
        for i, result in enumerate(results, 1):
            print(f"\n=== PRESCRIPTION {i} ===")
            print(f"ID: {result.get('prescription_id', 'N/A')}")
            print(f"Decision: {result.get('final_decision', 'N/A')}")
            
            if result.get('error'):
                print(f"Error: {result['error']}")
                continue
            
            # Processing times
            metadata = result.get('processing_metadata', {})
            print(f"Processing times:")
            print(f"  Dose: {metadata.get('dose_processing_time', 0):.3f}s")
            print(f"  SUT: {metadata.get('sut_processing_time', 0):.3f}s")
            print(f"  AI: {metadata.get('ai_processing_time', 0):.3f}s")
            print(f"  Total: {metadata.get('processing_time_seconds', 0):.3f}s")
            
            # Analysis results
            dose_analysis = result.get('dose_analysis', {})
            sut_analysis = result.get('sut_analysis', {}) 
            ai_analysis = result.get('ai_analysis', {})
            
            print(f"Analysis results:")
            print(f"  Dose: {dose_analysis.get('action', 'N/A')} (drugs: {dose_analysis.get('drugs_analyzed', 0)})")
            print(f"  SUT: {sut_analysis.get('action', 'N/A')} (compliance: {sut_analysis.get('compliant', False)})")
            print(f"  AI: {ai_analysis.get('action', 'N/A')} (confidence: {ai_analysis.get('confidence', 0):.2f})")
        
        # Performance metrics
        processing_times = [r.get('processing_metadata', {}).get('processing_time_seconds', 0) for r in results if not r.get('error')]
        
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            print(f"\nPERFORMANCE METRICS:")
            print(f"  Average processing: {avg_time:.3f}s")
            print(f"  Fastest: {min_time:.3f}s")
            print(f"  Slowest: {max_time:.3f}s")
            print(f"  Throughput: {len(processing_times)/total_time:.2f} prescriptions/second")
        
        # System assessment
        print(f"\n--- PHASE 5: SYSTEM ASSESSMENT ---")
        
        successful_results = [r for r in results if not r.get('error')]
        success_rate = len(successful_results) / len(results) * 100
        
        print(f"SUCCESS METRICS:")
        print(f"  Success rate: {success_rate:.1f}% ({len(successful_results)}/{len(results)})")
        print(f"  Error rate: {100-success_rate:.1f}%")
        
        # Check system reliability
        dose_working = sum(1 for r in successful_results if r.get('dose_analysis', {}).get('action') != 'N/A')
        sut_working = sum(1 for r in successful_results if r.get('sut_analysis', {}).get('action') != 'N/A')
        ai_working = sum(1 for r in successful_results if r.get('ai_analysis', {}).get('action') != 'N/A')
        
        if successful_results:
            print(f"SYSTEM RELIABILITY:")
            print(f"  Dose Controller: {dose_working}/{len(successful_results)} ({dose_working/len(successful_results)*100:.0f}%)")
            print(f"  SUT Analysis: {sut_working}/{len(successful_results)} ({sut_working/len(successful_results)*100:.0f}%)")
            print(f"  AI Analysis: {ai_working}/{len(successful_results)} ({ai_working/len(successful_results)*100:.0f}%)")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"batch_processing_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\nResults saved to: {results_file}")
        
        # Final assessment
        if success_rate >= 80 and avg_time <= 10:
            print(f"\nBATCH PROCESSING TEST: SUCCESS!")
            print(f"System ready for production batch processing")
            return True
        else:
            print(f"\nBATCH PROCESSING TEST: NEEDS IMPROVEMENT")
            print(f"Success rate or performance below thresholds")
            return False
        
    except Exception as e:
        print(f"BATCH TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_batch_processing()
    sys.exit(0 if success else 1)