"""
Eczane Otomasyon Ayarları
Tüm konfigürasyon parametrelerini yönetir
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """Uygulama ayarları sınıfı"""
    
    def __init__(self):
        # .env dosyasını yükle
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Medula Ayarları
        self.medula_url = os.getenv('MEDULA_URL', 'https://medeczane.sgk.gov.tr/eczane/')
        self.medula_username = os.getenv('MEDULA_USERNAME', '')
        self.medula_password = os.getenv('MEDULA_PASSWORD', '')
        
        # Browser Ayarları
        self.browser_type = os.getenv('BROWSER_TYPE', 'chrome')  # chrome, firefox, edge
        self.headless = os.getenv('HEADLESS', 'false').lower() == 'true'
        self.page_load_timeout = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
        self.implicit_wait = int(os.getenv('IMPLICIT_WAIT', '10'))
        
        # AI Ayarları
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        
        # Claude Ayarları (Aktif)
        self.claude_api_key = os.getenv('CLAUDE_API_KEY', '')
        self.ANTHROPIC_API_KEY = os.getenv('CLAUDE_API_KEY', '')  # Compatibility
        self.ai_provider = os.getenv('AI_PROVIDER', 'claude')  # Claude aktif!
        self.ai_model = os.getenv('AI_MODEL', 'claude-3-sonnet-20240229')  # Claude model
        
        # Logging Ayarları
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/eczane_otomasyon.log')
        
        # İş Mantığı Ayarları
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '60'))  # saniye
        self.max_retry_attempts = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
        self.auto_approve_threshold = float(os.getenv('AUTO_APPROVE_THRESHOLD', '0.8'))
        
        # Güvenlik Ayarları
        self.enable_screenshots = os.getenv('ENABLE_SCREENSHOTS', 'true').lower() == 'true'
        self.screenshot_dir = os.getenv('SCREENSHOT_DIR', 'screenshots')
        
        # Doğrulama yap
        self._validate_settings()
    
    def _validate_settings(self):
        """Ayarları doğrular"""
        errors = []
        
        if not self.medula_username:
            errors.append("MEDULA_USERNAME gerekli")
            
        if not self.medula_password:
            errors.append("MEDULA_PASSWORD gerekli")
            
        # AI Provider kontrolü
        if self.ai_provider.lower() == 'claude':
            if not self.claude_api_key:
                errors.append("CLAUDE_API_KEY gerekli")
        elif self.ai_provider.lower() == 'openai':
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY gerekli")
            
        if self.browser_type not in ['chrome', 'firefox', 'edge']:
            errors.append("BROWSER_TYPE 'chrome', 'firefox' veya 'edge' olmalı")
            
        if errors:
            raise ValueError("Ayar hataları:\n" + "\n".join(f"- {error}" for error in errors))
    
    def create_directories(self):
        """Gerekli dizinleri oluşturur"""
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        if self.enable_screenshots:
            screenshot_dir = Path(self.screenshot_dir)
            screenshot_dir.mkdir(exist_ok=True)
    
    def get_browser_options(self):
        """Browser seçeneklerini döndürür"""
        return {
            'headless': self.headless,
            'page_load_timeout': self.page_load_timeout,
            'implicit_wait': self.implicit_wait
        }
    
    def get_openai_config(self):
        """OpenAI konfigürasyonunu döndürür"""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'temperature': self.openai_temperature,
            'max_tokens': self.openai_max_tokens
        }