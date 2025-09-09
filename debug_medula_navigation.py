#!/usr/bin/env python3
"""
Debug Medula Navigation
Analyzes the page structure after login to fix navigation issues
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def debug_medula_navigation():
    """Debug Medula navigation after successful login"""
    try:
        print("=== MEDULA NAVIGATION DEBUG ===\n")
        
        # Import components
        from config.settings import Settings
        from medula_automation.browser import MedulaBrowser
        
        # Initialize with real settings
        settings = Settings()
        browser = MedulaBrowser(settings)
        
        print("[INFO] Starting browser with real credentials...")
        print(f"[CONFIG] Username: {settings.medula_username}")
        print(f"[CONFIG] Password: {'*' * len(settings.medula_password)}")
        
        # Start browser
        if not browser.start():
            print("[ERROR] Browser failed to start")
            return False
        
        print("[SUCCESS] Browser started")
        
        # Login process
        print("\n[LOGIN] Starting login process...")
        print("[INFO] This will:")
        print("- Auto-fill username/password")
        print("- Auto-check KVKK")
        print("- Wait for CAPTCHA (you need to solve it)")
        print("- Auto-submit when CAPTCHA complete")
        
        if not browser.login():
            print("[ERROR] Login failed")
            return False
        
        print("\n[SUCCESS] Login completed successfully!")
        
        # Now analyze the page structure after login
        print("\n=== COMPREHENSIVE PAGE ANALYSIS ===")
        
        from selenium.webdriver.common.by import By
        
        # Check for frames/iframes first
        print("\n[FRAME ANALYSIS]")
        frames = browser.driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(frames)} iframes")
        
        # Get current URL and page title
        current_url = browser.driver.current_url
        page_title = browser.driver.title
        print(f"\n[PAGE INFO]")
        print(f"Current URL: {current_url}")
        print(f"Page Title: {page_title}")
        
        # Check page source for Turkish keywords
        page_source = browser.driver.page_source.lower()
        keywords = ['reçete', 'recete', 'fatura', 'hasta', 'patient', 'prescription']
        found_keywords = [kw for kw in keywords if kw in page_source]
        print(f"Turkish keywords found in page: {found_keywords}")
        
        # Get all links with comprehensive analysis
        links = browser.driver.find_elements(By.TAG_NAME, "a")
        print(f"\n[LINK ANALYSIS] Found {len(links)} links on page:")
        
        prescription_links = []
        all_links = []
        
        for i, link in enumerate(links):
            try:
                text = link.text.strip()
                href = link.get_attribute('href') or ''
                title = link.get_attribute('title') or ''
                onclick = link.get_attribute('onclick') or ''
                
                link_info = {
                    'index': i,
                    'text': text,
                    'href': href,
                    'title': title,
                    'onclick': onclick
                }
                all_links.append(link_info)
                
                # Check if this could be prescription-related
                full_text = (text + href + title + onclick).lower()
                if any(keyword in full_text for keyword in 
                       ['reçete', 'recete', 'prescription', 'liste', 'fatura', 'hasta']):
                    prescription_links.append(link_info)
                    print(f"  🎯 PRESCRIPTION LINK {len(prescription_links)}:")
                    print(f"      Text: '{text}'")
                    print(f"      Href: '{href}'")
                    print(f"      Title: '{title}'")
                    print(f"      OnClick: '{onclick}'")
                else:
                    # Show all links for analysis
                    if text or href:  # Only show meaningful links
                        print(f"  Link {i+1}: '{text[:50]}...' -> '{href[:50]}...'")
                        
            except Exception as e:
                print(f"  Link {i+1}: [Error: {e}]")
        
        print(f"\n[SUMMARY] {len(prescription_links)} potential prescription links found!")
        
        # Also check for buttons, divs, spans with onclick
        print(f"\n[INTERACTIVE ELEMENTS]")
        clickable_elements = browser.driver.find_elements(By.CSS_SELECTOR, 
            "[onclick], button, input[type='submit'], input[type='button']")
        print(f"Found {len(clickable_elements)} clickable elements")
        
        for i, elem in enumerate(clickable_elements[:10]):
            try:
                text = elem.text.strip() or elem.get_attribute('value') or ''
                onclick = elem.get_attribute('onclick') or ''
                if any(kw in (text + onclick).lower() for kw in ['reçete', 'recete', 'liste']):
                    print(f"  🎯 INTERACTIVE: '{text}' onclick='{onclick[:50]}...'")
                elif text:
                    print(f"  Interactive {i+1}: '{text}' onclick='{onclick[:30]}...'")
            except Exception:
                pass
        
        # Analyze menu structures
        print("\n[MENU ANALYSIS]")
        menus = browser.driver.find_elements(By.CSS_SELECTOR, "nav, .menu, .navigation, #menu, .main-menu")
        print(f"Found {len(menus)} menu structures")
        
        # Analyze forms
        forms = browser.driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} forms")
        
        # Try to click the first prescription link if found
        if prescription_links:
            print(f"\n[TEST] Attempting to click first prescription link...")
            try:
                first_link = prescription_links[0]
                link_element = links[first_link['index']]
                
                # Use JavaScript click
                browser.driver.execute_script("arguments[0].click();", link_element)
                print(f"[SUCCESS] Clicked: {first_link['text']}")
                
                # Wait a bit and check current URL
                import time
                time.sleep(3)
                current_url = browser.driver.current_url
                print(f"[INFO] Current URL after click: {current_url}")
                
            except Exception as e:
                print(f"[ERROR] Failed to click prescription link: {e}")
        
        # Keep browser open for manual inspection
        print(f"\n[MANUAL] Browser staying open for manual inspection...")
        print(f"[MANUAL] Check the current page for 5 seconds...")
        
        # Wait 5 seconds instead of input()
        import time
        time.sleep(5)
        print("[INFO] Continuing analysis...")
        
        browser.quit()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Debugging Medula Navigation...")
    print("This will help us fix the 'demo user' issue by analyzing the real Medula structure\n")
    
    success = debug_medula_navigation()
    
    if success:
        print("\n✅ Debug completed - use findings to fix navigation")
    else:
        print("\n❌ Debug failed")