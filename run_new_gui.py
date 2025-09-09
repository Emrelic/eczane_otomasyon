#!/usr/bin/env python3
"""
Yeni Sekmeli GUI'yi başlat
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from gui.tabbed_main_window import TabbedMainWindow

if __name__ == "__main__":
    print("Yeni Sekmeli GUI baslatiliyor...")
    app = TabbedMainWindow()
    app.run()