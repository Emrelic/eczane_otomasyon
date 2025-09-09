#!/usr/bin/env python3
"""
Direct Medula Live Test
Tests actual Medula Live processing to see where demo user comes from
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def test_medula_live_direct():
    """Test Medula Live processing directly"""
    try:
        print("=== DIRECT MEDULA LIVE TEST ===\n")
        
        # Import processor
        from unified_prescription_processor import UnifiedPrescriptionProcessor
        
        # Initialize processor
        processor = UnifiedPrescriptionProcessor()
        print("[INFO] Unified processor initialized")
        
        # Check settings first
        print(f"[CONFIG] Username: {processor.settings.medula_username}")
        print(f"[CONFIG] Password: {'*' * len(processor.settings.medula_password)}")
        print()
        
        # Start Medula Live processing
        print("[START] Starting Medula Live processing...")
        print("[INFO] This will:")
        print("  1. Initialize browser with real credentials")
        print("  2. Navigate to Medula login")
        print("  3. Auto-fill username/password")
        print("  4. Auto-check KVKK")
        print("  5. Wait for CAPTCHA completion")
        print("  6. Auto-submit when CAPTCHA complete")
        print("  7. Extract real prescription data")
        print()
        
        # Process from Medula Live
        results = processor.process_from_medula_live(limit=2, group='A')
        
        print(f"\n[RESULTS] Got {len(results)} results:")
        for i, result in enumerate(results, 1):
            patient = result.get('prescription_data', {}).get('hasta_ad_soyad', 'N/A')
            prescription_id = result.get('prescription_id', 'N/A')
            source = result.get('processing_metadata', {}).get('source', 'unknown')
            
            print(f"  {i}. ID: {prescription_id}")
            print(f"     Patient: {patient}")
            print(f"     Source: {source}")
            
            if 'demo' in patient.lower() or 'fallback' in patient.lower():
                print(f"     ⚠️  This looks like mock/fallback data!")
            else:
                print(f"     ✅ This looks like real Medula data!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Medula Live processing directly...")
    print("This will show us exactly where 'demo user' comes from\n")
    
    success = test_medula_live_direct()
    
    if success:
        print("\n✅ Test completed - check results above")
    else:
        print("\n❌ Test failed - check errors")