import gspread
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
from google.oauth2.service_account import Credentials
from config import USERS

class DataManager:
    
    def __init__(self):
        self.users = USERS
        self.gc = None
        self.sheet = None
        self._cache = {}  # Simple cache for API responses
        self._cache_time = {}  # Track cache timestamps
        self.init_google_sheets()
    
    def init_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Try to get credentials from Streamlit secrets first, but catch all errors
            secrets_worked = False
            try:
                # Check if we're in Streamlit Cloud environment
                if hasattr(st, 'secrets'):
                    # Try to access secrets - this might raise an error
                    secrets_dict = dict(st.secrets)
                    if 'gcp_service_account' in secrets_dict:
                        credentials = Credentials.from_service_account_info(
                            st.secrets["gcp_service_account"],
                            scopes=[
                                "https://www.googleapis.com/auth/spreadsheets",
                                "https://www.googleapis.com/auth/drive"
                            ]
                        )
                        self.gc = gspread.authorize(credentials)
                        secrets_worked = True
            except Exception:
                # Any exception means we should try local files
                secrets_worked = False
            
            # If secrets didn't work, try local files
            if not secrets_worked:
                try:
                    self.gc = gspread.service_account(filename='service_account.json')
                except FileNotFoundError:
                        st.error("Google Sheets credentials not found. Please check setup instructions.")
                        return
            
            # Try to open existing sheet or create new one
            sheet_name = "Fantasy League Parlay Data"
            try:
                self.spreadsheet = self.gc.open(sheet_name)
                self.sheet = self.spreadsheet.sheet1
                st.success(f"Connected to existing Google Sheet: {self.spreadsheet.url}")
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                self.spreadsheet = self.gc.create(sheet_name)
                self.sheet = self.spreadsheet.sheet1
                # Initialize headers
                headers = ['Week', 'Position', 'User', 'Moneyline_Symbol', 'Moneyline_Value', 'Wager_Detail', 'Status', 'Updated_At']
                self.sheet.append_row(headers)
                st.success(f"Created new Google Sheet: {self.spreadsheet.url}")
                st.info("📝 Bookmark this URL to easily access your data!")
                
        except Exception as e:
            st.error(f"Failed to initialize Google Sheets: {e}")
    
    def load_week_wagers(self, week_num: int) -> pd.DataFrame:
        """Load all wagers for a specific week from Google Sheets"""
        if not self.sheet:
            return self._get_default_wagers_df(week_num)
        
        # Check cache first (cache for 30 seconds)
        cache_key = f"week_{week_num}"
        current_time = datetime.now().timestamp()
        
        if (cache_key in self._cache and 
            cache_key in self._cache_time and
            current_time - self._cache_time[cache_key] < 30):
            return self._cache[cache_key].copy()
        
        try:
            # Get all data from sheet
            all_data = self.sheet.get_all_records()
            df = pd.DataFrame(all_data)
            
            # Filter for the specific week
            if not df.empty and 'Week' in df.columns:
                week_df = df[df['Week'] == week_num].copy()
                
                # Rename columns to match expected format
                if not week_df.empty:
                    week_df = week_df.rename(columns={
                        'Week': 'week_number',
                        'Position': 'position', 
                        'User': 'user',
                        'Moneyline_Symbol': 'moneyline_symbol',
                        'Moneyline_Value': 'moneyline_value',
                        'Wager_Detail': 'wager_detail',
                        'Status': 'status',
                        'Updated_At': 'updated_at'
                    })
                    week_df = week_df.sort_values('position')
                else:
                    week_df = pd.DataFrame()
            else:
                week_df = pd.DataFrame()
            
            # Check if we need to apply default wagers
            # We should use saved data if we have meaningful wager data (not just users)
            needs_defaults = True
            if not week_df.empty and len(week_df) >= 10:
                # Check if we have actual wager data (users AND moneyline values)
                has_meaningful_data = False
                for _, row in week_df.iterrows():
                    user_val = row.get('user', '')
                    moneyline_val = row.get('moneyline_value', '')
                    if (pd.notna(user_val) and str(user_val).strip() != '' and
                        pd.notna(moneyline_val) and str(moneyline_val).strip() != ''):
                        has_meaningful_data = True
                        break
                needs_defaults = not has_meaningful_data
                
                # If we have meaningful data, ensure we have all 10 positions
                if not needs_defaults:
                    # Fill in any missing positions with empty data
                    all_positions = set(range(1, 11))
                    existing_positions = set(week_df['position'].astype(int))
                    missing_positions = all_positions - existing_positions
                    
                    if missing_positions:
                        # Add missing positions as empty rows
                        missing_rows = []
                        for pos in missing_positions:
                            missing_rows.append({
                                'week_number': week_num,
                                'position': pos,
                                'user': '',
                                'moneyline_symbol': '',
                                'moneyline_value': '',
                                'wager_detail': '',
                                'status': 'pending',
                                'updated_at': ''
                            })
                        week_df = pd.concat([week_df, pd.DataFrame(missing_rows)], ignore_index=True)
                        week_df = week_df.sort_values('position')
            
            if needs_defaults:
                result = self._get_default_wagers_df(week_num)
            else:
                result = week_df
            
            # Cache the result
            self._cache[cache_key] = result.copy()
            self._cache_time[cache_key] = current_time
            
            return result
            
        except Exception as e:
            st.error(f"Error loading data from Google Sheets: {e}")
            return self._get_default_wagers_df(week_num)
    
    def _get_default_wagers_df(self, week_num: int) -> pd.DataFrame:
        """Generate default wagers dataframe"""
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
        
        return pd.DataFrame({
            'week_number': [week_num] * 10,
            'position': list(range(1, 11)),
            'user': [wager[0] for wager in default_wagers],
            'moneyline_symbol': ['-'] * 10,
            'moneyline_value': [110] * 10,
            'wager_detail': [wager[1] for wager in default_wagers],
            'status': ['pending'] * 10,
            'updated_at': [None] * 10
        })
    
    def save_wager(self, week_num: int, position: int, wager_data: Dict):
        """Save or update a single wager in Google Sheets"""
        wagers_list = [dict(wager_data, position=position)]
        self.save_all_week_wagers(week_num, wagers_list)
    
    def save_all_week_wagers(self, week_num: int, wagers_list: List[Dict]):
        """Save all wagers for a week to Google Sheets"""
        if not self.sheet:
            st.error("Google Sheets not initialized")
            return
        
        try:
            # First, remove existing data for this week
            self.clear_week(week_num)
            
            # Clear cache for this week since we're updating data
            cache_key = f"week_{week_num}"
            if cache_key in self._cache:
                del self._cache[cache_key]
            if cache_key in self._cache_time:
                del self._cache_time[cache_key]
            
            # Prepare rows to append
            rows_to_add = []
            for wager_data in wagers_list:
                row = [
                    week_num,
                    wager_data.get('position'),
                    wager_data.get('user') or '',
                    wager_data.get('moneyline_symbol') or '',
                    wager_data.get('moneyline_value') or '',
                    wager_data.get('wager_detail') or '',
                    wager_data.get('status') or 'pending',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                rows_to_add.append(row)
            
            # Append all rows at once
            if rows_to_add:
                self.sheet.append_rows(rows_to_add)
            
        except Exception as e:
            st.error(f"Error saving to Google Sheets: {e}")
    
    def clear_week(self, week_num: int):
        """Clear all wagers for a week from Google Sheets"""
        if not self.sheet:
            return
        
        try:
            # Get all data and find rows to delete
            all_data = self.sheet.get_all_values()
            rows_to_delete = []
            
            # Skip header row (row 1) - only delete data rows
            for i, row in enumerate(all_data[1:], start=2):
                if row and len(row) > 0 and str(row[0]) == str(week_num):
                    rows_to_delete.append(i)
            
            # Delete rows in reverse order to maintain indices
            for row_num in reversed(rows_to_delete):
                self.sheet.delete_rows(row_num)
                
        except Exception as e:
            st.error(f"Error clearing week data: {e}")
    
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