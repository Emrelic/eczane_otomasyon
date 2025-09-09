# -*- coding: utf-8 -*-
"""
SQLite Database Handler
Simple database operations for prescription storage
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

class SQLiteHandler:
    """SQLite database handler for prescription storage"""
    
    def __init__(self, db_path="database/prescriptions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._initialize_database()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recete_no TEXT UNIQUE NOT NULL,
                    hasta_tc TEXT,
                    hasta_ad TEXT,
                    hasta_soyad TEXT,
                    prescription_data TEXT,
                    analysis_result TEXT,
                    decision TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recete_no TEXT,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE')):
                    conn.commit()
                    return cursor.rowcount
                else:
                    return cursor.fetchall()
                    
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    def save_prescription(self, prescription_data, analysis_result=None, decision=None):
        """Save prescription to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO prescriptions 
                    (recete_no, hasta_tc, hasta_ad, hasta_soyad, prescription_data, analysis_result, decision)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prescription_data.get('recete_no'),
                    prescription_data.get('hasta_tc'),
                    prescription_data.get('hasta_ad'),
                    prescription_data.get('hasta_soyad'),
                    json.dumps(prescription_data, ensure_ascii=False),
                    json.dumps(analysis_result, ensure_ascii=False) if analysis_result else None,
                    decision
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Database save error: {e}")
            return False
    
    def get_prescription(self, recete_no):
        """Get prescription by recete_no"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM prescriptions WHERE recete_no = ?", 
                    (recete_no,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Database get error: {e}")
            return None
    
    def get_all_prescriptions(self, limit=100):
        """Get all prescriptions with limit"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM prescriptions ORDER BY created_at DESC LIMIT ?", 
                    (limit,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database getall error: {e}")
            return []
    
    def log_processing(self, recete_no, action, details):
        """Log processing action"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO processing_logs (recete_no, action, details)
                    VALUES (?, ?, ?)
                """, (recete_no, action, details))
                conn.commit()
        except Exception as e:
            logger.error(f"Logging error: {e}")