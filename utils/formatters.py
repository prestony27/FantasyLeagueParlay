from config import STATUS_COLORS, CURRENCY_FORMAT

def format_moneyline(symbol: str, value: int) -> str:
    """Format moneyline for display"""
    if not symbol or not value:
        return ""
    return f"{symbol}{value}"

def format_currency(amount: float) -> str:
    """Format currency for display"""
    return CURRENCY_FORMAT.format(amount)

def get_row_color(status: str) -> str:
    """Get color based on wager status"""
    return STATUS_COLORS.get(status, '#FFFFFF')

def format_decimal_odds(odds: float) -> str:
    """Format decimal odds for display"""
    if odds <= 1:
        return "0.00"
    return f"{odds:.2f}"

def get_status_emoji(status: str) -> str:
    """Get emoji based on wager status"""
    status_emojis = {
        'pending': '⏳',
        'won': '✅',
        'lost': '❌',
        'push': '🟡'
    }
    return status_emojis.get(status, '⏳')

def format_wager_summary(position: int, user: str, detail: str, odds_str: str, status: str) -> str:
    """Format a single wager for summary display"""
    emoji = get_status_emoji(status)
    if user and detail and odds_str:
        return f"{emoji} {position}. {user}: {detail} ({odds_str})"
    elif user and detail:
        return f"{emoji} {position}. {user}: {detail}"
    elif user:
        return f"{emoji} {position}. {user}: (No details)"
    else:
        return f"{emoji} {position}. (Empty)"