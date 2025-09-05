import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import os
from config import USERS, DB_PATH

class DataManager:
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.users = USERS
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wagers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                position INTEGER NOT NULL CHECK (position BETWEEN 1 AND 10),
                user TEXT,
                moneyline_symbol TEXT CHECK (moneyline_symbol IN ('+', '-', NULL)),
                moneyline_value INTEGER,
                wager_detail TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(week_number, position)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for i, user in enumerate(self.users, 1):
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, display_name) 
                VALUES (?, ?)
            ''', (f"user_{i}", user))
        
        conn.commit()
        conn.close()
    
    def load_week_wagers(self, week_num: int) -> pd.DataFrame:
        """Load all wagers for a specific week"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT week_number, position, user, moneyline_symbol, 
                   moneyline_value, wager_detail, status, updated_at
            FROM wagers 
            WHERE week_number = ?
            ORDER BY position
        '''
        
        df = pd.read_sql_query(query, conn, params=(week_num,))
        conn.close()
        
        # Check if we need to apply default wagers (empty dataframe or no users assigned)
        needs_defaults = df.empty or df['user'].isna().all() or (df['user'] == '').all()
        
        if needs_defaults:
            # Default wager combinations
            default_wagers = [
                ("A.J. Wolfe", "Joe Burrow over X passing yards"),
                ("Clark Lee", "Lamar Jackson over X passing yards"),
                ("Clayton Horan", "C.J. Stroud over X passing yards"),
                ("Kyle Francis", "Brock Purdy over X passing yards"),
                ("Preston 'OP' Browne", "Bo Nix over X passing yards"),
                ("Preston Young", "Patrick Mahomes over X passing yards"),
                ("Tanner Nordeen", "Jalen Hurts over X passing yards"),
                ("Teddy MacDonell", "Jayden Daniels over X passing yards"),
                ("Trask Bottum", "Baker Mayfield over X passing yards"),
                ("Zaq Levick", "Josh Allen over X passing yards")
            ]
            
            df = pd.DataFrame({
                'week_number': [week_num] * 10,
                'position': list(range(1, 11)),
                'user': [wager[0] for wager in default_wagers],
                'moneyline_symbol': ['-'] * 10,
                'moneyline_value': [110] * 10,
                'wager_detail': [wager[1] for wager in default_wagers],
                'status': ['pending'] * 10,
                'updated_at': [None] * 10
            })
        
        return df
    
    def save_wager(self, week_num: int, position: int, wager_data: Dict):
        """Save or update a single wager"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO wagers 
            (week_number, position, user, moneyline_symbol, moneyline_value, 
             wager_detail, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            week_num,
            position,
            wager_data.get('user'),
            wager_data.get('moneyline_symbol'),
            wager_data.get('moneyline_value'),
            wager_data.get('wager_detail', ''),
            wager_data.get('status', 'pending'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def save_all_week_wagers(self, week_num: int, wagers_list: List[Dict]):
        """Save all wagers for a week at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for wager_data in wagers_list:
            cursor.execute('''
                INSERT OR REPLACE INTO wagers 
                (week_number, position, user, moneyline_symbol, moneyline_value, 
                 wager_detail, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                week_num,
                wager_data.get('position'),
                wager_data.get('user') if wager_data.get('user') else None,
                wager_data.get('moneyline_symbol') if wager_data.get('moneyline_symbol') else None,
                wager_data.get('moneyline_value') if wager_data.get('moneyline_value') else None,
                wager_data.get('wager_detail', ''),
                wager_data.get('status', 'pending'),
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
    
    def clear_week(self, week_num: int):
        """Clear all wagers for a week"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM wagers WHERE week_number = ?', (week_num,))
        
        conn.commit()
        conn.close()
    
    def export_week_data(self, week_num: int) -> pd.DataFrame:
        """Export week data for download"""
        return self.load_week_wagers(week_num)
    
    def copy_week_wagers(self, from_week: int, to_week: int):
        """Copy wagers from one week to another"""
        from_data = self.load_week_wagers(from_week)
        
        if not from_data.empty and from_data['user'].notna().any():
            wagers_to_copy = []
            for _, row in from_data.iterrows():
                if pd.notna(row['user']) and row['user']:
                    wagers_to_copy.append({
                        'position': row['position'],
                        'user': row['user'],
                        'moneyline_symbol': row['moneyline_symbol'],
                        'moneyline_value': row['moneyline_value'],
                        'wager_detail': row['wager_detail'],
                        'status': 'pending'
                    })
            
            if wagers_to_copy:
                self.save_all_week_wagers(to_week, wagers_to_copy)