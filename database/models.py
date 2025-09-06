"""
Veritabanı Modelleri
SQLite kullanarak veri saklama yapıları
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from loguru import logger


class DatabaseManager:
    """Veritabanı yönetim sınıfı"""
    
    def __init__(self, db_path="data/eczane_otomasyon.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        logger.info(f"Veritabanı başlatılıyor: {self.db_path}")
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Veritabanı bağlantısı context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Kolon isimlerini kullanabilmek için
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Veritabanı tablolarını oluşturur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tc_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    birth_date DATE,
                    phone TEXT,
                    address TEXT,
                    medical_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diploma_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    specialty TEXT,
                    hospital TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reçeteler tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id TEXT UNIQUE NOT NULL,
                    patient_tc TEXT NOT NULL,
                    doctor_diploma_no TEXT NOT NULL,
                    hospital TEXT,
                    prescription_date DATE NOT NULL,
                    diagnosis_code TEXT,
                    diagnosis_description TEXT,
                    total_amount DECIMAL(10,2),
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_tc) REFERENCES patients(tc_no),
                    FOREIGN KEY (doctor_diploma_no) REFERENCES doctors(diploma_no)
                )
            ''')
            
            # İlaçlar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    active_ingredient TEXT,
                    dosage TEXT,
                    form TEXT,
                    manufacturer TEXT,
                    sut_code TEXT,
                    price DECIMAL(8,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reçete İlaçları (prescription items) tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prescription_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id TEXT NOT NULL,
                    medication_barcode TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    usage_instruction TEXT,
                    unit_price DECIMAL(8,2),
                    total_price DECIMAL(10,2),
                    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id),
                    FOREIGN KEY (medication_barcode) REFERENCES medications(barcode)
                )
            ''')
            
            # SUT Kuralları tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sut_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    diagnosis_codes TEXT,  
                    medication_codes TEXT, 
                    conditions TEXT,       
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI Kararları tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT,
                    confidence DECIMAL(3,2),
                    risk_factors TEXT,      
                    recommendations TEXT,   
                    ai_model TEXT,
                    decision_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_overridden BOOLEAN DEFAULT 0,
                    override_reason TEXT,
                    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
                )
            ''')
            
            # Sistem Logları tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_level TEXT NOT NULL,
                    module TEXT,
                    message TEXT NOT NULL,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.success("Veritabanı tabloları oluşturuldu")
    
    # Hasta işlemleri
    def add_patient(self, tc_no, name, birth_date=None, phone=None, address=None, medical_history=None):
        """Yeni hasta ekler"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO patients (tc_no, name, birth_date, phone, address, medical_history)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (tc_no, name, birth_date, phone, address, medical_history))
                conn.commit()
                logger.info(f"Yeni hasta eklendi: {name} ({tc_no})")
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.warning(f"Hasta zaten mevcut: {tc_no}")
                return None
    
    def get_patient(self, tc_no):
        """Hasta bilgilerini getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients WHERE tc_no = ?', (tc_no,))
            return cursor.fetchone()
    
    def update_patient(self, tc_no, **kwargs):
        """Hasta bilgilerini günceller"""
        if not kwargs:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [tc_no]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE patients 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE tc_no = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    # Doktor işlemleri
    def add_doctor(self, diploma_no, name, specialty=None, hospital=None, phone=None):
        """Yeni doktor ekler"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO doctors (diploma_no, name, specialty, hospital, phone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (diploma_no, name, specialty, hospital, phone))
                conn.commit()
                logger.info(f"Yeni doktor eklendi: {name} ({diploma_no})")
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.warning(f"Doktor zaten mevcut: {diploma_no}")
                return None
    
    def get_doctor(self, diploma_no):
        """Doktor bilgilerini getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM doctors WHERE diploma_no = ?', (diploma_no,))
            return cursor.fetchone()
    
    # Reçete işlemleri
    def add_prescription(self, prescription_id, patient_tc, doctor_diploma_no, 
                        hospital, prescription_date, diagnosis_code=None, 
                        diagnosis_description=None, total_amount=None):
        """Yeni reçete ekler"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO prescriptions 
                    (prescription_id, patient_tc, doctor_diploma_no, hospital, 
                     prescription_date, diagnosis_code, diagnosis_description, total_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (prescription_id, patient_tc, doctor_diploma_no, hospital,
                      prescription_date, diagnosis_code, diagnosis_description, total_amount))
                conn.commit()
                logger.info(f"Yeni reçete eklendi: {prescription_id}")
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.warning(f"Reçete zaten mevcut: {prescription_id}")
                return None
    
    def get_prescription(self, prescription_id):
        """Reçete bilgilerini getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, 
                       pt.name as patient_name,
                       d.name as doctor_name
                FROM prescriptions p
                LEFT JOIN patients pt ON p.patient_tc = pt.tc_no
                LEFT JOIN doctors d ON p.doctor_diploma_no = d.diploma_no
                WHERE p.prescription_id = ?
            ''', (prescription_id,))
            return cursor.fetchone()
    
    def update_prescription_status(self, prescription_id, status):
        """Reçete durumunu günceller"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prescriptions 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE prescription_id = ?
            ''', (status, prescription_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_pending_prescriptions(self, limit=50):
        """Bekleyen reçeteleri getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, 
                       pt.name as patient_name,
                       d.name as doctor_name
                FROM prescriptions p
                LEFT JOIN patients pt ON p.patient_tc = pt.tc_no
                LEFT JOIN doctors d ON p.doctor_diploma_no = d.diploma_no
                WHERE p.status = 'pending'
                ORDER BY p.created_at ASC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    
    # İlaç işlemleri
    def add_medication(self, barcode, name, active_ingredient=None, dosage=None,
                      form=None, manufacturer=None, sut_code=None, price=None):
        """Yeni ilaç ekler"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO medications 
                    (barcode, name, active_ingredient, dosage, form, manufacturer, sut_code, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (barcode, name, active_ingredient, dosage, form, manufacturer, sut_code, price))
                conn.commit()
                logger.info(f"Yeni ilaç eklendi: {name} ({barcode})")
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.warning(f"İlaç zaten mevcut: {barcode}")
                return None
    
    def get_medication(self, barcode):
        """İlaç bilgilerini getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medications WHERE barcode = ?', (barcode,))
            return cursor.fetchone()
    
    # AI Karar işlemleri
    def save_ai_decision(self, prescription_id, decision, reason, confidence,
                        risk_factors=None, recommendations=None, ai_model="gpt-4"):
        """AI kararını kaydeder"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_decisions 
                (prescription_id, decision, reason, confidence, risk_factors, 
                 recommendations, ai_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (prescription_id, decision, reason, confidence,
                  json.dumps(risk_factors) if risk_factors else None,
                  json.dumps(recommendations) if recommendations else None,
                  ai_model))
            conn.commit()
            logger.info(f"AI kararı kaydedildi: {prescription_id} -> {decision}")
            return cursor.lastrowid
    
    def get_ai_decision(self, prescription_id):
        """AI kararını getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ai_decisions 
                WHERE prescription_id = ? 
                ORDER BY decision_time DESC 
                LIMIT 1
            ''', (prescription_id,))
            return cursor.fetchone()
    
    # İstatistik işlemleri
    def get_statistics(self):
        """Sistem istatistiklerini getirir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Toplam reçete sayısı
            cursor.execute('SELECT COUNT(*) FROM prescriptions')
            stats['total_prescriptions'] = cursor.fetchone()[0]
            
            # Durum bazında reçete sayıları
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM prescriptions 
                GROUP BY status
            ''')
            stats['prescriptions_by_status'] = dict(cursor.fetchall())
            
            # AI karar dağılımı
            cursor.execute('''
                SELECT decision, COUNT(*) 
                FROM ai_decisions 
                GROUP BY decision
            ''')
            stats['ai_decisions'] = dict(cursor.fetchall())
            
            # Ortalama güven skoru
            cursor.execute('SELECT AVG(confidence) FROM ai_decisions')
            avg_confidence = cursor.fetchone()[0]
            stats['average_confidence'] = float(avg_confidence) if avg_confidence else 0.0
            
            return stats
    
    def log_system_event(self, level, module, message, data=None):
        """Sistem olayını loglar"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (log_level, module, message, data)
                VALUES (?, ?, ?, ?)
            ''', (level, module, message, json.dumps(data) if data else None))
            conn.commit()


# Veritabanı yardımcı fonksiyonları
def get_db_manager():
    """Singleton database manager döndürür"""
    if not hasattr(get_db_manager, 'instance'):
        get_db_manager.instance = DatabaseManager()
    return get_db_manager.instance