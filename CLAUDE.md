# Streamlit 10-Leg Parlay Dashboard - Implementation Blueprint

## Project Overview
A Streamlit-based dashboard for managing a 10-leg parlay sports wager system where 10 users each select one sports wager. The dashboard tracks 15 weeks of NFL season with persistent data storage.

## Why Streamlit?
- **Simple deployment**: Single Python file can run the entire application
- **Built-in UI components**: Tabs, forms, dropdowns, tables ready to use
- **Session state management**: Perfect for tracking wager changes
- **Easy data persistence**: Works great with CSV/SQLite for data storage
- **Rapid development**: No separate frontend/backend needed

## Project Structure (Simple)
```
parlay-dashboard/
├── app.py                    # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── calculator.py         # Parlay odds calculations
│   ├── data_manager.py       # Data persistence (CSV/SQLite)
│   └── formatters.py         # Display formatting utilities
├── data/
│   ├── users.csv            # User list
│   ├── wagers.db            # SQLite database for wager data
│   └── backups/             # Weekly backups
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── README.md
```

## Core Components

### 1. Main Application (app.py)
```python
import streamlit as st
import pandas as pd
from utils.calculator import ParlayCalculator
from utils.data_manager import DataManager
from utils.formatters import format_moneyline, format_currency

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="10-Leg Parlay Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🏈 10-Leg Parlay Dashboard")
    
    # Week selection tabs
    week_tabs = st.tabs([f"Week {i}" for i in range(1, 16)])
    
    for week_num, tab in enumerate(week_tabs, 1):
        with tab:
            render_week_dashboard(week_num)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    if 'calculator' not in st.session_state:
        st.session_state.calculator = ParlayCalculator()
    if 'current_week' not in st.session_state:
        st.session_state.current_week = 1

def render_week_dashboard(week_num):
    """Render dashboard for a specific week"""
    
    # Load data for this week
    wagers = st.session_state.data_manager.load_week_wagers(week_num)
    
    # Parlay summary section
    render_parlay_summary(wagers)
    
    # Wager entry section
    render_wager_grid(week_num, wagers)
    
    # Action buttons
    render_action_buttons(week_num)
```

### 2. Data Manager (utils/data_manager.py)
```python
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

class DataManager:
    """Handles all data persistence operations"""
    
    def __init__(self, db_path: str = "data/wagers.db"):
        self.db_path = db_path
        self.users = self.load_users()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables"""
        # Create wagers table
        # week_number, position, user, moneyline_symbol, 
        # moneyline_value, wager_detail, status, created_at, updated_at
        
    def load_users(self) -> List[str]:
        """Load user list from CSV"""
        # Return list of 10 users
        
    def load_week_wagers(self, week_num: int) -> pd.DataFrame:
        """Load all wagers for a specific week"""
        
    def save_wager(self, week_num: int, position: int, wager_data: Dict):
        """Save or update a single wager"""
        
    def clear_week(self, week_num: int):
        """Clear all wagers for a week"""
        
    def export_week_data(self, week_num: int) -> pd.DataFrame:
        """Export week data for download"""
```

### 3. Parlay Calculator (utils/calculator.py)
```python
from typing import List, Tuple
import math

class ParlayCalculator:
    """Handles all parlay calculations"""
    
    def american_to_decimal(self, american_odds: int) -> float:
        """
        Convert American odds to decimal odds
        +150 -> 2.50
        -150 -> 1.667
        """
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def calculate_parlay_odds(self, odds_list: List[Tuple[str, int]]) -> float:
        """
        Calculate combined parlay odds
        Input: [('+', 150), ('-', 110), ...]
        Output: Combined decimal odds
        """
        decimal_odds = 1.0
        for symbol, value in odds_list:
            american_odds = value if symbol == '+' else -value
            decimal_odds *= self.american_to_decimal(american_odds)
        return decimal_odds
    
    def calculate_payout(self, wager_amount: float, decimal_odds: float) -> float:
        """Calculate potential payout"""
        return wager_amount * decimal_odds
    
    def format_american_odds(self, symbol: str, value: int) -> str:
        """Format odds for display (+150, -110)"""
        return f"{symbol}{value}"
```

### 4. Display Formatters (utils/formatters.py)
```python
def format_moneyline(symbol: str, value: int) -> str:
    """Format moneyline for display"""
    return f"{symbol}{value}" if symbol and value else ""

def format_currency(amount: float) -> str:
    """Format currency for display"""
    return f"${amount:,.2f}"

def get_row_color(status: str) -> str:
    """Get color based on wager status"""
    colors = {
        'pending': '#FFF3CD',
        'won': '#D4EDDA',
        'lost': '#F8D7DA',
        'push': '#D1ECF1'
    }
    return colors.get(status, '#FFFFFF')
```

## UI Components Detail

### Parlay Summary Section
```python
def render_parlay_summary(wagers: pd.DataFrame):
    """Render the parlay summary at the top of the dashboard"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Wager Amount", "$10.00")
    
    with col2:
        # Calculate and display potential payout
        if not wagers.empty and all(wagers['moneyline_value'].notna()):
            odds_list = list(zip(wagers['moneyline_symbol'], 
                               wagers['moneyline_value']))
            decimal_odds = st.session_state.calculator.calculate_parlay_odds(odds_list)
            payout = st.session_state.calculator.calculate_payout(10, decimal_odds)
            st.metric("Potential Payout", format_currency(payout))
        else:
            st.metric("Potential Payout", "$0.00")
    
    with col3:
        # Show parlay odds
        st.metric("Parlay Odds", f"{decimal_odds:.2f}" if decimal_odds else "0.00")
    
    with col4:
        # Show completion status
        completed = len(wagers[wagers['user'].notna()])
        st.metric("Wagers Completed", f"{completed}/10")
```

### Wager Grid Section
```python
def render_wager_grid(week_num: int, wagers: pd.DataFrame):
    """Render the 10-row wager entry grid"""
    
    st.subheader("Wager Selections")
    
    # Create a form for batch updates
    with st.form(f"week_{week_num}_wagers"):
        
        # Header row
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 3, 2, 1])
        col1.write("**#**")
        col2.write("**+/-**")
        col3.write("**Odds**")
        col4.write("**Wager Detail**")
        col5.write("**User**")
        col6.write("**Status**")
        
        # Create 10 wager rows
        wager_inputs = []
        for i in range(1, 11):
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 3, 2, 1])
            
            # Get existing data if available
            existing = wagers[wagers['position'] == i].iloc[0] if len(wagers[wagers['position'] == i]) > 0 else None
            
            with col1:
                st.write(f"{i}")
            
            with col2:
                symbol = st.selectbox(
                    f"Symbol {i}", 
                    options=['', '+', '-'],
                    index=['', '+', '-'].index(existing['moneyline_symbol']) if existing and existing['moneyline_symbol'] else 0,
                    key=f"symbol_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            with col3:
                odds_value = st.number_input(
                    f"Odds {i}",
                    min_value=100,
                    max_value=9999,
                    value=int(existing['moneyline_value']) if existing and existing['moneyline_value'] else 100,
                    key=f"odds_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            with col4:
                detail = st.text_input(
                    f"Detail {i}",
                    value=existing['wager_detail'] if existing else "",
                    key=f"detail_{week_num}_{i}",
                    placeholder="e.g., Chiefs -3.5, Over 47.5",
                    label_visibility="collapsed"
                )
            
            with col5:
                user = st.selectbox(
                    f"User {i}",
                    options=[''] + st.session_state.data_manager.users,
                    index=0,  # Will be set based on existing data
                    key=f"user_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            with col6:
                status = st.selectbox(
                    f"Status {i}",
                    options=['pending', 'won', 'lost', 'push'],
                    index=0,
                    key=f"status_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            wager_inputs.append({
                'position': i,
                'moneyline_symbol': symbol,
                'moneyline_value': odds_value,
                'wager_detail': detail,
                'user': user,
                'status': status
            })
        
        # Submit button
        submitted = st.form_submit_button("Save All Wagers", type="primary", use_container_width=True)
        
        if submitted:
            save_all_wagers(week_num, wager_inputs)
            st.success(f"Week {week_num} wagers saved!")
            st.rerun()
```

### Action Buttons Section
```python
def render_action_buttons(week_num: int):
    """Render action buttons for the week"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"Clear Week {week_num}", type="secondary"):
            if st.confirm("Are you sure you want to clear all wagers for this week?"):
                st.session_state.data_manager.clear_week(week_num)
                st.success(f"Week {week_num} cleared!")
                st.rerun()
    
    with col2:
        if st.button(f"Copy from Previous Week"):
            # Copy logic here
            pass
    
    with col3:
        if st.button(f"Export Week {week_num}"):
            df = st.session_state.data_manager.export_week_data(week_num)
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name=f"week_{week_num}_wagers.csv",
                mime="text/csv"
            )
    
    with col4:
        if st.button(f"Calculate Summary"):
            # Force recalculation
            st.rerun()
```

## Database Schema (SQLite)

```sql
CREATE TABLE wagers (
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
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration (config.py)

```python
# Configuration settings for the application

# Application settings
APP_TITLE = "10-Leg Parlay Dashboard"
WAGER_AMOUNT = 10.00
NUM_WEEKS = 15
NUM_WAGERS_PER_WEEK = 10

# User list (can be modified)
USERS = [
    "User 1",
    "User 2", 
    "User 3",
    "User 4",
    "User 5",
    "User 6",
    "User 7",
    "User 8",
    "User 9",
    "User 10"
]

# Database settings
DB_PATH = "data/wagers.db"
BACKUP_PATH = "data/backups/"

# Display settings
CURRENCY_FORMAT = "${:,.2f}"
ODDS_FORMAT = "{}{}"

# Status colors
STATUS_COLORS = {
    'pending': '#FFF3CD',
    'won': '#D4EDDA', 
    'lost': '#F8D7DA',
    'push': '#D1ECF1'
}
```

## Streamlit Configuration (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

## Requirements.txt

```
streamlit==1.28.0
pandas==2.1.0
sqlite3  # Built-in with Python
python-dateutil==2.8.2
```

## Implementation Steps for Claude Code

### Step 1: Create Project Structure
```bash
mkdir parlay-dashboard
cd parlay-dashboard
mkdir utils data .streamlit
touch app.py config.py requirements.txt README.md
touch utils/__init__.py utils/calculator.py utils/data_manager.py utils/formatters.py
```

### Step 2: Implement Core Components
1. Start with `config.py` - define all constants
2. Implement `utils/calculator.py` - parlay calculation logic
3. Implement `utils/data_manager.py` - data persistence
4. Implement `utils/formatters.py` - display utilities
5. Build `app.py` - main Streamlit application

### Step 3: Test Basic Functionality
1. Create test data for users
2. Test wager entry and saving
3. Verify parlay calculations
4. Test week navigation

### Step 4: Add Enhanced Features
1. Add data validation
2. Implement copy from previous week
3. Add export functionality
4. Create backup system

### Step 5: Polish UI
1. Add custom CSS styling
2. Improve responsive layout
3. Add confirmation dialogs
4. Implement success/error messages

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# The dashboard will be available at http://localhost:8501
```

## Key Features Summary

✅ **10 Wager Rows**: Each with position, moneyline, detail, user dropdown
✅ **15 Week Tabs**: Easy navigation between weeks
✅ **Parlay Calculation**: Automatic calculation of combined odds and payout
✅ **Data Persistence**: SQLite database for reliable storage
✅ **User Management**: Dropdown selection from 10 predefined users
✅ **Export Functionality**: Download week data as CSV
✅ **Visual Feedback**: Color-coded status indicators
✅ **Responsive Design**: Works on desktop and tablet

## Future API Integration (Phase 2)

Once the basic dashboard is working, integrate The Odds API:

1. Add API configuration to `config.py`
2. Create `utils/odds_api.py` for API client
3. Add "Import from API" button to wager rows
4. Implement automatic grading using scores endpoint
5. Add real-time odds updates

## Notes for Claude Code

- Start with a working minimal version, then add features incrementally
- Use Streamlit's session state to manage data between reruns
- Implement proper error handling for database operations
- Use Streamlit's built-in components wherever possible (no custom HTML/CSS initially)
- Test with mock data before implementing real user workflow
- Keep the UI simple and focused on functionality first

This blueprint provides a clear path to build a functional 10-leg parlay dashboard using Streamlit, without the complexity of a full web application stack.