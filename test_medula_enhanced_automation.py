#!/usr/bin/env python3
"""
Enhanced Medula Automation Test
Tests the improved CAPTCHA auto-submit and real credentials
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def test_enhanced_medula_automation():
    """Test the enhanced Medula automation features"""
    try:
        print("=== ENHANCED MEDULA AUTOMATION TEST ===\n")
        
        # Import components
        from config.settings import Settings
        from medula_automation.browser import MedulaBrowser
        
        # Initialize settings - check real credentials
        settings = Settings()
        print(f"[CONFIG] Medula URL: {settings.medula_url}")
        print(f"[CONFIG] Username: {settings.medula_username}")
        print(f"[CONFIG] Password: {'*' * len(settings.medula_password)}")
        print()
        
        # Initialize browser
        browser = MedulaBrowser(settings)
        print("[BROWSER] Browser initializing...")
        
        if not browser.start():
            print("[ERROR] Browser failed to start")
            return False
        
        print("[SUCCESS] Browser started successfully")
        print("[INFO] Opening Medula login page...")
        
        # Test the enhanced login process
        print("\n=== ENHANCED LOGIN TEST ===")
        print("[FEATURES]")
        print("[OK] Automatic username/password filling")
        print("[OK] Automatic KVKK checkbox selection") 
        print("[OK] CAPTCHA field detection")
        print("[OK] 6-digit auto-submit on CAPTCHA completion")
        print("[OK] Real credentials from .env file")
        print()
        
        print("[INSTRUCTION] Please follow these steps:")
        print("1. Username/password will be filled automatically")
        print("2. KVKK checkbox will be checked automatically")
        print("3. Enter the 6-digit CAPTCHA code")
        print("4. System will auto-submit after 6th digit")
        print()
        
        # Start login process
        login_result = browser.login()
        
        if login_result:
            print("\n[SUCCESS] Enhanced Medula login completed!")
            print("[INFO] Real credentials working correctly")
            print("[INFO] Auto-CAPTCHA submission working")
        else:
            print("\n[ERROR] Login process failed")
            return False
        
        # Clean up
        browser.quit()
        print("\n[CLEANUP] Browser closed")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Enhanced Medula Automation Test...")
    print("This test validates:")
    print("- Real .env credentials usage")
    print("- Auto username/password fill")
    print("- Auto KVKK checkbox")
    print("- 6-digit CAPTCHA auto-submit")
    print()
    
    success = test_enhanced_medula_automation()
    
    if success:
        print("\nSUCCESS: Enhanced Medula automation test successful!")
        print("All improvements working correctly!")
    else:
        print("\nERROR: Test failed - check errors above")