"""
Live Bet Builder
Analyze upcoming matches for betting opportunities
"""

from typing import Dict
from .backtest import BacktestAnalyzer, print_backtest_analysis


class LiveBetBuilder(BacktestAnalyzer):
    """
    Live bet builder - same as backtest but without gameweek filtering
    """
    
    def analyze_upcoming_match(self, league_key: str, season_id: int, match_id: int) -> Dict:
        """
        Analyze upcoming match using all available data
        
        Args:
            league_key: League identifier
            season_id: Season ID
            match_id: Match ID to analyze
        
        Returns:
            Complete analysis dict with predictions (no actuals)
        """
        # Use parent's analyze_match but without gameweek limit
        # Pass a very high gameweek number to effectively disable filtering
        return self.analyze_match(league_key, season_id, match_id, target_gameweek=999)


def print_live_analysis(analysis: Dict):
    """Print live analysis (no actual results)"""
    print_backtest_analysis(analysis, is_backtest=False)