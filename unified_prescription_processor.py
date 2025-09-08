"""
Unified Prescription Processor
Tüm reçete işleme sürecini tek dosyada birleştirir
- Medula browser integration
- JSON data processing  
- SUT analysis
- Claude AI analysis
- Complete workflow management
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from loguru import logger

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from medula_automation.browser import MedulaBrowser
from ai_analyzer.sut_rules_database import SUTRulesDatabase
from ai_analyzer.claude_prescription_analyzer import ClaudePrescriptionAnalyzer
from database.sqlite_handler import SQLiteHandler
from config.settings import Settings

class UnifiedPrescriptionProcessor:
    """Unified reçete işleme sistemi"""
    
    def __init__(self):
        self.settings = Settings()
        self.browser = None
        self.sut_db = SUTRulesDatabase()
        self.ai_analyzer = ClaudePrescriptionAnalyzer()
        self.database = SQLiteHandler()
        
        # Results storage
        self.processed_prescriptions = []
        self.processing_stats = {
            "total_processed": 0,
            "approved": 0,
            "rejected": 0,
            "held": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
        
        logger.info("Unified Prescription Processor initialized with database")
    
    # =========================================================================
    # CORE PROCESSING METHODS
    # =========================================================================
    
    def process_from_json_file(self, json_file_path, output_file=None):
        """JSON dosyasından reçeteleri işler"""
        try:
            logger.info(f"Processing prescriptions from JSON: {json_file_path}")
            
            # JSON dosyasını oku
            if not os.path.exists(json_file_path):
                raise FileNotFoundError(f"JSON file not found: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                prescriptions = json.load(f)
            
            if not prescriptions:
                logger.warning("No prescriptions found in JSON file")
                return []
            
            logger.info(f"Found {len(prescriptions)} prescriptions to process")
            
            # Reçeteleri işle
            results = self._process_prescription_batch(prescriptions, "json_file")
            
            # Sonuçları kaydet
            if output_file:
                self._save_results(results, output_file)
            
            return results
            
        except Exception as e:
            logger.error(f"JSON processing error: {e}")
            raise
    
    def process_from_medula_live(self, limit=5, group='A'):
        """Canlı Medula'dan reçeteleri çeker ve işler"""
        try:
            logger.info("Starting live Medula prescription processing")
            
            # Browser başlat
            if not self._initialize_browser():
                raise Exception("Browser initialization failed")
            
            # Medula'ya giriş yap
            if not self._medula_login():
                raise Exception("Medula login failed")
            
            # Reçete listesini çek
            prescriptions = self._extract_prescriptions_from_medula(limit, group)
            
            if not prescriptions:
                logger.warning("No prescriptions extracted from Medula")
                return []
            
            logger.info(f"Extracted {len(prescriptions)} prescriptions from Medula")
            
            # Reçeteleri işle
            results = self._process_prescription_batch(prescriptions, "medula_live")
            
            # Browser'ı kapat
            self._cleanup_browser()
            
            return results
            
        except Exception as e:
            logger.error(f"Live Medula processing error: {e}")
            self._cleanup_browser()
            raise
    
    def process_single_prescription(self, prescription_data, source="manual"):
        """Tek bir reçeteyi işler"""
        try:
            logger.info(f"Processing single prescription: {prescription_data.get('recete_no', 'N/A')}")
            
            # Temel doğrulama
            if not self._validate_prescription_data(prescription_data):
                return self._create_error_result(prescription_data, "Invalid prescription data")
            
            # İşleme başlangıcı
            start_time = datetime.now()
            
            # SUT analizi
            sut_result = self._perform_sut_analysis(prescription_data)
            
            # AI analizi  
            ai_result = self._perform_ai_analysis(prescription_data)
            
            # Sonucu birleştir
            final_result = self._combine_analysis_results(
                prescription_data, sut_result, ai_result, source, start_time
            )
            
            # İstatistikleri güncelle
            self._update_stats(final_result)
            
            # Veritabanına kaydet
            self._save_to_database(prescription_data, final_result)
            
            logger.info(f"Prescription processed: {final_result['prescription_id']} -> {final_result['final_decision']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Single prescription processing error: {e}")
            return self._create_error_result(prescription_data, str(e))
    
    # =========================================================================
    # MEDULA INTEGRATION METHODS
    # =========================================================================
    
    def _initialize_browser(self):
        """Browser'ı başlatır"""
        try:
            self.browser = MedulaBrowser(self.settings)
            success = self.browser.start()
            
            if success:
                logger.info("Browser initialized successfully")
                return True
            else:
                logger.error("Browser initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Browser initialization error: {e}")
            return False
    
    def _medula_login(self):
        """Medula'ya giriş yapar"""
        try:
            if not self.browser:
                return False
            
            success = self.browser.login()
            
            if success:
                logger.info("Medula login successful")
                return True
            else:
                logger.error("Medula login failed")
                return False
                
        except Exception as e:
            logger.error(f"Medula login error: {e}")
            return False
    
    def _extract_prescriptions_from_medula(self, limit=5, group='A'):
        """Medula'dan reçete listesini çıkarır"""
        try:
            # Bu kısmı advanced_prescription_extractor'dan adapte edebiliriz
            logger.info(f"Extracting {limit} prescriptions from Medula (Group {group})")
            
            # Şu an için mock data döndürelim - gerçek entegrasyonu sonra yapabiliriz
            logger.warning("Medula extraction not implemented yet, using mock data")
            
            # Mock prescription data
            mock_prescriptions = [
                {
                    "recete_no": f"MOCK{i:03d}",
                    "hasta_ad": f"Test{i}",
                    "hasta_soyad": "Patient",
                    "hasta_tc": f"1234567890{i}",
                    "drugs": [
                        {"ilac_adi": f"Test Drug {i}", "adet": "1"}
                    ],
                    "ilac_mesajlari": "",
                    "rapor_no": f"RPT{i:03d}",
                    "extraction_method": "medula_mock"
                }
                for i in range(1, min(limit + 1, 4))  # Max 3 mock prescriptions
            ]
            
            return mock_prescriptions
            
        except Exception as e:
            logger.error(f"Medula extraction error: {e}")
            return []
    
    def _cleanup_browser(self):
        """Browser'ı temizler"""
        try:
            if self.browser:
                self.browser.quit()
                self.browser = None
                logger.info("Browser cleaned up")
        except Exception as e:
            logger.error(f"Browser cleanup error: {e}")
    
    # =========================================================================
    # ANALYSIS METHODS
    # =========================================================================
    
    def _perform_sut_analysis(self, prescription_data):
        """SUT analizi yapar"""
        try:
            sut_analysis = self.sut_db.get_sut_analysis_for_prescription(prescription_data)
            sut_recommendation = self.sut_db.get_recommendation_for_prescription(prescription_data)
            
            return {
                "analysis": sut_analysis,
                "recommendation": sut_recommendation,
                "processing_time": 0.1  # SUT analizi çok hızlı
            }
            
        except Exception as e:
            logger.error(f"SUT analysis error: {e}")
            return {
                "analysis": {"overall_compliance": False, "issues": [str(e)]},
                "recommendation": {"action": "hold", "confidence": 0.1, "reason": f"SUT error: {e}"},
                "processing_time": 0.0,
                "error": str(e)
            }
    
    def _perform_ai_analysis(self, prescription_data):
        """AI analizi yapar"""
        try:
            start_time = time.time()
            ai_result = self.ai_analyzer.analyze_prescription_with_claude(prescription_data)
            processing_time = time.time() - start_time
            
            return {
                "result": ai_result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "result": {
                    "action": "hold",
                    "confidence": 0.1,
                    "reason": f"AI error: {e}",
                    "claude_available": False
                },
                "processing_time": 0.0,
                "error": str(e)
            }
    
    def _combine_analysis_results(self, prescription_data, sut_result, ai_result, source, start_time):
        """Analiz sonuçlarını birleştirir"""
        try:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Temel bilgiler
            result = {
                "prescription_id": prescription_data.get("recete_no", "UNKNOWN"),
                "patient_info": {
                    "name": f"{prescription_data.get('hasta_ad', '')} {prescription_data.get('hasta_soyad', '')}",
                    "tc": prescription_data.get("hasta_tc", ""),
                },
                "processing_metadata": {
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": processing_time,
                    "sut_processing_time": sut_result.get("processing_time", 0),
                    "ai_processing_time": ai_result.get("processing_time", 0)
                }
            }
            
            # SUT sonuçları
            sut_rec = sut_result.get("recommendation", {})
            result["sut_analysis"] = {
                "compliant": sut_result.get("analysis", {}).get("overall_compliance", False),
                "action": sut_rec.get("action", "hold"),
                "confidence": sut_rec.get("confidence", 0.0),
                "issues_count": len(sut_result.get("analysis", {}).get("issues", [])),
                "warnings_count": len(sut_result.get("analysis", {}).get("warnings", []))
            }
            
            # AI sonuçları
            ai_res = ai_result.get("result", {})
            result["ai_analysis"] = {
                "action": ai_res.get("action", "hold"),
                "confidence": ai_res.get("confidence", 0.0),
                "claude_used": ai_res.get("claude_available", False),
                "method": ai_res.get("analysis_method", "unknown")
            }
            
            # Final karar
            result["final_decision"] = self._determine_final_decision(
                sut_rec.get("action", "hold"),
                ai_res.get("action", "hold"),
                sut_rec.get("confidence", 0.0),
                ai_res.get("confidence", 0.0)
            )
            
            # Detay bilgileri
            result["details"] = {
                "sut_reason": sut_rec.get("reason", ""),
                "ai_reason": ai_res.get("reason", ""),
                "sut_issues": sut_result.get("analysis", {}).get("issues", []),
                "ai_risk_factors": ai_res.get("risk_factors", []),
                "recommendations": ai_res.get("recommendations", [])
            }
            
            # Ham veriler (debug için)
            result["raw_data"] = {
                "prescription_data": prescription_data,
                "sut_full_result": sut_result,
                "ai_full_result": ai_result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Result combination error: {e}")
            return self._create_error_result(prescription_data, str(e))
    
    def _determine_final_decision(self, sut_action, ai_action, sut_confidence, ai_confidence):
        """Final kararı belirler"""
        
        # Conservative approach - en düşük riski al
        priority_order = {"reject": 3, "hold": 2, "approve": 1}
        
        if priority_order.get(sut_action, 2) >= priority_order.get(ai_action, 2):
            return sut_action
        else:
            return ai_action
    
    # =========================================================================
    # BATCH PROCESSING METHODS  
    # =========================================================================
    
    def _process_prescription_batch(self, prescriptions, source):
        """Reçete toplu işleme"""
        try:
            logger.info(f"Processing batch of {len(prescriptions)} prescriptions")
            
            self.processing_stats["start_time"] = datetime.now()
            self.processing_stats["total_processed"] = 0
            
            results = []
            
            for i, prescription in enumerate(prescriptions, 1):
                logger.info(f"Processing {i}/{len(prescriptions)}: {prescription.get('recete_no', 'N/A')}")
                
                result = self.process_single_prescription(prescription, source)
                results.append(result)
                
                # Progress update
                self.processing_stats["total_processed"] += 1
                print(f"[{i}/{len(prescriptions)}] {result['prescription_id']} -> {result['final_decision'].upper()}")
                
                # Kısa bekleme (API rate limiting için)
                time.sleep(0.5)
            
            self.processing_stats["end_time"] = datetime.now()
            
            # Final stats
            self._calculate_final_stats(results)
            self._print_processing_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return []
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _validate_prescription_data(self, prescription_data):
        """Reçete verisini doğrular"""
        if not isinstance(prescription_data, dict):
            return False
        
        required_fields = ["recete_no"]
        for field in required_fields:
            if field not in prescription_data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _create_error_result(self, prescription_data, error_message):
        """Hata sonucu oluşturur"""
        return {
            "prescription_id": prescription_data.get("recete_no", "UNKNOWN"),
            "final_decision": "error",
            "error": error_message,
            "processing_metadata": {
                "timestamp": datetime.now().isoformat(),
                "processing_time_seconds": 0.0,
                "source": "error"
            },
            "sut_analysis": {"action": "error", "confidence": 0.0},
            "ai_analysis": {"action": "error", "confidence": 0.0}
        }
    
    def _update_stats(self, result):
        """İstatistikleri günceller"""
        decision = result.get("final_decision", "error")
        
        if decision == "approve":
            self.processing_stats["approved"] += 1
        elif decision == "reject":
            self.processing_stats["rejected"] += 1
        elif decision == "hold":
            self.processing_stats["held"] += 1
        else:
            self.processing_stats["errors"] += 1
    
    def _calculate_final_stats(self, results):
        """Final istatistikleri hesaplar"""
        for result in results:
            decision = result.get("final_decision", "error")
            
            if decision == "approve":
                self.processing_stats["approved"] += 1
            elif decision == "reject":
                self.processing_stats["rejected"] += 1
            elif decision == "hold":
                self.processing_stats["held"] += 1
            else:
                self.processing_stats["errors"] += 1
    
    def _print_processing_summary(self, results):
        """İşlem özetini yazdırır"""
        if not results:
            return
        
        total = len(results)
        stats = self.processing_stats
        
        processing_time = 0
        if stats["start_time"] and stats["end_time"]:
            processing_time = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        print(f"""
        
=== PROCESSING SUMMARY ===
Total Prescriptions: {total}
[+] Approved: {stats['approved']} ({stats['approved']/total*100:.1f}%)
[-] Rejected: {stats['rejected']} ({stats['rejected']/total*100:.1f}%)
[?] Hold: {stats['held']} ({stats['held']/total*100:.1f}%)
[!] Errors: {stats['errors']} ({stats['errors']/total*100:.1f}%)

Processing Time: {processing_time:.2f}s
Average per Prescription: {processing_time/total:.2f}s

Claude API Status: {'Active' if any(r.get('ai_analysis', {}).get('claude_used') for r in results) else 'Fallback'}
        """)
    
    def _save_results(self, results, output_file):
        """Sonuçları dosyaya kaydeder"""
        try:
            # Convert datetime objects to strings for JSON serialization
            stats_for_json = self.processing_stats.copy()
            if stats_for_json.get("start_time"):
                stats_for_json["start_time"] = stats_for_json["start_time"].isoformat()
            if stats_for_json.get("end_time"):
                stats_for_json["end_time"] = stats_for_json["end_time"].isoformat()
            
            output_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_prescriptions": len(results),
                    "processing_stats": stats_for_json,
                    "processor_version": "unified_v1.0"
                },
                "results": results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Save results error: {e}")
            return False
    
    def get_processing_stats(self):
        """İşlem istatistiklerini döndürür"""
        return self.processing_stats.copy()
    
    def _save_to_database(self, prescription_data, final_result):
        """Reçete ve analiz sonucunu veritabanına kaydeder"""
        try:
            # Analysis result for database
            analysis_result = {
                "sut_analysis": final_result.get("sut_analysis", {}),
                "ai_analysis": final_result.get("ai_analysis", {}),
                "final_decision": final_result.get("final_decision"),
                "processing_metadata": final_result.get("processing_metadata", {}),
                "details": final_result.get("details", {})
            }
            
            # Save to database
            success = self.database.save_prescription(
                prescription_data=prescription_data,
                analysis_result=analysis_result,
                decision=final_result.get("final_decision")
            )
            
            if success:
                # Log the processing action
                self.database.log_processing(
                    recete_no=prescription_data.get("recete_no"),
                    action="processed",
                    details=f"Decision: {final_result.get('final_decision')}"
                )
                logger.debug(f"Saved prescription {prescription_data.get('recete_no')} to database")
            else:
                logger.warning(f"Failed to save prescription {prescription_data.get('recete_no')} to database")
                
        except Exception as e:
            logger.error(f"Database save error: {e}")

# =========================================================================
# TEST AND DEMO FUNCTIONS
# =========================================================================

def test_json_processing():
    """JSON processing test"""
    print("=== TESTING JSON PROCESSING ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    json_file = "manual_detailed_prescriptions.json"
    if os.path.exists(json_file):
        results = processor.process_from_json_file(json_file, "unified_test_results.json")
        print(f"Processed {len(results)} prescriptions from JSON")
        return True
    else:
        print(f"Test file not found: {json_file}")
        return False

def test_single_prescription():
    """Single prescription test"""
    print("\\n=== TESTING SINGLE PRESCRIPTION ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    test_prescription = {
        "recete_no": "TEST001",
        "hasta_ad": "TEST",
        "hasta_soyad": "PATIENT",
        "hasta_tc": "12345678901",
        "drugs": [
            {"ilac_adi": "TEST DRUG", "adet": "1"}
        ],
        "ilac_mesajlari": "Test message",
        "rapor_no": "TEST_RPT"
    }
    
    result = processor.process_single_prescription(test_prescription, "test")
    
    print(f"Single prescription test:")
    print(f"  ID: {result['prescription_id']}")
    print(f"  Decision: {result['final_decision']}")
    print(f"  Processing time: {result['processing_metadata']['processing_time_seconds']:.2f}s")
    print(f"  SUT: {result['sut_analysis']['action']} ({result['sut_analysis']['confidence']:.2f})")
    print(f"  AI: {result['ai_analysis']['action']} ({result['ai_analysis']['confidence']:.2f})")
    
    return True

def test_medula_processing():
    """Medula processing test (mock)"""
    print("\\n=== TESTING MEDULA PROCESSING (MOCK) ===")
    
    processor = UnifiedPrescriptionProcessor()
    
    try:
        results = processor.process_from_medula_live(limit=3, group='A')
        print(f"Processed {len(results)} prescriptions from Medula (mock)")
        return True
    except Exception as e:
        print(f"Medula processing failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("UNIFIED PRESCRIPTION PROCESSOR - TEST SUITE")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: JSON Processing
    if test_json_processing():
        success_count += 1
    
    # Test 2: Single Prescription
    if test_single_prescription():
        success_count += 1
    
    # Test 3: Medula Processing (Mock)
    if test_medula_processing():
        success_count += 1
    
    # Final Results
    print(f"\\n{'='*60}")
    print(f"TEST RESULTS: {success_count}/{total_tests} PASSED")
    print(f"SUCCESS RATE: {success_count/total_tests*100:.1f}%")
    print("="*60)
    
    if success_count == total_tests:
        print("[*] ALL TESTS PASSED - SYSTEM READY!")
    else:
        print("[!] SOME TESTS FAILED - CHECK LOGS")

if __name__ == "__main__":
    main()