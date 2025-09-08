# -*- coding: utf-8 -*-
"""
ECZANE OTOMASYON SISTEMI - PRODUCTION CONFIGURATION
Deployment Date: 2025-09-08T12:24:09.121736
Version: 1.0.0
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
            r"C:\chromedriver\chromedriver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
