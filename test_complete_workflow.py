"""
End-to-End Workflow Test
Tüm sistemin entegre testini yapar
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from ai_analyzer.claude_prescription_analyzer import ClaudePrescriptionAnalyzer
from ai_analyzer.sut_rules_database import SUTRulesDatabase

def test_complete_workflow():
    """Complete workflow testi"""
    print("=" * 60)
    print("[+] ECZANE OTOMASYON - COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    # 1. Test Data Preparation
    print("\\n[STEP 1] Test verileri hazirlanıyor...")
    prescription_file = "manual_detailed_prescriptions.json"
    
    if not os.path.exists(prescription_file):
        print("[-] Test dosyasi bulunamadi:", prescription_file)
        return False
    
    with open(prescription_file, 'r', encoding='utf-8') as f:
        prescriptions = json.load(f)
    
    print(f"[+] {len(prescriptions)} reçete test verileri yüklendi")
    
    # 2. SUT Rules Database Test
    print("\\n[STEP 2] SUT Rules Database test ediliyor...")
    sut_db = SUTRulesDatabase()
    
    # Her reçete için SUT analizi
    sut_results = []
    for i, prescription in enumerate(prescriptions, 1):
        print(f"  [{i}/{len(prescriptions)}] {prescription.get('recete_no', 'N/A')} SUT analizi...")
        
        sut_analysis = sut_db.get_sut_analysis_for_prescription(prescription)
        sut_recommendation = sut_db.get_recommendation_for_prescription(prescription)
        
        sut_results.append({
            "prescription_id": prescription.get('recete_no', 'N/A'),
            "sut_compliant": sut_analysis.get('overall_compliance', False),
            "sut_action": sut_recommendation.get('action', 'unknown'),
            "sut_confidence": sut_recommendation.get('confidence', 0.0),
            "issues_count": len(sut_analysis.get('issues', [])),
            "warnings_count": len(sut_analysis.get('warnings', []))
        })
    
    print("[+] SUT analizi tamamlandı")
    
    # 3. Claude AI Analyzer Test
    print("\\n[STEP 3] Claude AI Analyzer test ediliyor...")
    analyzer = ClaudePrescriptionAnalyzer()
    
    # Sadece ilk 2 reçeteyi test et (hız için)
    test_prescriptions = prescriptions[:2]
    ai_results = []
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"  [{i}/{len(test_prescriptions)}] {prescription.get('recete_no', 'N/A')} AI analizi...")
        
        result = analyzer.analyze_prescription_with_claude(prescription)
        
        ai_results.append({
            "prescription_id": prescription.get('recete_no', 'N/A'),
            "ai_action": result.get('action', 'unknown'),
            "ai_confidence": result.get('confidence', 0.0),
            "claude_used": result.get('claude_available', False),
            "analysis_method": result.get('analysis_method', 'unknown')
        })
        
        print(f"    -> {result['action'].upper()} (güven: {result.get('confidence', 0):.2f})")
    
    print("[+] AI analizi tamamlandı")
    
    # 4. Integration Test
    print("\\n[STEP 4] Entegrasyon testi...")
    
    integration_score = 0
    total_tests = 0
    
    # Test 1: SUT Database çalışıyor mu?
    if sut_results and all(r['sut_action'] != 'unknown' for r in sut_results):
        integration_score += 1
        print("  [+] SUT Database integration OK")
    else:
        print("  [-] SUT Database integration FAIL")
    total_tests += 1
    
    # Test 2: AI Analyzer çalışıyor mu?
    if ai_results and all(r['ai_action'] != 'unknown' for r in ai_results):
        integration_score += 1
        print("  [+] AI Analyzer integration OK")
    else:
        print("  [-] AI Analyzer integration FAIL")
    total_tests += 1
    
    # Test 3: JSON formatları uyumlu mu?
    try:
        test_output = {
            "timestamp": datetime.now().isoformat(),
            "sut_results": sut_results,
            "ai_results": ai_results
        }
        json.dumps(test_output, ensure_ascii=False)
        integration_score += 1
        print("  [+] JSON format compatibility OK")
    except:
        print("  [-] JSON format compatibility FAIL")
    total_tests += 1
    
    # 5. Performance Test
    print("\\n[STEP 5] Performance testi...")
    
    start_time = datetime.now()
    
    # 1 reçete için tam workflow
    test_prescription = prescriptions[0]
    
    # SUT analizi
    sut_start = datetime.now()
    sut_analysis = sut_db.get_sut_analysis_for_prescription(test_prescription)
    sut_time = (datetime.now() - sut_start).total_seconds()
    
    # AI analizi
    ai_start = datetime.now()
    ai_result = analyzer.analyze_prescription_with_claude(test_prescription)
    ai_time = (datetime.now() - ai_start).total_seconds()
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    print(f"  SUT analizi: {sut_time:.2f}s")
    print(f"  AI analizi: {ai_time:.2f}s")
    print(f"  Toplam: {total_time:.2f}s")
    
    if total_time < 5:  # 5 saniyeden az
        integration_score += 1
        print("  [+] Performance OK (< 5s per prescription)")
    else:
        print("  [-] Performance SLOW (> 5s per prescription)")
    total_tests += 1
    
    # 6. Final Report
    print("\\n" + "=" * 60)
    print("[#] WORKFLOW TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (integration_score / total_tests) * 100
    
    print(f"Integration Tests: {integration_score}/{total_tests} (%{success_rate:.1f})")
    print(f"SUT Database: {'[+] OK' if sut_results else '[-] FAIL'}")
    print(f"AI Analyzer: {'[+] OK' if ai_results else '[-] FAIL'}")
    print(f"Performance: {total_time:.2f}s per prescription")
    
    # SUT İstatistikleri
    sut_approve = len([r for r in sut_results if r['sut_action'] == 'approve'])
    sut_reject = len([r for r in sut_results if r['sut_action'] == 'reject'])  
    sut_hold = len([r for r in sut_results if r['sut_action'] == 'hold'])
    
    print(f"\\nSUT Results ({len(sut_results)} prescriptions):")
    print(f"  [+] Approved: {sut_approve}")
    print(f"  [-] Rejected: {sut_reject}")
    print(f"  [?] Hold: {sut_hold}")
    
    # AI İstatistikleri  
    if ai_results:
        ai_approve = len([r for r in ai_results if r['ai_action'] == 'approve'])
        ai_reject = len([r for r in ai_results if r['ai_action'] == 'reject'])
        ai_hold = len([r for r in ai_results if r['ai_action'] == 'hold'])
        
        print(f"\\nAI Results ({len(ai_results)} prescriptions):")
        print(f"  [+] Approved: {ai_approve}")
        print(f"  [-] Rejected: {ai_reject}")
        print(f"  [?] Hold: {ai_hold}")
    
    # Claude API Status
    claude_available = any(r.get('claude_used', False) for r in ai_results)
    print(f"\\nClaude API: {'[+] Active' if claude_available else '[-] Fallback to SUT only'}")
    
    # Overall Status
    if success_rate >= 75:
        status = "[*] EXCELLENT"
        color = "[+]"
    elif success_rate >= 50:
        status = "[!] NEEDS WORK"
        color = "[!]"
    else:
        status = "[-] MAJOR ISSUES"
        color = "[-]"
    
    print(f"\\n{color} OVERALL STATUS: {status} ({success_rate:.1f}%)")
    
    # Sonraki adımlar
    print("\\n[:] NEXT STEPS:")
    if not claude_available:
        print("  1. Fix Claude API model issue")
    if sut_hold + sut_reject > sut_approve:
        print("  2. Review SUT rules - too many rejections")
    if total_time > 3:
        print("  3. Optimize performance")
    print("  4. Add GUI integration")
    print("  5. Add batch processing")
    
    return success_rate >= 75

def test_single_prescription():
    """Tek reçete için detaylı test"""
    print("\\n" + "=" * 40)
    print("[>] SINGLE PRESCRIPTION DETAILED TEST")
    print("=" * 40)
    
    # Test prescription
    test_prescription = {
        "recete_no": "3GP25RF",
        "hasta_ad": "YALÇIN",
        "hasta_soyad": "DURDAĞI", 
        "hasta_tc": "11916110202",
        "drugs": [
            {"ilac_adi": "VEMLIDY 25MG 30 FILM KAPLI TABLET", "adet": "33"},
            {"ilac_adi": "PANTO 40 MG.28 TABLET", "adet": "3"}
        ],
        "ilac_mesajlari": "1013(1) - 4.2.13.1 Kronik Hepatit B tedavisi",
        "rapor_no": "1992805",
        "report_details": {
            "rapor_numarasi": "1992805",
            "tani_bilgileri": [{"tani_kodu": "B18.1"}]
        }
    }
    
    print(f"Test Prescription: {test_prescription['recete_no']}")
    print(f"Patient: {test_prescription['hasta_ad']} {test_prescription['hasta_soyad']}")
    print(f"Drugs: {len(test_prescription['drugs'])}")
    
    # SUT Test
    print("\\n[SUT ANALYSIS]")
    sut_db = SUTRulesDatabase()
    sut_analysis = sut_db.get_sut_analysis_for_prescription(test_prescription)
    sut_recommendation = sut_db.get_recommendation_for_prescription(test_prescription)
    
    print(f"Compliance: {sut_analysis['overall_compliance']}")
    print(f"Issues: {len(sut_analysis.get('issues', []))}")
    print(f"Decision: {sut_recommendation['action'].upper()}")
    print(f"Confidence: {sut_recommendation['confidence']}")
    
    if sut_analysis.get('issues'):
        print("Issues:")
        for issue in sut_analysis['issues'][:3]:
            print(f"  - {issue}")
    
    # AI Test
    print("\\n[AI ANALYSIS]")
    analyzer = ClaudePrescriptionAnalyzer()
    ai_result = analyzer.analyze_prescription_with_claude(test_prescription)
    
    print(f"Decision: {ai_result['action'].upper()}")
    print(f"Confidence: {ai_result['confidence']}")
    print(f"Method: {ai_result.get('analysis_method', 'unknown')}")
    print(f"Reason: {ai_result.get('reason', 'N/A')[:100]}...")
    
    return True

if __name__ == "__main__":
    print("Starting complete workflow test...")
    
    # Full workflow test
    success = test_complete_workflow()
    
    # Single prescription detailed test
    test_single_prescription()
    
    print(f"\\n{'='*60}")
    print(f"[=] TEST COMPLETED - {'SUCCESS' if success else 'NEEDS WORK'}")
    print("="*60)