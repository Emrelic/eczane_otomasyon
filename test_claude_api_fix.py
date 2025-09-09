#!/usr/bin/env python3
"""
Claude API Test - API key fix validation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def test_claude_api():
    """Test Claude API with fixed configuration"""
    try:
        print("[TEST] Claude API fix validation...")
        
        # Test settings
        from config.settings import Settings
        settings = Settings()
        
        print(f"[INFO] API Key present: {'Yes' if settings.ANTHROPIC_API_KEY else 'No'}")
        print(f"[INFO] API Key length: {len(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else 0}")
        
        # Test Claude analyzer
        from ai_analyzer.claude_prescription_analyzer import ClaudePrescriptionAnalyzer
        analyzer = ClaudePrescriptionAnalyzer()
        
        print(f"[INFO] Claude enabled: {analyzer.claude_enabled}")
        
        if analyzer.claude_enabled:
            # Simple test prescription
            test_prescription = {
                "recete_no": "TEST001",
                "hasta_ad": "Test",
                "hasta_soyad": "Patient",
                "hasta_tc": "12345678901",
                "drugs": [
                    {
                        "ilac_adi": "PAROL 500MG TABLET",
                        "adet": "1"
                    }
                ],
                "ilac_mesajlari": "Test mesaj",
                "rapor_no": "TEST123",
                "rapor_tarihi": "2024-01-01"
            }
            
            print("[TEST] Testing Claude API call...")
            result = analyzer.analyze_prescription_with_claude(test_prescription)
            
            print(f"[SUCCESS] Claude API working! Decision: {result['action']}")
            print(f"[INFO] Confidence: {result['confidence']}")
            print(f"[INFO] Reason: {result['reason'][:100]}...")
            
            return True
        else:
            print("[ERROR] Claude API not initialized")
            return False
            
    except Exception as e:
        print(f"[ERROR] Claude API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_claude_api()
    if success:
        print("\n[RESULT] SUCCESS: Claude API fix successful!")
    else:
        print("\n[RESULT] ERROR: Claude API still has issues")