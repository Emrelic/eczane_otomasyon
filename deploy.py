#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Deployment Script
Eczane Otomasyon Sistemi - Production Deployment
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class ProductionDeployer:
    """Production deployment automation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_info = {
            "deployment_time": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": []
        }
        
        # Core components to deploy
        self.core_files = [
            "unified_prescription_processor.py",
            "gui_unified_processor.py", 
            "advanced_batch_processor.py",
            "config/settings.py",
            "ai_analyzer/claude_prescription_analyzer.py",
            "ai_analyzer/sut_rules_database.py",
            "medula_automation/browser.py",
            "database/sqlite_handler.py",
            "utils/helpers.py"
        ]
        
        # Required directories
        self.required_dirs = [
            "config", "ai_analyzer", "medula_automation", 
            "database", "utils", "screenshots", 
            "exports", "logs", "batch_results"
        ]
        
        # Dependencies
        self.dependencies = [
            "selenium>=4.0.0",
            "anthropic>=0.3.0", 
            "customtkinter>=5.0.0",
            "loguru>=0.7.0",
            "pandas>=2.0.0",
            "openpyxl>=3.1.0",
            "schedule>=1.2.0",
            "watchdog>=4.0.0",
            "pillow>=10.0.0",
            "requests>=2.28.0"
        ]

    def check_system_requirements(self):
        """System requirements kontrolu"""
        print("=== SISTEM GEREKSINIMLERI KONTROL ===")
        
        checks = {
            "Python Version": self._check_python_version(),
            "Chrome Browser": self._check_chrome_browser(),
            "Required Files": self._check_required_files(),
            "Configuration": self._check_configuration()
        }
        
        all_passed = True
        for check_name, result in checks.items():
            status = "BASARILI" if result else "BASARISIZ"
            print(f"{check_name}: {status}")
            if not result:
                all_passed = False
                
        return all_passed
    
    def _check_python_version(self):
        """Python version check"""
        version = sys.version_info
        return version.major == 3 and version.minor >= 8
    
    def _check_chrome_browser(self):
        """Chrome browser check"""
        try:
            if sys.platform.startswith('win'):
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                return any(os.path.exists(path) for path in chrome_paths)
            return True
        except:
            return False
    
    def _check_required_files(self):
        """Required files check"""
        missing_files = []
        for file_path in self.core_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"Eksik dosyalar: {missing_files}")
            return False
        return True
    
    def _check_configuration(self):
        """Configuration check"""
        config_file = self.project_root / "config" / "settings.py"
        if not config_file.exists():
            return False
            
        try:
            # Check if Claude API key is configured
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'CLAUDE_API_KEY' in content
        except:
            return False

    def install_dependencies(self):
        """Python dependencies kurulum"""
        print("\n=== DEPENDENCY KURULUM ===")
        
        try:
            # requirements.txt olustur
            requirements_path = self.project_root / "requirements.txt"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                for dep in self.dependencies:
                    f.write(f"{dep}\n")
            
            print(f"Requirements.txt olusturuldu: {requirements_path}")
            
            # pip install
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                str(requirements_path)
            ])
            
            print(" Tum dependencies kuruldu!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f" Dependency kurulum hatasi: {e}")
            return False
        except Exception as e:
            print(f" Beklenmeyen hata: {e}")
            return False

    def create_directory_structure(self):
        """Production directory structure olustur"""
        print("\n=== DIRECTORY STRUCTURE ===")
        
        try:
            for dir_name in self.required_dirs:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(exist_ok=True)
                print(f"Dizin hazir: {dir_path}")
            
            # Log files için özel dizin
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Empty log file olustur
            log_file = logs_dir / "system.log"
            if not log_file.exists():
                log_file.touch()
            
            print(" Directory structure hazir!")
            return True
            
        except Exception as e:
            print(f" Directory olusturma hatasi: {e}")
            return False

    def create_startup_scripts(self):
        """Startup scripts olustur"""
        print("\n=== STARTUP SCRIPTS ===")
        
        try:
            # Windows batch file
            batch_content = f"""@echo off
echo Eczane Otomasyon Sistemi Baslatiliyor...
cd /d "{self.project_root}"
python gui_unified_processor.py
pause
"""
            
            batch_file = self.project_root / "start_system.bat"
            with open(batch_file, 'w', encoding='cp1254') as f:
                f.write(batch_content)
            
            # Python launcher
            launcher_content = f'''#!/usr/bin/env python3
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
        print(f"Import hatasi: {{e}}")
        print("Lutfen dependencies kurulu oldugundan emin olun:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Sistem baslatma hatasi: {{e}}")
        input("Devam etmek için Enter tuslayın...")
'''
            
            launcher_file = self.project_root / "launch_system.py"
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            print(f" Startup scripts olusturuldu:")
            print(f"  - Windows: {batch_file}")
            print(f"  - Python: {launcher_file}")
            
            return True
            
        except Exception as e:
            print(f" Startup script olusturma hatasi: {e}")
            return False

    def create_configuration_template(self):
        """Configuration template olustur"""
        print("\n=== CONFIGURATION TEMPLATE ===")
        
        try:
            config_template = f'''# -*- coding: utf-8 -*-
"""
ECZANE OTOMASYON SISTEMI - PRODUCTION CONFIGURATION
Deployment Date: {self.deployment_info["deployment_time"]}
Version: {self.deployment_info["version"]}
"""

import os
from pathlib import Path

class Settings:
    """Production Settings Configuration"""
    
    # API Configuration
    CLAUDE_API_KEY = "YOUR_CLAUDE_API_KEY_HERE"  # Claude API anahtarini buraya girin
    CLAUDE_MODEL = "claude-3-haiku-20240307"
    
    # Database Configuration
    DATABASE_PATH = "database/prescriptions.db"
    
    # Selenium Configuration
    SELENIUM_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080"
    ]
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/system.log"
    LOG_ROTATION = "1 day"
    LOG_RETENTION = "30 days"
    
    # Batch Processing Configuration
    BATCH_SIZE = 5
    MAX_CONCURRENT_WORKERS = 3
    PROCESSING_TIMEOUT = 300  # 5 minutes
    
    # File Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
    EXPORTS_DIR = PROJECT_ROOT / "exports"
    BATCH_RESULTS_DIR = PROJECT_ROOT / "batch_results"
    
    # Auto-processing Configuration
    AUTO_PROCESSING_ENABLED = False
    MONITORING_DIRECTORIES = []
    PROCESSING_SCHEDULE = "0 */2 * * *"  # Her 2 saatte bir
    
    @classmethod
    def validate_configuration(cls):
        """Configuration validation"""
        errors = []
        
        if not cls.CLAUDE_API_KEY or cls.CLAUDE_API_KEY == "YOUR_CLAUDE_API_KEY_HERE":
            errors.append("Claude API key tanimlanmamis!")
        
        required_dirs = [cls.SCREENSHOTS_DIR, cls.EXPORTS_DIR, cls.BATCH_RESULTS_DIR]
        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
        
        return errors
    
    @classmethod
    def get_chrome_driver_path(cls):
        """ChromeDriver path detection"""
        possible_paths = [
            "chromedriver.exe",
            "drivers/chromedriver.exe",
            r"C:\\chromedriver\\chromedriver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
'''
            
            config_file = self.project_root / "config" / "production_settings.py"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_template)
            
            print(f" Configuration template olusturuldu: {config_file}")
            print(" ONEMLI: Claude API key'i production_settings.py dosyasinda tanimlayin!")
            
            return True
            
        except Exception as e:
            print(f" Configuration template hatasi: {e}")
            return False

    def create_deployment_info(self):
        """Deployment bilgileri dosyasi olustur"""
        print("\n=== DEPLOYMENT INFO ===")
        
        try:
            self.deployment_info["components"] = [
                {
                    "name": "Unified Prescription Processor",
                    "file": "unified_prescription_processor.py",
                    "status": "deployed"
                },
                {
                    "name": "GUI Interface", 
                    "file": "gui_unified_processor.py",
                    "status": "deployed"
                },
                {
                    "name": "Advanced Batch Processor",
                    "file": "advanced_batch_processor.py", 
                    "status": "deployed"
                },
                {
                    "name": "Claude AI Analyzer",
                    "file": "ai_analyzer/claude_prescription_analyzer.py",
                    "status": "deployed"
                },
                {
                    "name": "SUT Rules Database",
                    "file": "ai_analyzer/sut_rules_database.py",
                    "status": "deployed"
                }
            ]
            
            deployment_file = self.project_root / "DEPLOYMENT_INFO.json"
            with open(deployment_file, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_info, f, ensure_ascii=False, indent=2)
            
            print(f" Deployment info olusturuldu: {deployment_file}")
            return True
            
        except Exception as e:
            print(f" Deployment info hatasi: {e}")
            return False

    def run_final_tests(self):
        """Final test suite"""
        print("\n=== FINAL TESTS ===")
        
        try:
            # Import test
            sys.path.insert(0, str(self.project_root))
            
            test_results = {
                "import_test": self._test_imports(),
                "configuration_test": self._test_configuration(),
                "database_test": self._test_database_connection()
            }
            
            all_passed = all(test_results.values())
            
            for test_name, result in test_results.items():
                status = "BASARILI" if result else "BASARISIZ"
                print(f"{test_name}: {status}")
            
            return all_passed
            
        except Exception as e:
            print(f" Final test hatasi: {e}")
            return False
    
    def _test_imports(self):
        """Import test"""
        try:
            import unified_prescription_processor
            import gui_unified_processor
            import advanced_batch_processor
            return True
        except ImportError:
            return False
    
    def _test_configuration(self):
        """Configuration test"""
        try:
            from config.settings import Settings
            return True
        except:
            return False
    
    def _test_database_connection(self):
        """Database connection test"""
        try:
            from database.sqlite_handler import SQLiteHandler
            db = SQLiteHandler()
            return True
        except:
            return False

    def deploy(self):
        """Full deployment process"""
        print("ECZANE OTOMASYON SISTEMI - PRODUCTION DEPLOYMENT")
        print("=" * 60)
        
        steps = [
            ("System Requirements Check", self.check_system_requirements),
            ("Install Dependencies", self.install_dependencies),
            ("Create Directory Structure", self.create_directory_structure),
            ("Create Startup Scripts", self.create_startup_scripts),
            ("Create Configuration Template", self.create_configuration_template),
            ("Create Deployment Info", self.create_deployment_info),
            ("Run Final Tests", self.run_final_tests)
        ]
        
        success_count = 0
        
        for step_name, step_function in steps:
            print(f"\n--- {step_name} ---")
            
            try:
                if step_function():
                    success_count += 1
                    print(f" {step_name} TAMAMLANDI!")
                else:
                    print(f" {step_name} BASARISIZ!")
            except Exception as e:
                print(f" {step_name} HATASI: {e}")
        
        # Final results
        print("\n" + "=" * 60)
        print("DEPLOYMENT SONUCLARI:")
        print(f"Tamamlanan adimlar: {success_count}/{len(steps)}")
        
        if success_count == len(steps):
            print("DEPLOYMENT BASARIYLA TAMAMLANDI!")
            print("\nSISTEM BASLATMA:")
            print("1. Windows: start_system.bat dosyasini calistirin")
            print("2. Python: python launch_system.py komutu calistirin")
            print("\nONEMLI NOTLAR:")
            print("- config/production_settings.py dosyasinda Claude API key tanimlayin")
            print("- Chrome browser kurulu olduguna emin olun")
            print("- Internet baglantisi gereklidir")
        else:
            print("DEPLOYMENT KISMI BASARISIZ!")
            print("Lutfen hatalari kontrol edin ve tekrar deneyin.")
        
        return success_count == len(steps)

def main():
    """Main deployment function"""
    deployer = ProductionDeployer()
    return deployer.deploy()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)