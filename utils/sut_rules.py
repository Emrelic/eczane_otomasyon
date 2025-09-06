"""
SUT (Sağlık Uygulama Tebliği) Kuralları
İlaç-tanı uyumluluğu ve SUT kuralları kontrolleri
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class SUTRules:
    """SUT kuralları sınıfı"""
    
    def __init__(self):
        self.rules_cache = {}
        self.load_basic_rules()
    
    def load_basic_rules(self):
        """Temel SUT kurallarını yükler"""
        self.rules_cache = {
            # Yaş sınırlamaları
            "age_restrictions": {
                "pediatric_only": ["J07*", "J05AX*"],  # Aşılar, çocuk antiviralleri
                "adult_only": ["G04CA*", "C02*"],      # Prostat ilaçları, antihipertansifler
                "elderly_caution": ["N05*", "N06*"]    # Psikotropik ilaçlar
            },
            
            # Dozaj sınırları (günlük maksimum)
            "dosage_limits": {
                "N02BE01": {"max_daily": 4000, "unit": "mg"},  # Paracetamol
                "M01AE01": {"max_daily": 1200, "unit": "mg"},  # Ibuprofen
                "A02BC01": {"max_daily": 40, "unit": "mg"},    # Omeprazol
                "C09AA01": {"max_daily": 10, "unit": "mg"}     # Enalapril
            },
            
            # İlaç etkileşimleri (major)
            "drug_interactions": {
                "warfarin": ["aspirin", "ibuprofen", "ciprofloxacin"],
                "metformin": ["contrast_agents", "alcohol"],
                "digoxin": ["quinidine", "verapamil", "amiodarone"]
            },
            
            # Tanı-ilaç uyumluluğu
            "diagnosis_drug_compatibility": {
                "I10": ["C09AA*", "C08CA*", "C07AB*"],     # Hipertansiyon
                "E11": ["A10BA*", "A10BB*", "A10BH*"],     # Tip 2 DM
                "J44": ["R03AC*", "R03BA*", "R03BB*"],     # KOAH
                "K25": ["A02BC*", "A02BA*", "H02AB*"],     # Peptik ülser
                "F32": ["N06AB*", "N06AX*", "N05BA*"]      # Depresyon
            },
            
            # Kontrendikasyonlar
            "contraindications": {
                "pregnancy": ["C03*", "C09*", "C08*"],     # Gebelikte yasak
                "kidney_failure": ["A10BA02", "M01AE*"],   # Böbrek yetmezliğinde yasak
                "liver_failure": ["N02BE01", "A02BC*"]     # Karaciğer yetmezliğinde dikkat
            },
            
            # Özel durumlar
            "special_conditions": {
                "requires_monitoring": ["warfarin", "digoxin", "lithium"],
                "generic_mandatory": ["A10BA02", "C01DA14"],  # Jenerik kullanım zorunlu
                "prescription_limit": {"N02AA01": 30}         # Morfin gibi opioidler
            }
        }
        
        logger.info("Temel SUT kuralları yüklendi")
    
    def check_diagnosis_drug_compatibility(self, diagnosis_code: str, drug_codes: List[str]) -> Dict[str, Any]:
        """
        Tanı-ilaç uyumluluğunu kontrol eder
        
        Args:
            diagnosis_code: ICD-10 tanı kodu
            drug_codes: ATC ilaç kodları listesi
            
        Returns:
            Dict: Uyumluluk sonucu
        """
        result = {
            "compatible": [],
            "incompatible": [],
            "warnings": [],
            "score": 0.0
        }
        
        try:
            # Tanı kodu için uygun ilaçları bul
            compatible_drugs = self.rules_cache["diagnosis_drug_compatibility"].get(diagnosis_code, [])
            
            for drug_code in drug_codes:
                is_compatible = False
                
                for compatible_pattern in compatible_drugs:
                    if self._match_atc_pattern(drug_code, compatible_pattern):
                        is_compatible = True
                        result["compatible"].append(drug_code)
                        break
                
                if not is_compatible:
                    result["incompatible"].append(drug_code)
                    result["warnings"].append(
                        f"İlaç {drug_code} tanı {diagnosis_code} ile uyumlu görünmüyor"
                    )
            
            # Uyumluluk skorunu hesapla
            total_drugs = len(drug_codes)
            compatible_count = len(result["compatible"])
            
            if total_drugs > 0:
                result["score"] = compatible_count / total_drugs
            
            return result
            
        except Exception as e:
            logger.error(f"Tanı-ilaç uyumluluk kontrolü hatası: {e}")
            result["warnings"].append(f"Kontrol hatası: {e}")
            return result
    
    def check_age_restrictions(self, patient_age: int, drug_codes: List[str]) -> Dict[str, Any]:
        """
        Yaş kısıtlamalarını kontrol eder
        
        Args:
            patient_age: Hasta yaşı
            drug_codes: İlaç kodları
            
        Returns:
            Dict: Yaş uyumluluk sonucu
        """
        result = {
            "appropriate": [],
            "inappropriate": [],
            "warnings": [],
            "score": 1.0
        }
        
        try:
            age_rules = self.rules_cache["age_restrictions"]
            
            for drug_code in drug_codes:
                warnings = []
                
                # Çocuk ilaçları kontrolü
                if patient_age >= 18:
                    for pediatric_pattern in age_rules["pediatric_only"]:
                        if self._match_atc_pattern(drug_code, pediatric_pattern):
                            warnings.append(f"{drug_code} çocuk ilacı, yetişkin hastada dikkatli kullanım")
                
                # Yetişkin ilaçları kontrolü
                if patient_age < 18:
                    for adult_pattern in age_rules["adult_only"]:
                        if self._match_atc_pattern(drug_code, adult_pattern):
                            warnings.append(f"{drug_code} yetişkin ilacı, çocukta kontrendike")
                            result["inappropriate"].append(drug_code)
                            continue
                
                # Yaşlı hastalar için dikkat
                if patient_age >= 65:
                    for elderly_pattern in age_rules["elderly_caution"]:
                        if self._match_atc_pattern(drug_code, elderly_pattern):
                            warnings.append(f"{drug_code} yaşlı hastada dikkatli kullanım gerekli")
                
                if drug_code not in result["inappropriate"]:
                    result["appropriate"].append(drug_code)
                
                result["warnings"].extend(warnings)
            
            # Skor hesaplama
            total_drugs = len(drug_codes)
            appropriate_count = len(result["appropriate"])
            
            if total_drugs > 0:
                result["score"] = appropriate_count / total_drugs
            
            return result
            
        except Exception as e:
            logger.error(f"Yaş kısıtlama kontrolü hatası: {e}")
            result["warnings"].append(f"Kontrol hatası: {e}")
            return result
    
    def check_drug_interactions(self, drug_codes: List[str]) -> Dict[str, Any]:
        """
        İlaç etkileşimlerini kontrol eder
        
        Args:
            drug_codes: İlaç kodları
            
        Returns:
            Dict: Etkileşim sonucu
        """
        result = {
            "interactions": [],
            "warnings": [],
            "severity": "low",
            "score": 1.0
        }
        
        try:
            interactions = self.rules_cache["drug_interactions"]
            found_interactions = []
            
            for drug1 in drug_codes:
                drug1_name = self._get_drug_name(drug1)
                
                if drug1_name in interactions:
                    interacting_drugs = interactions[drug1_name]
                    
                    for drug2 in drug_codes:
                        if drug1 != drug2:
                            drug2_name = self._get_drug_name(drug2)
                            
                            if drug2_name in interacting_drugs:
                                interaction = {
                                    "drug1": drug1,
                                    "drug2": drug2,
                                    "severity": "major",
                                    "description": f"{drug1_name} ile {drug2_name} arasında etkileşim"
                                }
                                found_interactions.append(interaction)
                                
                                result["warnings"].append(
                                    f"MAJÖR ETKİLEŞİM: {drug1_name} + {drug2_name}"
                                )
            
            result["interactions"] = found_interactions
            
            if found_interactions:
                result["severity"] = "major"
                result["score"] = 0.0 if any(i["severity"] == "major" for i in found_interactions) else 0.5
            
            return result
            
        except Exception as e:
            logger.error(f"İlaç etkileşim kontrolü hatası: {e}")
            result["warnings"].append(f"Kontrol hatası: {e}")
            return result
    
    def check_dosage_limits(self, drug_dosages: Dict[str, float]) -> Dict[str, Any]:
        """
        Dozaj sınırlarını kontrol eder
        
        Args:
            drug_dosages: İlaç kodları ve günlük dozları
            
        Returns:
            Dict: Dozaj kontrol sonucu
        """
        result = {
            "within_limits": [],
            "exceeds_limits": [],
            "warnings": [],
            "score": 1.0
        }
        
        try:
            limits = self.rules_cache["dosage_limits"]
            
            for drug_code, daily_dose in drug_dosages.items():
                if drug_code in limits:
                    max_dose = limits[drug_code]["max_daily"]
                    unit = limits[drug_code]["unit"]
                    
                    if daily_dose > max_dose:
                        result["exceeds_limits"].append({
                            "drug": drug_code,
                            "prescribed": daily_dose,
                            "max_allowed": max_dose,
                            "unit": unit
                        })
                        result["warnings"].append(
                            f"{drug_code} günlük dozajı limit aşıyor: {daily_dose}{unit} > {max_dose}{unit}"
                        )
                    else:
                        result["within_limits"].append(drug_code)
                else:
                    result["within_limits"].append(drug_code)
            
            # Skor hesaplama
            total_drugs = len(drug_dosages)
            within_limits_count = len(result["within_limits"])
            
            if total_drugs > 0:
                result["score"] = within_limits_count / total_drugs
            
            return result
            
        except Exception as e:
            logger.error(f"Dozaj kontrol hatası: {e}")
            result["warnings"].append(f"Kontrol hatası: {e}")
            return result
    
    def check_contraindications(self, patient_conditions: List[str], drug_codes: List[str]) -> Dict[str, Any]:
        """
        Kontrendikasyonları kontrol eder
        
        Args:
            patient_conditions: Hasta durumları (pregnancy, kidney_failure, vb.)
            drug_codes: İlaç kodları
            
        Returns:
            Dict: Kontrendikasyon sonucu
        """
        result = {
            "safe": [],
            "contraindicated": [],
            "warnings": [],
            "score": 1.0
        }
        
        try:
            contraindications = self.rules_cache["contraindications"]
            
            for condition in patient_conditions:
                if condition in contraindications:
                    restricted_patterns = contraindications[condition]
                    
                    for drug_code in drug_codes:
                        is_contraindicated = False
                        
                        for pattern in restricted_patterns:
                            if self._match_atc_pattern(drug_code, pattern):
                                result["contraindicated"].append({
                                    "drug": drug_code,
                                    "condition": condition,
                                    "reason": f"{drug_code} {condition} durumunda kontrendike"
                                })
                                result["warnings"].append(
                                    f"KONTRENDİKE: {drug_code} {condition} hastalarında kullanılamaz"
                                )
                                is_contraindicated = True
                                break
                        
                        if not is_contraindicated and drug_code not in result["safe"]:
                            result["safe"].append(drug_code)
            
            # Hiç durum yoksa tüm ilaçları güvenli kabul et
            if not patient_conditions:
                result["safe"] = drug_codes
            
            # Skor hesaplama
            total_drugs = len(drug_codes)
            contraindicated_count = len(set(item["drug"] for item in result["contraindicated"]))
            
            if total_drugs > 0:
                result["score"] = (total_drugs - contraindicated_count) / total_drugs
            
            return result
            
        except Exception as e:
            logger.error(f"Kontrendikasyon kontrolü hatası: {e}")
            result["warnings"].append(f"Kontrol hatası: {e}")
            return result
    
    def comprehensive_check(self, prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kapsamlı SUT kuralı kontrolü
        
        Args:
            prescription_data: Reçete verileri
            
        Returns:
            Dict: Kapsamlı kontrol sonucu
        """
        result = {
            "overall_score": 0.0,
            "overall_status": "unknown",
            "checks": {},
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Veri çıkarma
            diagnosis_code = prescription_data.get("diagnosis_code", "")
            drug_codes = prescription_data.get("drug_codes", [])
            patient_age = prescription_data.get("patient_age", 0)
            patient_conditions = prescription_data.get("patient_conditions", [])
            drug_dosages = prescription_data.get("drug_dosages", {})
            
            # Tüm kontrolleri çalıştır
            checks_to_run = [
                ("diagnosis_compatibility", 
                 lambda: self.check_diagnosis_drug_compatibility(diagnosis_code, drug_codes)),
                ("age_restrictions", 
                 lambda: self.check_age_restrictions(patient_age, drug_codes)),
                ("drug_interactions", 
                 lambda: self.check_drug_interactions(drug_codes)),
                ("dosage_limits", 
                 lambda: self.check_dosage_limits(drug_dosages)),
                ("contraindications", 
                 lambda: self.check_contraindications(patient_conditions, drug_codes))
            ]
            
            scores = []
            all_warnings = []
            
            for check_name, check_func in checks_to_run:
                try:
                    check_result = check_func()
                    result["checks"][check_name] = check_result
                    scores.append(check_result["score"])
                    all_warnings.extend(check_result.get("warnings", []))
                except Exception as e:
                    logger.error(f"{check_name} kontrolü hatası: {e}")
                    result["checks"][check_name] = {"score": 0.5, "warnings": [str(e)]}
                    scores.append(0.5)
            
            # Genel skor hesaplama (ağırlıklı ortalama)
            weights = [0.3, 0.2, 0.25, 0.15, 0.1]  # Tanı uyumu en önemli
            result["overall_score"] = sum(s * w for s, w in zip(scores, weights))
            
            # Genel durum belirleme
            if result["overall_score"] >= 0.8:
                result["overall_status"] = "approved"
                result["recommendations"].append("Reçete SUT kurallarına uygun, onaylanabilir")
            elif result["overall_score"] >= 0.6:
                result["overall_status"] = "conditional"
                result["recommendations"].append("Bazı uyarılar var, dikkatli değerlendirme gerekli")
            else:
                result["overall_status"] = "rejected"
                result["recommendations"].append("Ciddi SUT ihlalleri var, reçete reddedilmeli")
            
            # Uyarıları ekle
            result["warnings"] = all_warnings
            
            # Öneriler ekle
            if result["checks"].get("drug_interactions", {}).get("interactions"):
                result["recommendations"].append("İlaç etkileşimlerini gözden geçirin")
            
            if result["checks"].get("contraindications", {}).get("contraindicated"):
                result["recommendations"].append("Kontrendike ilaçları değiştirin")
            
            return result
            
        except Exception as e:
            logger.error(f"Kapsamlı SUT kontrolü hatası: {e}")
            result["warnings"].append(f"Genel kontrol hatası: {e}")
            result["overall_score"] = 0.0
            result["overall_status"] = "error"
            return result
    
    def _match_atc_pattern(self, drug_code: str, pattern: str) -> bool:
        """ATC kod deseni eşleştirme"""
        if "*" in pattern:
            # Wildcard desteği
            regex_pattern = pattern.replace("*", ".*")
            return bool(re.match(regex_pattern, drug_code))
        else:
            return drug_code == pattern
    
    def _get_drug_name(self, drug_code: str) -> str:
        """İlaç kodundan ilaç adını çıkarır (basit mapping)"""
        # Bu gerçek bir sistemde veritabanından gelecek
        drug_names = {
            "warfarin": "warfarin",
            "aspirin": "aspirin", 
            "ibuprofen": "ibuprofen",
            "metformin": "metformin",
            "digoxin": "digoxin"
        }
        
        # ATC kodundan basit çıkarım
        for name, code in drug_names.items():
            if name.lower() in drug_code.lower():
                return name
        
        return drug_code.lower()


# Yardımcı fonksiyonlar
def create_sut_checker():
    """SUT kontrol nesnesi oluşturur"""
    return SUTRules()


def validate_prescription_sut(prescription_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reçete SUT uyumluluğunu doğrular
    
    Args:
        prescription_data: Reçete verileri
        
    Returns:
        Dict: Doğrulama sonucu
    """
    sut_checker = create_sut_checker()
    return sut_checker.comprehensive_check(prescription_data)