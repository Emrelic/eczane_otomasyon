#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eczane Otomasyon System Launcher
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        from gui_unified_processor import UnifiedProcessorGUI
        app = UnifiedProcessorGUI()
        app.mainloop()
    except ImportError as e:
        print(f"Import hatasi: {e}")
        print("Lutfen dependencies kurulu oldugundan emin olun:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Sistem baslatma hatasi: {e}")
        input("Devam etmek için Enter tuslayın...")
