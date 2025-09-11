from datetime import datetime, timedelta
import calendar

APP_TITLE = "10-Leg Parlay Dashboard"
WAGER_AMOUNT = 10.00
NUM_WEEKS = 15
NUM_WAGERS_PER_WEEK = 10

USERS = [
    "A.J. Wolfe",
    "Clark Lee", 
    "Clayton Horan",
    "Kyle Francis",
    "Preston 'OP' Browne",
    "Preston Young",
    "Tanner Nordeen",
    "Teddy MacDonell",
    "Trask Bottum",
    "Zaq Levick"
]

# Google Sheets configuration will be handled via Streamlit secrets

CURRENCY_FORMAT = "${:,.2f}"
ODDS_FORMAT = "{}{}"

STATUS_COLORS = {
    'pending': '#FFF3CD',
    'won': '#D4EDDA', 
    'lost': '#F8D7DA',
    'push': '#D1ECF1'
}

STATUS_OPTIONS = ['pending', 'won', 'lost', 'push']

def get_current_nfl_week():
    """
    Calculate current NFL week based on date.
    NFL season starts first Tuesday in September, each week starts Tuesday.
    """
    today = datetime.now()
    current_year = today.year
    
    # Find first Tuesday in September
    september_first = datetime(current_year, 9, 1)
    days_until_tuesday = (1 - september_first.weekday()) % 7
    first_tuesday = september_first + timedelta(days=days_until_tuesday)
    
    # If we're before the season starts, default to Week 1
    if today < first_tuesday:
        return 1
    
    # Calculate weeks since season started
    days_since_start = (today - first_tuesday).days
    week = (days_since_start // 7) + 1
    
    # Cap at 15 weeks
    return min(week, NUM_WEEKS)