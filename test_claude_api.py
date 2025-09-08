"""Claude API Test Script"""
import json
import sys
import os

# Add current directory to path
sys.path.append('.')

try:
    from ai_analyzer.claude_prescription_analyzer import ClaudePrescriptionAnalyzer
    from config.settings import Settings
    
    print("Claude API Test başlıyor...")
    
    # Test verilerini yükle
    with open('manual_detailed_prescriptions.json', 'r', encoding='utf-8') as f:
        prescriptions = json.load(f)
    
    if prescriptions:
        test_prescription = prescriptions[0]  # İlk reçeteyi test et
        print(f"Test reçetesi: {test_prescription['recete_no']}")
        
        # Analyzer'ı başlat
        analyzer = ClaudePrescriptionAnalyzer()
        
        print(f"Claude enabled: {analyzer.claude_enabled}")
        
        # Analiz yap
        result = analyzer.analyze_prescription_with_claude(test_prescription)
        
        print("\nAnaliz Sonucu:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        print("Test verisi bulunamadı!")
        
except Exception as e:
    print(f"HATA: {e}")
    import traceback
    traceback.print_exc()