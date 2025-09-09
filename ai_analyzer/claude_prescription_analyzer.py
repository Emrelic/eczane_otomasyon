"""
Claude AI ile Reçete Analiz Sistemi
Gerçek reçete verilerini Claude API ile analiz eder
"""

import json
import os
import sys
from datetime import datetime
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai_analyzer.sut_rules_database import SUTRulesDatabase
from config.settings import Settings

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logger.warning("Anthropic library not found. Install with: pip install anthropic")

class ClaudePrescriptionAnalyzer:
    """Claude AI ile reçete analizi yapan sınıf"""
    
    def __init__(self):
        self.settings = Settings()
        self.sut_db = SUTRulesDatabase()
        
        # Claude API setup
        if CLAUDE_AVAILABLE and hasattr(self.settings, 'ANTHROPIC_API_KEY') and self.settings.ANTHROPIC_API_KEY:
            try:
                self.client = anthropic.Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)
                self.model = "claude-3-haiku-20240307"  # Working model
                self.claude_enabled = True
                logger.info("Claude API initialized successfully")
            except Exception as e:
                logger.error(f"Claude API initialization failed: {e}")
                self.claude_enabled = False
        else:
            self.claude_enabled = False
            logger.warning("Claude API not available - using SUT rules only")
        
        self.analysis_results = []
    
    def analyze_prescription_with_claude(self, prescription_data):
        """Claude AI ile reçete analizi yapar"""
        try:
            if not self.claude_enabled:
                return self._analyze_with_sut_only(prescription_data)
            
            # SUT analizi yap
            sut_analysis = self.sut_db.get_sut_analysis_for_prescription(prescription_data)
            sut_recommendation = self.sut_db.get_recommendation_for_prescription(prescription_data)
            
            # Claude için prompt hazırla
            prompt = self._create_claude_prompt(prescription_data, sut_analysis)
            
            # Claude API çağrısı
            claude_response = self._call_claude_api(prompt)
            
            # Yanıtı birleştir
            final_decision = self._combine_analyses(sut_recommendation, claude_response, prescription_data)
            
            logger.info(f"Prescription {prescription_data.get('recete_no')} analyzed - Decision: {final_decision['action']}")
            
            return final_decision
            
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return self._analyze_with_sut_only(prescription_data)
    
    def _analyze_with_sut_only(self, prescription_data):
        """Sadece SUT kuralları ile analiz"""
        logger.info("Using SUT rules only for analysis")
        
        sut_recommendation = self.sut_db.get_recommendation_for_prescription(prescription_data)
        
        return {
            **sut_recommendation,
            "analysis_method": "sut_only",
            "timestamp": datetime.now().isoformat(),
            "prescription_id": prescription_data.get("recete_no", ""),
            "claude_available": False
        }
    
    def _create_claude_prompt(self, prescription_data, sut_analysis):
        """Claude için detaylı prompt oluşturur"""
        
        # İlaçları formatla
        drugs_text = ""
        for i, drug in enumerate(prescription_data.get("drugs", []), 1):
            drugs_text += f"{i}. {drug.get('ilac_adi', 'N/A')} - Adet: {drug.get('adet', 'N/A')}\\n"
        
        # Tanı kodlarını formatla
        diagnosis_codes = []
        if "report_details" in prescription_data:
            tani_bilgileri = prescription_data["report_details"].get("tani_bilgileri", [])
            for tani in tani_bilgileri:
                if isinstance(tani, dict):
                    diagnosis_codes.append(tani.get("tani_kodu", ""))
                else:
                    diagnosis_codes.append(str(tani))
        
        diagnosis_text = ", ".join(diagnosis_codes) if diagnosis_codes else "Belirtilmemiş"
        
        # SUT analizi özeti
        sut_summary = f"""
        SUT Uyumluluğu: {'✓ Uyumlu' if sut_analysis.get('overall_compliance') else '✗ Uyumsuz'}
        Issues: {len(sut_analysis.get('issues', []))} problem
        Warnings: {len(sut_analysis.get('warnings', []))} uyarı
        """
        
        prompt = """
        Lütfen aşağıdaki reçeteyi değerlendir ve bir karar ver:

        ## RECETE BILGILERI
        Reçete No: """ + str(prescription_data.get('recete_no', 'N/A')) + """
        Hasta: """ + str(prescription_data.get('hasta_ad', '')) + " " + str(prescription_data.get('hasta_soyad', '')) + """
        TC: """ + str(prescription_data.get('hasta_tc', 'N/A')) + """
        Reçete Tarihi: """ + str(prescription_data.get('recete_tarihi', 'N/A')) + """
        
        ## ILACLAR
        """ + drugs_text + """
        
        ## TANI KODLARI (ICD)
        """ + diagnosis_text + """
        
        ## ILAC MESAJLARI
        """ + str(prescription_data.get('ilac_mesajlari', 'Mesaj yok')) + """
        
        ## RAPOR BILGILERI
        Rapor No: """ + str(prescription_data.get('rapor_no', 'N/A')) + """
        Rapor Tarihi: """ + str(prescription_data.get('rapor_tarihi', 'N/A')) + """
        
        ## SUT ANALIZ OZETI
        """ + sut_summary + """
        
        ## TALIMAT
        Sen uzman bir eczane müdürüsün. Bu reçeteyi SGK SUT kurallarına göre değerlendir.
        
        Özellikle kontrol et:
        1. İlaç-tanı uyumluluğu (ICD kodları ile ilaçlar eşleşiyor mu?)
        2. Rapor gereklilikleri (Raporlu ilaçlar için rapor var mı?)
        3. İlaç mesaj kodları (1013, 1301, 1038, 1002 kodları doğru mu?)
        4. Dozaj ve süre limitleri
        5. Hasta güvenliği (etkileşimler, kontrendikasyonlar)
        
        ## KARAR SECENEKLERI
        - approve: Reçete tamamen uygun, onaylanabilir
        - reject: Ciddi sorunlar var, kesinlikle reddedilmeli
        - hold: Belirsizlikler var, manuel inceleme gerekli
        
        Yanıtını JSON formatında ver:
        {
            "action": "approve/reject/hold",
            "confidence": 0.0-1.0,
            "reason": "Kararının detaylı gerekçesi",
            "clinical_assessment": "Klinik değerlendirme",
            "sut_compliance": "SUT uyumluluğu değerlendirmesi", 
            "risk_factors": ["Risk faktörleri listesi"],
            "recommendations": ["Öneriler listesi"],
            "key_findings": ["Önemli bulgular"]
        }
        """
        
        return prompt
    
    def _call_claude_api(self, prompt):
        """Claude API çağrısı yapar"""
        try:
            logger.info("Calling Claude API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Newer anthropic library format
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content[0])
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _combine_analyses(self, sut_recommendation, claude_response, prescription_data):
        """SUT ve Claude analizlerini birleştirir"""
        try:
            # Claude yanıtından JSON çıkar
            claude_data = self._parse_claude_response(claude_response)
            
            # Kararları karşılaştır
            sut_action = sut_recommendation.get("action", "hold")
            claude_action = claude_data.get("action", "hold")
            
            # Nihai karar stratejisi
            final_action = self._determine_final_action(sut_action, claude_action)
            
            # Confidence hesapla
            sut_confidence = sut_recommendation.get("confidence", 0.5)
            claude_confidence = claude_data.get("confidence", 0.5)
            final_confidence = min(sut_confidence, claude_confidence)  # Konservatif yaklaşım
            
            # Gerekçeleri birleştir
            combined_reason = f"SUT: {sut_recommendation.get('reason', '')} | Claude: {claude_data.get('reason', '')}"
            
            return {
                "action": final_action,
                "confidence": final_confidence,
                "reason": combined_reason,
                "clinical_assessment": claude_data.get("clinical_assessment", ""),
                "sut_compliance": claude_data.get("sut_compliance", ""),
                "risk_factors": claude_data.get("risk_factors", []),
                "recommendations": claude_data.get("recommendations", []),
                "key_findings": claude_data.get("key_findings", []),
                "analysis_details": {
                    "sut_recommendation": sut_recommendation,
                    "claude_analysis": claude_data,
                    "decision_logic": f"SUT: {sut_action}, Claude: {claude_action} -> Final: {final_action}"
                },
                "analysis_method": "sut_plus_claude",
                "timestamp": datetime.now().isoformat(),
                "prescription_id": prescription_data.get("recete_no", ""),
                "claude_available": True
            }
            
        except Exception as e:
            logger.error(f"Analysis combination error: {e}")
            # Hata durumunda SUT sonucunu kullan
            return {
                **sut_recommendation,
                "analysis_method": "sut_fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_claude_response(self, response_text):
        """Claude yanıtını parse eder"""
        try:
            # JSON kısmını bul
            import re
            json_match = re.search(r'```json\\s*({.*?})\\s*```', response_text, re.DOTALL)
            
            if not json_match:
                # Alternatif format dene
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1) if '```' in response_text else json_match.group(0)
                return json.loads(json_str)
            
            else:
                # JSON bulunamadı, text analiz et
                return self._extract_decision_from_text(response_text)
                
        except Exception as e:
            logger.error(f"Claude response parsing error: {e}")
            return {
                "action": "hold",
                "confidence": 0.3,
                "reason": "Claude yanıtı parse edilemedi",
                "error": str(e)
            }
    
    def _extract_decision_from_text(self, text):
        """Text'ten karar çıkarmaya çalışır"""
        text_lower = text.lower()
        
        # Karar kelimelerini ara
        if "approve" in text_lower or "onay" in text_lower:
            action = "approve"
            confidence = 0.7
        elif "reject" in text_lower or "red" in text_lower:
            action = "reject" 
            confidence = 0.7
        else:
            action = "hold"
            confidence = 0.5
        
        return {
            "action": action,
            "confidence": confidence,
            "reason": f"Text-based analysis: {text[:200]}...",
            "full_response": text
        }
    
    def _determine_final_action(self, sut_action, claude_action):
        """İki analiz sonucunu birleştirerek nihai karar verir"""
        
        # Güvenlik öncelikli karar matrisi
        decision_matrix = {
            ("approve", "approve"): "approve",
            ("approve", "hold"): "hold",      # Konservatif
            ("approve", "reject"): "hold",    # Çelişki -> Manuel inceleme
            ("hold", "approve"): "hold",      # SUT problemi var
            ("hold", "hold"): "hold",
            ("hold", "reject"): "reject",
            ("reject", "approve"): "hold",    # Çelişki -> Manuel inceleme 
            ("reject", "hold"): "reject",
            ("reject", "reject"): "reject"
        }
        
        return decision_matrix.get((sut_action, claude_action), "hold")
    
    def analyze_batch_prescriptions(self, prescription_file_path):
        """Toplu reçete analizi yapar"""
        try:
            # JSON dosyasını oku
            with open(prescription_file_path, 'r', encoding='utf-8') as f:
                prescriptions = json.load(f)
            
            logger.info(f"Starting batch analysis of {len(prescriptions)} prescriptions")
            
            results = []
            for i, prescription in enumerate(prescriptions, 1):
                logger.info(f"Analyzing prescription {i}/{len(prescriptions)}: {prescription.get('recete_no', 'N/A')}")
                
                result = self.analyze_prescription_with_claude(prescription)
                results.append(result)
                
                # Progress
                print(f"[{i}/{len(prescriptions)}] {prescription.get('recete_no', 'N/A')} -> {result['action'].upper()}")
            
            # Sonuçları kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"prescription_analysis_results_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Özet istatistik
            self._print_analysis_summary(results)
            
            logger.info(f"Batch analysis completed. Results saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Batch analysis error: {e}")
            return None
    
    def _print_analysis_summary(self, results):
        """Analiz özetini yazdırır"""
        if not results:
            return
        
        total = len(results)
        approved = len([r for r in results if r['action'] == 'approve'])
        rejected = len([r for r in results if r['action'] == 'reject'])
        held = len([r for r in results if r['action'] == 'hold'])
        
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total
        
        print(f"""
        
=== ANALIZ OZETI ===
Toplam Recete: {total}
[+] Onaylanan: {approved} (%{approved/total*100:.1f})
[-] Reddedilen: {rejected} (%{rejected/total*100:.1f})
[?] Bekletilen: {held} (%{held/total*100:.1f})

Ortalama Guven: {avg_confidence:.2f}
Claude Kullanim: {"YES" if self.claude_enabled else "NO"}
        """)
        
        # En riskli reçeteler
        risky_prescriptions = [r for r in results if r['action'] in ['reject', 'hold']]
        if risky_prescriptions:
            print("\\n=== RISKLI RECETELER ===")
            for risk in risky_prescriptions[:3]:  # İlk 3 tanesi
                print(f"- {risk['prescription_id']}: {risk['action'].upper()} - {risk['reason'][:100]}...")

def test_claude_analyzer():
    """Claude analyzer test fonksiyonu"""
    analyzer = ClaudePrescriptionAnalyzer()
    
    # Manuel detailed prescriptions dosyasını analiz et
    prescription_file = "manual_detailed_prescriptions.json"
    
    if os.path.exists(prescription_file):
        print("=== CLAUDE PRESCRIPTION ANALYZER TEST ===\\n")
        output_file = analyzer.analyze_batch_prescriptions(prescription_file)
        
        if output_file:
            print(f"\\nAnaliz tamamlandı! Sonuç dosyası: {output_file}")
        else:
            print("\\nAnaliz başarısız!")
    else:
        print(f"Test dosyası bulunamadı: {prescription_file}")

if __name__ == "__main__":
    test_claude_analyzer()