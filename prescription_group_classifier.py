#!/usr/bin/env python3
"""
Prescription Group Classifier
Automatically classifies prescriptions into A, B, C, C_blood, or Geçici Koruma groups
Based on domain expert knowledge from 09 Eylül 2025
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

@dataclass
class PrescriptionGroup:
    """Prescription group classification result"""
    group_id: str
    group_name: str
    reason: str
    confidence: float
    details: List[str]

class PrescriptionGroupClassifier:
    """Classifies prescriptions into the correct groups"""
    
    def __init__(self):
        self.load_classification_rules()
        
    def load_classification_rules(self):
        """Load classification rules and keywords"""
        
        # Keywords that indicate report-required drugs (A Group)
        self.report_required_keywords = [
            'rapor', 'raporlu', 'özel rapor', 'yeşil rapor', 'kırmızı rapor',
            'uzman doktor', 'endikasyon', 'sut eki', 'ek 2', 'ek 3', 'ek 4',
            'biyoteknolojik', 'gen tedavi', 'onkoloji', 'immün', 'monoklonal',
            'interferon', 'antineoplastik', 'kemoterapötik', 'target tedavi'
        ]
        
        # Keywords for blood products (C_blood group)
        self.blood_product_keywords = [
            'kan ürünü', 'plazma', 'eritrosit', 'trombosit', 'albumin', 
            'immünoglobulin', 'faktör', 'koagülasyon', 'fibrinojen',
            'antitrombin', 'protein c', 'protein s', 'taze donmuş plazma',
            'kırmızı alyuvar', 'beyaz alyuvar', 'kan nakli'
        ]
        
        # Keywords for sequential distribution/quota limited drugs (C Group)
        self.sequential_distribution_keywords = [
            'sıralı dağıtım', 'kotalı', 'üst limit', 'aylık limit',
            'dozaj limiti', 'miktar kısıtı', 'özel dağıtım', 'kontrollü dağıtım',
            'sınırlı kullanım', 'merkez eczane', 'özel merkez'
        ]
        
        # Keywords for temporary protection (refugees)
        self.temporary_protection_keywords = [
            'geçici koruma', 'mülteci', 'sığınmacı', 'suriyeli', 
            'temporary protection', 'refugee', 'asylum', 'göçmen',
            'kimlik belgesi', '99', 'koruma statü'
        ]
        
    def classify_prescription(self, prescription_data: Dict) -> PrescriptionGroup:
        """
        Classify a prescription into the correct group
        
        Args:
            prescription_data: Dictionary containing prescription information
            
        Returns:
            PrescriptionGroup: Classification result
        """
        
        # Extract relevant text for analysis
        full_text = self._extract_text_for_analysis(prescription_data)
        
        # Check for temporary protection first (most specific)
        if self._is_temporary_protection(prescription_data, full_text):
            return PrescriptionGroup(
                group_id="temp_protection",
                group_name="Geçici Koruma",
                reason="Geçici koruma statüsü tespit edildi",
                confidence=0.95,
                details=["Mülteci/Suriyeli hasta", "Özel sosyal güvenlik"]
            )
            
        # Check for blood products (C_blood)
        if self._contains_blood_products(prescription_data, full_text):
            return PrescriptionGroup(
                group_id="C_blood",
                group_name="C Grubu - Kan Ürünleri",
                reason="Kan ürünü tespit edildi",
                confidence=0.90,
                details=["Sıralı dağıtım gerekli", "En hassas kategori"]
            )
            
        # Check for report-required drugs (A Group)
        # CRITICAL: Even ONE report-required drug makes entire prescription A Group
        if self._contains_report_required_drugs(prescription_data, full_text):
            return PrescriptionGroup(
                group_id="A",
                group_name="A Grubu - Raporlu İlaçlar",
                reason="Bir veya daha fazla raporlu ilaç tespit edildi",
                confidence=0.85,
                details=["Tek raporlu ilaç bile tüm reçeteyi A yapar", "Rapor kontrolü gerekli"]
            )
            
        # Check for sequential distribution/quota limited (C Group)
        if self._contains_sequential_distribution_drugs(prescription_data, full_text):
            return PrescriptionGroup(
                group_id="C",
                group_name="C Grubu - Sıralı Dağıtım",
                reason="Sıralı dağıtım/kotalı ilaç tespit edildi",
                confidence=0.80,
                details=["Özel dağıtım kuralları", "Kota kontrolü gerekli"]
            )
            
        # Default to B Group (normal drugs)
        return PrescriptionGroup(
            group_id="B",
            group_name="B Grubu - Normal İlaçlar",
            reason="Normal raporsuz ilaçlar",
            confidence=0.75,
            details=["Standart SGK ilaçları", "En yaygın grup"]
        )
        
    def _extract_text_for_analysis(self, prescription_data: Dict) -> str:
        """Extract all relevant text from prescription for analysis"""
        
        text_parts = []
        
        # Patient information
        if 'hasta_ad_soyad' in prescription_data:
            text_parts.append(prescription_data['hasta_ad_soyad'])
            
        # Drug information
        if 'drugs' in prescription_data:
            for drug in prescription_data['drugs']:
                if isinstance(drug, dict):
                    for key, value in drug.items():
                        if isinstance(value, str):
                            text_parts.append(value)
                elif isinstance(drug, str):
                    text_parts.append(drug)
                    
        # Drug details
        if 'drug_details' in prescription_data:
            details = prescription_data['drug_details']
            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                        
        # Drug messages
        if 'drug_messages' in prescription_data:
            for message in prescription_data['drug_messages']:
                if isinstance(message, str):
                    text_parts.append(message)
                elif isinstance(message, dict):
                    for key, value in message.items():
                        if isinstance(value, str):
                            text_parts.append(value)
                            
        # Report details
        if 'report_details' in prescription_data:
            report = prescription_data['report_details']
            if isinstance(report, dict):
                for key, value in report.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                text_parts.append(item)
        
        return ' '.join(text_parts).lower()
        
    def _is_temporary_protection(self, prescription_data: Dict, full_text: str) -> bool:
        """Check if prescription is for temporary protection status"""
        
        # Check TC ID pattern (temporary protection often starts with 99)
        tc_id = prescription_data.get('hasta_tc', '')
        if tc_id.startswith('99'):
            return True
            
        # Check for keywords
        for keyword in self.temporary_protection_keywords:
            if keyword in full_text:
                return True
                
        return False
        
    def _contains_blood_products(self, prescription_data: Dict, full_text: str) -> bool:
        """Check if prescription contains blood products"""
        
        for keyword in self.blood_product_keywords:
            if keyword in full_text:
                return True
                
        # Check specific drug codes or names that are blood products
        if 'drugs' in prescription_data:
            for drug in prescription_data['drugs']:
                drug_text = str(drug).lower()
                if any(blood_kw in drug_text for blood_kw in self.blood_product_keywords):
                    return True
                    
        return False
        
    def _contains_report_required_drugs(self, prescription_data: Dict, full_text: str) -> bool:
        """Check if prescription contains ANY report-required drugs"""
        
        # Check for report keywords in text
        for keyword in self.report_required_keywords:
            if keyword in full_text:
                return True
                
        # Check drug messages for report indicators
        if 'drug_messages' in prescription_data:
            for message in prescription_data['drug_messages']:
                message_text = str(message).lower()
                if 'rapor' in message_text or 'endikasyon' in message_text:
                    return True
                    
        # Check if there's report_details section (indicates reports exist)
        if 'report_details' in prescription_data:
            report_details = prescription_data['report_details']
            if report_details and len(str(report_details)) > 10:  # Non-empty report
                return True
                
        return False
        
    def _contains_sequential_distribution_drugs(self, prescription_data: Dict, full_text: str) -> bool:
        """Check if prescription contains sequential distribution drugs"""
        
        for keyword in self.sequential_distribution_keywords:
            if keyword in full_text:
                return True
                
        # Check drug messages for sequential distribution indicators
        if 'drug_messages' in prescription_data:
            for message in prescription_data['drug_messages']:
                message_text = str(message).lower()
                if any(seq_kw in message_text for seq_kw in self.sequential_distribution_keywords):
                    return True
                    
        return False
        
    def classify_batch_prescriptions(self, prescriptions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify multiple prescriptions and group them
        
        Args:
            prescriptions: List of prescription dictionaries
            
        Returns:
            Dictionary with group_id as keys and prescription lists as values
        """
        
        grouped_prescriptions = {
            "A": [],
            "B": [],
            "C": [],
            "C_blood": [],
            "temp_protection": []
        }
        
        classification_results = []
        
        for prescription in prescriptions:
            try:
                classification = self.classify_prescription(prescription)
                
                # Add prescription to appropriate group
                group_id = classification.group_id
                if group_id in grouped_prescriptions:
                    prescription['classification'] = {
                        'group_id': classification.group_id,
                        'group_name': classification.group_name,
                        'reason': classification.reason,
                        'confidence': classification.confidence,
                        'details': classification.details
                    }
                    grouped_prescriptions[group_id].append(prescription)
                    
                classification_results.append({
                    'prescription_id': prescription.get('recete_no', 'unknown'),
                    'patient': prescription.get('hasta_ad_soyad', 'unknown'),
                    'classification': classification
                })
                
            except Exception as e:
                print(f"Classification error for prescription: {e}")
                # Default to B group on error
                prescription['classification'] = {
                    'group_id': 'B',
                    'group_name': 'B Grubu - Normal İlaçlar',
                    'reason': f'Classification error: {e}',
                    'confidence': 0.5,
                    'details': ['Error in classification']
                }
                grouped_prescriptions['B'].append(prescription)
                
        return grouped_prescriptions, classification_results
        
    def get_group_statistics(self, grouped_prescriptions: Dict[str, List[Dict]]) -> Dict:
        """Get statistics about grouped prescriptions"""
        
        total_prescriptions = sum(len(group) for group in grouped_prescriptions.values())
        
        stats = {
            'total_prescriptions': total_prescriptions,
            'group_counts': {
                group_id: len(prescriptions)
                for group_id, prescriptions in grouped_prescriptions.items()
            },
            'group_percentages': {}
        }
        
        # Calculate percentages
        if total_prescriptions > 0:
            for group_id, count in stats['group_counts'].items():
                percentage = (count / total_prescriptions) * 100
                stats['group_percentages'][group_id] = round(percentage, 2)
                
        return stats

def test_prescription_classifier():
    """Test the prescription classifier"""
    
    # Sample prescription data for testing
    test_prescriptions = [
        {
            'recete_no': 'TEST001',
            'hasta_ad_soyad': 'Test Hasta 1',
            'hasta_tc': '12345678901',
            'drugs': ['Aspirin 100mg', 'Paracetamol 500mg'],
            'drug_messages': [],
            'report_details': {}
        },
        {
            'recete_no': 'TEST002', 
            'hasta_ad_soyad': 'Test Hasta 2',
            'hasta_tc': '98765432109',
            'drugs': ['Herceptin', 'Raporlu ilaç'],
            'drug_messages': ['Rapor gerekli', 'Onkoloji uzmanı'],
            'report_details': {'tani_bilgileri': ['C50.9']}
        },
        {
            'recete_no': 'TEST003',
            'hasta_ad_soyad': 'Ahmed Al-Suriye', 
            'hasta_tc': '99000000001',
            'drugs': ['Antibiyotik'],
            'drug_messages': ['Geçici koruma'],
            'report_details': {}
        }
    ]
    
    classifier = PrescriptionGroupClassifier()
    
    print("=== PRESCRIPTION GROUP CLASSIFIER TEST ===\n")
    
    # Test individual classifications
    for prescription in test_prescriptions:
        classification = classifier.classify_prescription(prescription)
        print(f"Prescription: {prescription['recete_no']}")
        print(f"Patient: {prescription['hasta_ad_soyad']}")
        print(f"Classification: {classification.group_name}")
        print(f"Reason: {classification.reason}")
        print(f"Confidence: {classification.confidence}")
        print(f"Details: {', '.join(classification.details)}")
        print("-" * 50)
        
    # Test batch classification
    grouped, results = classifier.classify_batch_prescriptions(test_prescriptions)
    
    print("\n=== BATCH CLASSIFICATION RESULTS ===")
    for group_id, prescriptions in grouped.items():
        if prescriptions:
            print(f"\n{group_id} Group ({len(prescriptions)} prescriptions):")
            for prescription in prescriptions:
                print(f"  - {prescription['recete_no']}: {prescription['hasta_ad_soyad']}")
                
    # Statistics
    stats = classifier.get_group_statistics(grouped)
    print(f"\n=== STATISTICS ===")
    print(f"Total Prescriptions: {stats['total_prescriptions']}")
    for group_id, count in stats['group_counts'].items():
        percentage = stats['group_percentages'][group_id]
        print(f"{group_id} Group: {count} ({percentage}%)")

if __name__ == "__main__":
    test_prescription_classifier()