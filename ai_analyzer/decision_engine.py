"""
AI Karar Verme Motoru
OpenAI API kullanarak reçete değerlendirmesi yapar
"""

import openai
import json
from loguru import logger
from datetime import datetime, timedelta
import re


class DecisionEngine:
    """AI tabanlı reçete karar verme motoru"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Karar kriterleri
        self.approval_criteria = {
            'max_daily_dose': True,
            'drug_interactions': True,
            'patient_age_compatibility': True,
            'diagnosis_drug_match': True,
            'prescription_completeness': True
        }
        
        logger.info("AI Karar Motoru başlatıldı")
    
    def analyze_prescription(self, prescription_data):
        """Reçeteyi analiz eder ve karar verir"""
        try:
            logger.info(f"Reçete analiz ediliyor - ID: {prescription_data['id']}")
            
            # AI prompt'u hazırla
            prompt = self._create_analysis_prompt(prescription_data)
            
            # OpenAI API'sine istek gönder
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            
            # Yanıtı parse et
            decision = self._parse_ai_response(response.choices[0].message.content)
            
            # Güvenlik kontrolleri
            decision = self._apply_safety_checks(prescription_data, decision)
            
            logger.info(f"Karar alındı - ID: {prescription_data['id']}, Karar: {decision['action']}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Reçete analizi sırasında hata: {e}")
            # Hata durumunda güvenli karar ver
            return {
                'action': 'hold',
                'reason': f'Analiz hatası: {str(e)}',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_system_prompt(self):
        """Sistem prompt'unu döndürür"""
        return """Sen deneyimli bir eczane müdürü ve ilaç uzmanısın. 
        Görevin reçeteleri değerlendirip onay, red veya bekleme kararı vermek.
        
        Değerlendirme kriterlerin:
        1. İlaç dozaj uygunluğu
        2. İlaç etkileşimleri
        3. Hasta yaş uyumluluğu
        4. Tanı-ilaç uyumu
        5. Reçete eksiksizliği
        6. Yasal gereklilikler
        
        Karar seçenekleri:
        - approve: Reçete uygun, onaylanabilir
        - reject: Reçetede ciddi sorun var, reddedilmeli
        - hold: Belirsizlik var, manuel inceleme gerekli
        
        Yanıtını JSON formatında ver:
        {
            "action": "approve/reject/hold",
            "reason": "karar gerekçesi",
            "confidence": 0.0-1.0,
            "risk_factors": ["risk faktörleri listesi"],
            "recommendations": ["öneriler listesi"]
        }"""
    
    def _create_analysis_prompt(self, prescription_data):
        """Analiz prompt'unu oluşturur"""
        return f"""
        Aşağıdaki reçeteyi değerlendir:
        
        Reçete Bilgileri:
        - Reçete ID: {prescription_data['id']}
        - Hasta: {prescription_data['patient_name']}
        - Hasta TC: {prescription_data['patient_tc']}
        - Doktor: {prescription_data['doctor_name']}
        - Hastane: {prescription_data['hospital']}
        - Reçete Tarihi: {prescription_data['prescription_date']}
        - Toplam Tutar: {prescription_data['total_amount']}
        - Mevcut Durum: {prescription_data['status']}
        
        Bu reçete için kararını ver ve gerekçelendir.
        """
    
    def _parse_ai_response(self, response_text):
        """AI yanıtını parse eder"""
        try:
            # JSON formatını bulmaya çalış
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                decision_data = json.loads(json_str)
                
                # Gerekli alanları kontrol et
                required_fields = ['action', 'reason', 'confidence']
                for field in required_fields:
                    if field not in decision_data:
                        raise KeyError(f"Gerekli alan eksik: {field}")
                
                # Timestamp ekle
                decision_data['timestamp'] = datetime.now().isoformat()
                
                # Varsayılan değerler
                if 'risk_factors' not in decision_data:
                    decision_data['risk_factors'] = []
                if 'recommendations' not in decision_data:
                    decision_data['recommendations'] = []
                
                return decision_data
            
            else:
                raise ValueError("JSON formatı bulunamadı")
                
        except Exception as e:
            logger.error(f"AI yanıtı parse edilemedi: {e}")
            logger.debug(f"Ham yanıt: {response_text}")
            
            # Varsayılan karar
            return {
                'action': 'hold',
                'reason': 'AI yanıtı parse edilemedi, manuel inceleme gerekli',
                'confidence': 0.0,
                'risk_factors': ['AI parsing hatası'],
                'recommendations': ['Manuel inceleme yapın'],
                'timestamp': datetime.now().isoformat()
            }
    
    def _apply_safety_checks(self, prescription_data, decision):
        """Güvenlik kontrollerini uygular"""
        try:
            # Yüksek riskli durumlar
            high_risk_conditions = [
                'kanser',
                'kemotarapi', 
                'morfin',
                'opioid',
                'narkotik'
            ]
            
            prescription_text = ' '.join([
                prescription_data.get('patient_name', ''),
                prescription_data.get('doctor_name', ''),
                prescription_data.get('hospital', '')
            ]).lower()
            
            # Yüksek risk kontrolü
            for condition in high_risk_conditions:
                if condition in prescription_text:
                    if decision['action'] == 'approve' and decision['confidence'] < 0.9:
                        decision['action'] = 'hold'
                        decision['reason'] += f' (Yüksek risk: {condition} tespit edildi)'
                        decision['risk_factors'].append(f'Yüksek riskli durum: {condition}')
            
            # Tutar kontrolü
            try:
                amount = float(prescription_data.get('total_amount', '0').replace(',', ''))
                if amount > 1000:  # 1000 TL üzeri
                    if decision['action'] == 'approve' and decision['confidence'] < 0.8:
                        decision['action'] = 'hold'
                        decision['reason'] += ' (Yüksek tutar nedeniyle ek kontrol gerekli)'
                        decision['risk_factors'].append('Yüksek reçete tutarı')
            except:
                pass
            
            # Zaman kontrolü (çok eski reçeteler)
            try:
                prescription_date = datetime.strptime(prescription_data['prescription_date'], '%Y-%m-%d')
                if datetime.now() - prescription_date > timedelta(days=30):
                    decision['risk_factors'].append('Eski tarihli reçete')
            except:
                pass
            
            # Otomatik onay eşiği kontrolü
            if decision['action'] == 'approve':
                if decision['confidence'] < self.settings.auto_approve_threshold:
                    decision['action'] = 'hold'
                    decision['reason'] += f' (Güven skoru {self.settings.auto_approve_threshold} altında)'
            
            return decision
            
        except Exception as e:
            logger.error(f"Güvenlik kontrolleri sırasında hata: {e}")
            # Hata durumunda bekletme kararı ver
            decision['action'] = 'hold'
            decision['reason'] += f' (Güvenlik kontrolü hatası: {str(e)})'
            return decision
    
    def get_decision_statistics(self):
        """Karar istatistiklerini döndürür"""
        # Bu method gelecekte karar geçmişini takip etmek için kullanılabilir
        return {
            'total_decisions': 0,
            'approved': 0,
            'rejected': 0,
            'held': 0,
            'average_confidence': 0.0
        }
    
    def validate_prescription_format(self, prescription_data):
        """Reçete formatının doğruluğunu kontrol eder"""
        required_fields = [
            'id', 'patient_name', 'patient_tc', 
            'doctor_name', 'hospital', 'prescription_date'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in prescription_data or not prescription_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'missing_fields': missing_fields,
                'message': f'Eksik alanlar: {", ".join(missing_fields)}'
            }
        
        return {
            'valid': True,
            'message': 'Reçete formatı geçerli'
        }