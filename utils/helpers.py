"""
Yardımcı Fonksiyonlar
Genel amaçlı utility fonksiyonları
"""

import re
import hashlib
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
from loguru import logger


def validate_tc_no(tc_no: str) -> bool:
    """
    Türkiye Cumhuriyeti Kimlik Numarası doğrulaması
    
    Args:
        tc_no: TC kimlik numarası
        
    Returns:
        bool: Geçerli ise True
    """
    if not tc_no or len(tc_no) != 11:
        return False
    
    if not tc_no.isdigit():
        return False
    
    # İlk hane 0 olamaz
    if tc_no[0] == '0':
        return False
    
    # Son iki hane kontrol haneleri
    digits = [int(x) for x in tc_no]
    
    # 10. hane kontrolü
    odd_sum = sum(digits[0:9:2])  # 1,3,5,7,9. haneler
    even_sum = sum(digits[1:8:2])  # 2,4,6,8. haneler
    
    check_digit_10 = (odd_sum * 7 - even_sum) % 10
    
    if check_digit_10 != digits[9]:
        return False
    
    # 11. hane kontrolü
    check_digit_11 = sum(digits[0:10]) % 10
    
    if check_digit_11 != digits[10]:
        return False
    
    return True


def format_currency(amount: float) -> str:
    """
    Parasal tutarı Türkiye formatında biçimlendirir
    
    Args:
        amount: Tutar
        
    Returns:
        str: Biçimlendirilmiş tutar
    """
    try:
        return f"{amount:,.2f} ₺".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "0,00 ₺"


def parse_currency(currency_str: str) -> float:
    """
    Türkiye formatındaki parasal tutarı float'a çevirir
    
    Args:
        currency_str: Parasal tutar string'i
        
    Returns:
        float: Tutar
    """
    try:
        # Sadece rakam, nokta ve virgülü bırak
        cleaned = re.sub(r'[^\d,.]', '', currency_str)
        
        # Türkiye formatından ABD formatına çevir
        if ',' in cleaned and '.' in cleaned:
            # 1.234,56 formatı
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # 1234,56 formatı
            cleaned = cleaned.replace(',', '.')
        
        return float(cleaned)
    except:
        return 0.0


def validate_email(email: str) -> bool:
    """
    Email adresi doğrulaması
    
    Args:
        email: Email adresi
        
    Returns:
        bool: Geçerli ise True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Türkiye telefon numarası doğrulaması
    
    Args:
        phone: Telefon numarası
        
    Returns:
        bool: Geçerli ise True
    """
    # Sadece rakamları al
    digits = re.sub(r'\D', '', phone)
    
    # Türkiye cep telefonu formatları
    patterns = [
        r'^90(5\d{9})$',      # +90 ile başlayanlar
        r'^0(5\d{9})$',       # 0 ile başlayanlar
        r'^(5\d{9})$'         # Direkt 5 ile başlayanlar
    ]
    
    for pattern in patterns:
        if re.match(pattern, digits):
            return True
    
    return False


def format_phone(phone: str) -> str:
    """
    Telefon numarasını standart formata çevirir
    
    Args:
        phone: Ham telefon numarası
        
    Returns:
        str: Formatlanmış telefon numarası
    """
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10 and digits.startswith('5'):
        return f"0{digits[:3]} {digits[3:6]} {digits[6:8]} {digits[8:]}"
    elif len(digits) == 11 and digits.startswith('05'):
        return f"{digits[:4]} {digits[4:7]} {digits[7:9]} {digits[9:]}"
    elif len(digits) == 13 and digits.startswith('905'):
        return f"0{digits[2:5]} {digits[5:8]} {digits[8:10]} {digits[10:]}"
    
    return phone


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    String'i hash'ler
    
    Args:
        text: Hash'lenecek metin
        algorithm: Hash algoritması
        
    Returns:
        str: Hash değeri
    """
    try:
        hash_func = getattr(hashlib, algorithm)
        return hash_func(text.encode('utf-8')).hexdigest()
    except:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Güvenli JSON parse
    
    Args:
        json_str: JSON string
        default: Hata durumunda döndürülecek değer
        
    Returns:
        Any: Parse edilmiş değer veya default
    """
    try:
        return json.loads(json_str) if json_str else default
    except:
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Güvenli JSON stringify
    
    Args:
        data: JSON'a çevrilecek veri
        default: Hata durumunda döndürülecek değer
        
    Returns:
        str: JSON string
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except:
        return default


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Tarih-saat formatlaması
    
    Args:
        dt: Datetime objesi
        format_str: Format string
        
    Returns:
        str: Formatlanmış tarih-saat
    """
    try:
        return dt.strftime(format_str)
    except:
        return "Bilinmeyen tarih"


def parse_datetime(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    String'den datetime parse eder
    
    Args:
        date_str: Tarih string'i
        formats: Denenecek formatlar
        
    Returns:
        Optional[datetime]: Parse edilmiş tarih veya None
    """
    if not formats:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None


def calculate_age(birth_date: date) -> int:
    """
    Yaş hesaplar
    
    Args:
        birth_date: Doğum tarihi
        
    Returns:
        int: Yaş
    """
    try:
        today = date.today()
        age = today.year - birth_date.year
        
        # Doğum günü henüz gelmemişse yaşı 1 azalt
        if today.month < birth_date.month or \
           (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
            
        return age
    except:
        return 0


def sanitize_filename(filename: str) -> str:
    """
    Dosya adını güvenli hale getirir
    
    Args:
        filename: Ham dosya adı
        
    Returns:
        str: Güvenli dosya adı
    """
    # Türkçe karakterleri değiştir
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ş': 's', 'ü': 'u', 'ö': 'o',
        'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ş': 'S', 'Ü': 'U', 'Ö': 'O'
    }
    
    for tr_char, en_char in replacements.items():
        filename = filename.replace(tr_char, en_char)
    
    # Sadece alfanumerik karakterler, tire ve alt çizgi
    sanitized = re.sub(r'[^\w\-_.]', '_', filename)
    
    # Çoklu alt çizgileri tek yap
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    return sanitized


def ensure_directory(directory: str) -> bool:
    """
    Dizinin var olmasını sağlar
    
    Args:
        directory: Dizin yolu
        
    Returns:
        bool: Başarılı ise True
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Dizin oluşturma hatası: {e}")
        return False


def get_file_size(filepath: str) -> int:
    """
    Dosya boyutunu byte cinsinden döndürür
    
    Args:
        filepath: Dosya yolu
        
    Returns:
        int: Dosya boyutu (byte)
    """
    try:
        return Path(filepath).stat().st_size
    except:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Dosya boyutunu okunabilir formata çevirir
    
    Args:
        size_bytes: Byte cinsinden boyut
        
    Returns:
        str: Formatlanmış boyut
    """
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    except:
        return "0 B"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    String'i belirtilen uzunlukta keser
    
    Args:
        text: Kesilecek metin
        max_length: Maksimum uzunluk
        suffix: Kesim sonrası eklenen son ek
        
    Returns:
        str: Kesilmiş metin
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def mask_sensitive_data(text: str, mask_char: str = "*") -> str:
    """
    Hassas verileri maskeler (TC, telefon, email vb.)
    
    Args:
        text: Maskelenecek metin
        mask_char: Maskeleme karakteri
        
    Returns:
        str: Maskelenmiş metin
    """
    # TC numarası maskeleme
    text = re.sub(r'\b\d{11}\b', lambda m: m.group()[:3] + mask_char*5 + m.group()[-3:], text)
    
    # Email maskeleme
    text = re.sub(r'\b[\w._%+-]+@[\w.-]+\.[A-Z]{2,}\b', 
                  lambda m: m.group().split('@')[0][:2] + mask_char*3 + '@' + m.group().split('@')[1], 
                  text, flags=re.IGNORECASE)
    
    # Telefon maskeleme
    text = re.sub(r'\b0\d{3}\s*\d{3}\s*\d{2}\s*\d{2}\b',
                  lambda m: m.group()[:4] + mask_char*7, text)
    
    return text


def generate_report_id() -> str:
    """
    Benzersiz rapor ID'si oluşturur
    
    Returns:
        str: Rapor ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = hashlib.md5(str(datetime.now().microsecond).encode()).hexdigest()[:6]
    return f"RPT_{timestamp}_{random_part.upper()}"


def validate_diagnosis_code(code: str) -> bool:
    """
    ICD-10 tanı kodu doğrulaması (basit)
    
    Args:
        code: Tanı kodu
        
    Returns:
        bool: Geçerli ise True
    """
    # ICD-10 formatı: Harf + rakam + (isteğe bağlı nokta ve rakamlar)
    pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'
    return bool(re.match(pattern, code.upper()))


class DataValidator:
    """Veri doğrulama sınıfı"""
    
    @staticmethod
    def validate_prescription_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Reçete verilerini doğrular
        
        Args:
            data: Reçete verileri
            
        Returns:
            Dict: Hata listesi
        """
        errors = {}
        
        # TC kontrolü
        if 'patient_tc' in data:
            if not validate_tc_no(data['patient_tc']):
                errors.setdefault('patient_tc', []).append('Geçersiz TC kimlik numarası')
        
        # Tarih kontrolü
        if 'prescription_date' in data:
            if not parse_datetime(data['prescription_date']):
                errors.setdefault('prescription_date', []).append('Geçersiz tarih formatı')
        
        # Tutar kontrolü
        if 'total_amount' in data:
            try:
                amount = float(data['total_amount'])
                if amount < 0:
                    errors.setdefault('total_amount', []).append('Tutar negatif olamaz')
            except:
                errors.setdefault('total_amount', []).append('Geçersiz tutar formatı')
        
        # Tanı kodu kontrolü
        if 'diagnosis_code' in data and data['diagnosis_code']:
            if not validate_diagnosis_code(data['diagnosis_code']):
                errors.setdefault('diagnosis_code', []).append('Geçersiz tanı kodu formatı')
        
        return errors


def setup_logging(log_file: str = "logs/app.log", level: str = "INFO"):
    """
    Logging sistemini yapılandırır
    
    Args:
        log_file: Log dosya yolu
        level: Log seviyesi
    """
    try:
        # Log dizinini oluştur
        ensure_directory(Path(log_file).parent)
        
        # Loguru yapılandırması
        logger.add(
            log_file,
            rotation="10 MB",
            retention="30 days",
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
            encoding="utf-8"
        )
        
        logger.info("Logging sistemi başlatıldı")
        
    except Exception as e:
        print(f"Logging kurulum hatası: {e}")


def create_backup(source_file: str, backup_dir: str = "backups") -> bool:
    """
    Dosya yedeği oluşturur
    
    Args:
        source_file: Kaynak dosya
        backup_dir: Yedek dizini
        
    Returns:
        bool: Başarılı ise True
    """
    try:
        source_path = Path(source_file)
        if not source_path.exists():
            return False
        
        ensure_directory(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = Path(backup_dir) / backup_name
        
        import shutil
        shutil.copy2(source_path, backup_path)
        
        logger.info(f"Yedek oluşturuldu: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Yedek oluşturma hatası: {e}")
        return False