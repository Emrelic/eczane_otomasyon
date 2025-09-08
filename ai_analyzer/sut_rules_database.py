"""
SUT (Sağlık Uygulama Tebliği) Kuralları Veritabanı
Reçete analizi için kritik kuralları içerir
"""

import json
from datetime import datetime
from loguru import logger

class SUTRulesDatabase:
    """SUT kuralları ve ilaç-tanı eşleştirmelerini yöneten sınıf"""
    
    def __init__(self):
        self.rules = self._load_sut_rules()
        self.drug_diagnosis_mapping = self._load_drug_diagnosis_mapping()
        self.message_codes = self._load_message_codes()
        logger.info("SUT Kuralları veritabanı yüklendi")
    
    def _load_sut_rules(self):
        """Temel SUT kurallarını yükler"""
        return {
            "general_rules": {
                "max_prescription_age_days": 30,
                "max_total_amount": 5000,
                "require_doctor_signature": True,
                "require_patient_tc": True
            },
            "age_restrictions": {
                "pediatric_max_age": 18,
                "geriatric_min_age": 65,
                "special_monitoring_required": ["morphine", "codeine", "tramadol"]
            },
            "dosage_limits": {
                "daily_max": {
                    "paracetamol": 4000,  # mg
                    "ibuprofen": 2400,    # mg
                    "diclofenac": 150,    # mg
                    "morphine": 30        # mg
                }
            },
            "report_requirements": {
                "chronic_hepatitis_b": {
                    "required": True,
                    "icd_codes": ["B18.1", "06.01"],
                    "max_duration_months": 12,
                    "required_drugs": ["TENOFOVIR", "ENTECAVIR"]
                },
                "diabetes": {
                    "required": True,
                    "icd_codes": ["E11", "E10"],
                    "max_duration_months": 6,
                    "required_drugs": ["METFORMIN", "INSULIN"]
                },
                "hypertension": {
                    "required": False,
                    "icd_codes": ["I10", "I15"],
                    "drugs": ["ACE", "ARB", "BETA_BLOCKER"]
                },
                "psychiatric": {
                    "required": True,
                    "icd_codes": ["F20", "F25", "F31"],
                    "max_duration_months": 3,
                    "required_drugs": ["ANTIPSYCHOTIC", "MOOD_STABILIZER"]
                }
            }
        }
    
    def _load_drug_diagnosis_mapping(self):
        """İlaç-tanı eşleştirmelerini yükler"""
        return {
            # Kronik Hepatit B
            "VEMLIDY": {
                "active_ingredient": "TENOFOVIR ALAFENAMID",
                "required_diagnosis": ["B18.1", "06.01"],
                "category": "antiviral",
                "report_required": True,
                "message_codes": ["1013"],
                "max_duration_months": 12,
                "monitoring_required": ["liver_function", "kidney_function"]
            },
            "BARACLUDE": {
                "active_ingredient": "ENTECAVIR",
                "required_diagnosis": ["B18.1", "06.01"],
                "category": "antiviral",
                "report_required": True,
                "message_codes": ["1013"],
                "max_duration_months": 12
            },
            
            # Prostat büyümesi
            "XALFU": {
                "active_ingredient": "ALFUZOSIN",
                "required_diagnosis": ["N40", "N42"],
                "category": "alpha_blocker",
                "report_required": False,
                "message_codes": ["1301"],
                "contraindications": ["hypotension"]
            },
            
            # Diyabet
            "GLIFIX": {
                "active_ingredient": "PIOGLITAZONE",
                "required_diagnosis": ["E11", "E10"],
                "category": "antidiabetic",
                "report_required": True,
                "message_codes": ["1038"],
                "contraindications": ["heart_failure", "bladder_cancer"]
            },
            
            # Antipsikotik
            "RISPERDAL": {
                "active_ingredient": "RISPERIDONE",
                "required_diagnosis": ["F20", "F25", "F31"],
                "category": "antipsychotic",
                "report_required": True,
                "message_codes": ["1002"],
                "max_duration_months": 3,
                "monitoring_required": ["movement_disorders", "metabolic_syndrome"]
            },
            "SOLIAN": {
                "active_ingredient": "AMISULPRIDE",
                "required_diagnosis": ["F20", "F25"],
                "category": "antipsychotic",
                "report_required": True,
                "message_codes": ["1002"],
                "contraindications": ["prolactinoma", "breast_cancer"]
            },
            
            # Proton pompası inhibitörü
            "NEXIUM": {
                "active_ingredient": "ESOMEPRAZOLE",
                "category": "ppi",
                "report_required": False,
                "max_duration_days": 56,
                "drug_interactions": ["clopidogrel", "warfarin"]
            },
            "PANTO": {
                "active_ingredient": "PANTOPRAZOLE", 
                "category": "ppi",
                "report_required": False,
                "max_duration_days": 56
            }
        }
    
    def _load_message_codes(self):
        """İlaç mesaj kodlarını yükler"""
        return {
            "1013": {
                "description": "Kronik Hepatit B tedavisi",
                "sut_section": "4.2.13.1",
                "report_required": True,
                "max_duration": "12 months",
                "monitoring": "3 monthly liver function tests"
            },
            "1301": {
                "description": "Prostat tedavisi - Alfuzosin grubu",
                "sut_section": "EK-4/E Madde 13",
                "report_required": False,
                "contraindications": ["severe_hypotension"]
            },
            "1038": {
                "description": "Diyabet tedavisi kuralları",
                "sut_section": "4.2.38",
                "report_required": True,
                "hba1c_requirement": ">7%",
                "combination_rules": "metformin_first_line"
            },
            "1002": {
                "description": "Antipsikotik kullanım ilkeleri",
                "sut_section": "4.2.2",
                "report_required": True,
                "max_duration": "3 months",
                "renewal_criteria": "clinical_improvement"
            }
        }
    
    def get_drug_requirements(self, drug_name):
        """İlaç gereksinimlerini döndürür"""
        drug_name_clean = drug_name.upper().split()[0]  # İlk kelimeyi al
        
        if drug_name_clean in self.drug_diagnosis_mapping:
            return self.drug_diagnosis_mapping[drug_name_clean]
        
        # Partial match dene
        for drug_key in self.drug_diagnosis_mapping.keys():
            if drug_key in drug_name_clean or drug_name_clean in drug_key:
                return self.drug_diagnosis_mapping[drug_key]
        
        return None
    
    def check_drug_diagnosis_compatibility(self, drug_name, diagnosis_codes):
        """İlaç-tanı uyumluluğunu kontrol eder"""
        drug_req = self.get_drug_requirements(drug_name)
        
        if not drug_req:
            return {
                "compatible": "unknown",
                "reason": f"Drug {drug_name} not found in database"
            }
        
        if "required_diagnosis" not in drug_req:
            return {
                "compatible": True,
                "reason": "No specific diagnosis requirement"
            }
        
        required_diagnoses = drug_req["required_diagnosis"]
        
        # Tanı kodları eşleşmesini kontrol et
        for diagnosis in diagnosis_codes:
            if diagnosis in required_diagnoses:
                return {
                    "compatible": True,
                    "reason": f"Diagnosis {diagnosis} matches requirement",
                    "matched_diagnosis": diagnosis
                }
        
        return {
            "compatible": False,
            "reason": f"Required diagnoses {required_diagnoses} not found in {diagnosis_codes}",
            "required": required_diagnoses,
            "found": diagnosis_codes
        }
    
    def check_message_code_validity(self, message_code, drug_name):
        """Mesaj kodu geçerliliğini kontrol eder"""
        if message_code not in self.message_codes:
            return {
                "valid": False,
                "reason": f"Message code {message_code} not recognized"
            }
        
        drug_req = self.get_drug_requirements(drug_name)
        if drug_req and "message_codes" in drug_req:
            if message_code in drug_req["message_codes"]:
                return {
                    "valid": True,
                    "reason": "Message code matches drug requirement"
                }
            else:
                return {
                    "valid": False,
                    "reason": f"Message code {message_code} not expected for {drug_name}"
                }
        
        return {
            "valid": "unknown",
            "reason": "Drug requirements not found, cannot validate message code"
        }
    
    def get_sut_analysis_for_prescription(self, prescription_data):
        """Reçete için kapsamlı SUT analizi yapar"""
        analysis = {
            "prescription_id": prescription_data.get("recete_no", ""),
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_compliance": True,
            "issues": [],
            "warnings": [],
            "drug_analyses": []
        }
        
        drugs = prescription_data.get("drugs", [])
        diagnosis_codes = []
        
        # Rapor detaylarından tanı kodlarını çıkar
        if "report_details" in prescription_data:
            tani_bilgileri = prescription_data["report_details"].get("tani_bilgileri", [])
            for tani in tani_bilgileri:
                if isinstance(tani, dict) and "tani_kodu" in tani:
                    diagnosis_codes.append(tani["tani_kodu"])
                elif isinstance(tani, str):
                    diagnosis_codes.append(tani)
        
        # Her ilaç için analiz
        for drug in drugs:
            drug_name = drug.get("ilac_adi", "")
            drug_analysis = self._analyze_single_drug(drug, diagnosis_codes, prescription_data)
            analysis["drug_analyses"].append(drug_analysis)
            
            # Genel uyumluluğu güncelle
            if not drug_analysis.get("compliant", True):
                analysis["overall_compliance"] = False
                analysis["issues"].extend(drug_analysis.get("issues", []))
        
        # İlaç mesajları analizi
        message_analysis = self._analyze_message_codes(prescription_data)
        analysis["message_code_analysis"] = message_analysis
        
        # Genel SUT kuralları kontrolü
        general_check = self._check_general_sut_rules(prescription_data)
        analysis["general_compliance"] = general_check
        
        return analysis
    
    def _analyze_single_drug(self, drug, diagnosis_codes, prescription_data):
        """Tek bir ilacın SUT uyumluluğunu analiz eder"""
        drug_name = drug.get("ilac_adi", "")
        analysis = {
            "drug_name": drug_name,
            "compliant": True,
            "issues": [],
            "warnings": []
        }
        
        # İlaç gereksinimlerini kontrol et
        drug_req = self.get_drug_requirements(drug_name)
        
        if drug_req:
            # Tanı uyumluluğu
            if "required_diagnosis" in drug_req:
                compatibility = self.check_drug_diagnosis_compatibility(drug_name, diagnosis_codes)
                if not compatibility.get("compatible", True):
                    analysis["compliant"] = False
                    analysis["issues"].append(f"Diagnosis mismatch: {compatibility['reason']}")
            
            # Rapor gerekliliği
            if drug_req.get("report_required", False):
                if not prescription_data.get("report_details", {}).get("rapor_numarasi"):
                    analysis["compliant"] = False
                    analysis["issues"].append(f"Report required for {drug_name} but not found")
            
            # Kontrendikasyonlar
            if "contraindications" in drug_req:
                analysis["warnings"].append(f"Check contraindications: {drug_req['contraindications']}")
        
        else:
            analysis["warnings"].append(f"Drug {drug_name} not found in SUT database")
        
        return analysis
    
    def _analyze_message_codes(self, prescription_data):
        """İlaç mesaj kodlarını analiz eder"""
        message_analysis = {
            "valid_codes": [],
            "invalid_codes": [],
            "missing_codes": []
        }
        
        # Mevcut mesaj kodlarını çıkar
        message_text = prescription_data.get("ilac_mesajlari", "")
        found_codes = []
        
        for code in self.message_codes.keys():
            if code in message_text:
                found_codes.append(code)
                message_analysis["valid_codes"].append(code)
        
        # Her ilaç için gerekli mesaj kodlarını kontrol et
        drugs = prescription_data.get("drugs", [])
        for drug in drugs:
            drug_name = drug.get("ilac_adi", "")
            drug_req = self.get_drug_requirements(drug_name)
            
            if drug_req and "message_codes" in drug_req:
                for required_code in drug_req["message_codes"]:
                    if required_code not in found_codes:
                        message_analysis["missing_codes"].append({
                            "drug": drug_name,
                            "missing_code": required_code
                        })
        
        return message_analysis
    
    def _check_general_sut_rules(self, prescription_data):
        """Genel SUT kurallarını kontrol eder"""
        compliance = {
            "compliant": True,
            "issues": []
        }
        
        # TC kimlik kontrolü
        if not prescription_data.get("hasta_tc"):
            compliance["compliant"] = False
            compliance["issues"].append("Patient TC number missing")
        
        # Reçete tarihi kontrolü
        prescription_date = prescription_data.get("recete_tarihi")
        if prescription_date:
            try:
                # Tarih formatını parse et (örn: "22/05/2025")
                date_parts = prescription_date.split("/")
                if len(date_parts) == 3:
                    day, month, year = date_parts
                    prescription_datetime = datetime(int(year), int(month), int(day))
                    
                    # 30 günden eski mi?
                    age_days = (datetime.now() - prescription_datetime).days
                    if age_days > self.rules["general_rules"]["max_prescription_age_days"]:
                        compliance["issues"].append(f"Prescription too old: {age_days} days")
            except:
                compliance["issues"].append("Invalid prescription date format")
        
        return compliance
    
    def get_recommendation_for_prescription(self, prescription_data):
        """Reçete için öneri döndürür"""
        analysis = self.get_sut_analysis_for_prescription(prescription_data)
        
        if analysis["overall_compliance"]:
            if not analysis.get("warnings", []):
                return {
                    "action": "approve",
                    "confidence": 0.95,
                    "reason": "Full SUT compliance, no issues found"
                }
            else:
                return {
                    "action": "approve",
                    "confidence": 0.8,
                    "reason": "SUT compliant with minor warnings",
                    "warnings": analysis["warnings"]
                }
        else:
            critical_issues = len(analysis["issues"])
            if critical_issues >= 3:
                return {
                    "action": "reject",
                    "confidence": 0.9,
                    "reason": f"Multiple SUT violations ({critical_issues} issues)",
                    "issues": analysis["issues"]
                }
            else:
                return {
                    "action": "hold",
                    "confidence": 0.6,
                    "reason": "SUT compliance issues require manual review",
                    "issues": analysis["issues"]
                }

# Test fonksiyonu
def test_sut_database():
    """SUT veritabanını test eder"""
    sut_db = SUTRulesDatabase()
    
    # Test verisi (gerçek reçete)
    test_prescription = {
        "recete_no": "3GP25RF",
        "hasta_tc": "11916110202",
        "drugs": [
            {"ilac_adi": "PANTO 40 MG.28 TABLET"},
            {"ilac_adi": "VEMLIDY 25MG 30 FILM KAPLI TABLET"}
        ],
        "ilac_mesajlari": "1013(1) - 4.2.13.1 Kronik Hepatit B tedavisi",
        "report_details": {
            "rapor_numarasi": "1992805",
            "tani_bilgileri": [{"tani_kodu": "B18.1"}]
        }
    }
    
    analysis = sut_db.get_sut_analysis_for_prescription(test_prescription)
    recommendation = sut_db.get_recommendation_for_prescription(test_prescription)
    
    print("=== SUT DATABASE TEST ===")
    print(f"Analysis: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
    print(f"Recommendation: {json.dumps(recommendation, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_sut_database()