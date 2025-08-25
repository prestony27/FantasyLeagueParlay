from typing import List, Tuple, Optional

class ParlayCalculator:
    
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
        if not odds_list:
            return 0.0
            
        decimal_odds = 1.0
        for symbol, value in odds_list:
            if symbol and value:
                american_odds = value if symbol == '+' else -value
                decimal_odds *= self.american_to_decimal(american_odds)
        return decimal_odds
    
    def calculate_payout(self, wager_amount: float, decimal_odds: float) -> float:
        """Calculate potential payout (total return including original wager)"""
        return wager_amount * decimal_odds
    
    def calculate_profit(self, wager_amount: float, decimal_odds: float) -> float:
        """Calculate profit (payout minus original wager)"""
        return (wager_amount * decimal_odds) - wager_amount
    
    def format_american_odds(self, symbol: str, value: int) -> str:
        """Format odds for display (+150, -110)"""
        if not symbol or not value:
            return ""
        return f"{symbol}{value}"
    
    def validate_odds_input(self, symbol: str, value: Optional[int]) -> bool:
        """Validate that odds input is properly formatted"""
        if not symbol or not value:
            return False
        if symbol not in ['+', '-']:
            return False
        if value < 100:
            return False
        return True