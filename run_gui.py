#!/usr/bin/env python3
"""
GUI Başlatma Scripti
CustomTkinter tabanlı modern arayüzü başlatır
"""

import sys
import os
from pathlib import Path

# Proje root dizinini path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """GUI uygulamasını başlat"""
    print("Eczane Recete Kontrol Otomasyonu GUI Baslatiliyor...")
    print("Proje dizini:", project_root)
    
    try:
        # Gerekli dizinleri oluştur
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
        # GUI'yi başlat
        from gui.main_window import EczaneOtomasyonGUI
        
        app = EczaneOtomasyonGUI()
        app.run()
        
    except ImportError as e:
        print(f"Import hatasi: {e}")
        print("Gerekli kutuphaneleri yukleyin: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"Uygulama hatasi: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())