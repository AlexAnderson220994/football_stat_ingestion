"""
Team Quality Analyzer
Calculates comprehensive quality ratings based on multiple factors
"""

from typing import Dict, List, Optional
from .utils import calculate_percentage, safe_divide, get_match_result, is_home_team, filter_matches_before_gameweek, is_completed_match


class TeamQualityAnalyzer:
    """
    Analyzes team quality based on:
    - League position
    - Recent form (last 6 matches)
    - Home/Away performance split
    - Opposition quality faced
    - Momentum trends
    """
    
    def __init__(self, league_table: dict, all_fixtures: list, team_id: int, 
                 max_gameweek: Optional[int] = None):
        """
        Args:
            league_table: League table data
            all_fixtures: All team fixtures (will be filtered by max_gameweek)
            team_id: Team ID to analyze
            max_gameweek: Maximum gameweek to include (for backtesting)
        """
        self.team_id = team_id
        self.max_gameweek = max_gameweek
        
        # Filter fixtures if backtesting
        if max_gameweek:
            self.fixtures = [f for f in all_fixtures 
                           if is_completed_match(f) and 
                           filter_matches_before_gameweek([f], max_gameweek)]
        else:
            self.fixtures = [f for f in all_fixtures if is_completed_match(f)]
        
        # Extract team info from league table
        self.team_info = self._find_team_in_table(league_table)
        
    def _find_team_in_table(self, league_table: dict) -> Optional[dict]:
        """Find team in league table"""
        data = league_table.get('data', {})
        
        # Handle different table structures
        league_table_list = data.get('league_table', [])
        
        if league_table_list:
            for team in league_table_list:
                if team.get('id') == self.team_id:
                    return team
        
        # Check specific_tables for tournament formats
        specific_tables = data.get('specific_tables', [])
        for round_data in specific_tables:
            if round_data.get('table'):
                for team in round_data['table']:
                    if team.get('id') == self.team_id:
                        return team
            
            if round_data.get('groups'):
                for group in round_data['groups']:
                    if group.get('table'):
                        for team in group['table']:
                            if team.get('id') == self.team_id:
                                return team
        
        return None
    
    def calculate_quality_rating(self, is_home: bool = True) -> int:
        """
        Calculate overall quality rating (0-100)
        
        Args:
            is_home: Whether calculating for home or away performance
        
        Returns:
            Quality rating 0-100
        """
        if not self.team_info or not self.fixtures:
            return 50  # Default mid-table
        
        # Component ratings
        position_rating = self._calculate_position_rating()
        form_rating = self._calculate_form_rating(is_home)
        venue_rating = self._calculate_venue_rating(is_home)
        momentum_rating = self._calculate_momentum_rating()
        opposition_rating = self._calculate_opposition_quality_rating()
        
        # Weighted combination
        weights = {
            'position': 0.30,
            'form': 0.25,
            'venue': 0.20,
            'momentum': 0.15,
            'opposition': 0.10
        }
        
        overall = (
            position_rating * weights['position'] +
            form_rating * weights['form'] +
            venue_rating * weights['venue'] +
            momentum_rating * weights['momentum'] +
            opposition_rating * weights['opposition']
        )
        
        return int(round(overall))
    
    def _calculate_position_rating(self) -> int:
        """Rating based on league position (0-100)"""
        position = self.team_info.get('position', 10)
        matches_played = self.team_info.get('matchesPlayed', 0)
        
        # Don't fully trust early season positions
        if matches_played < 5:
            confidence = 0.6
        elif matches_played < 10:
            confidence = 0.8
        else:
            confidence = 1.0
        
        # Simple inverse - 1st = 100, 20th = 0 (scaled)
        # Assuming 20 team league, adjust if needed
        max_position = 20
        base_rating = ((max_position - position + 1) / max_position) * 100
        
        return int(base_rating * confidence)
    
    def _calculate_form_rating(self, is_home: bool) -> int:
        """Rating based on recent form (0-100)"""
        # Get last 6 matches
        recent_fixtures = self._get_recent_fixtures(6, is_home)
        
        if not recent_fixtures:
            return 50
        
        wins = sum(1 for m in recent_fixtures if get_match_result(m, self.team_id) == 'W')
        draws = sum(1 for m in recent_fixtures if get_match_result(m, self.team_id) == 'D')
        
        # Points from last 6 (max 18)
        points = (wins * 3) + draws
        max_points = len(recent_fixtures) * 3
        
        rating = (points / max_points) * 100
        
        return int(rating)
    
    def _calculate_venue_rating(self, is_home: bool) -> int:
        """Rating based on home/away performance (0-100)"""
        venue_fixtures = [f for f in self.fixtures 
                         if is_home_team(f, self.team_id) == is_home]
        
        if not venue_fixtures:
            return 50
        
        wins = sum(1 for m in venue_fixtures if get_match_result(m, self.team_id) == 'W')
        draws = sum(1 for m in venue_fixtures if get_match_result(m, self.team_id) == 'D')
        
        points = (wins * 3) + draws
        max_points = len(venue_fixtures) * 3
        
        rating = (points / max_points) * 100
        
        return int(rating)
    
    def _calculate_momentum_rating(self) -> int:
        """
        Rating based on momentum/trend (0-100)
        Compares last 3 matches to previous 3 matches
        """
        if len(self.fixtures) < 6:
            return 50
        
        last_3 = self.fixtures[-3:]
        previous_3 = self.fixtures[-6:-3]
        
        def get_points(matches):
            wins = sum(1 for m in matches if get_match_result(m, self.team_id) == 'W')
            draws = sum(1 for m in matches if get_match_result(m, self.team_id) == 'D')
            return (wins * 3) + draws
        
        recent_points = get_points(last_3)
        previous_points = get_points(previous_3)
        
        # Compare momentum
        if recent_points > previous_points:
            # Improving
            rating = 60 + ((recent_points - previous_points) * 5)
        elif recent_points < previous_points:
            # Declining
            rating = 40 - ((previous_points - recent_points) * 5)
        else:
            # Stable
            rating = 50
        
        return max(0, min(100, int(rating)))
    
    def _calculate_opposition_quality_rating(self) -> int:
        """
        Rating based on quality of opposition faced (0-100)
        Higher rating if performed well against strong teams
        """
        recent_fixtures = self._get_recent_fixtures(6)
        
        if not recent_fixtures:
            return 50
        
        # For now, simplified version
        # TODO: Could be enhanced by looking at opponent league positions
        # and adjusting based on results vs strong/weak teams
        
        return 50  # Neutral for now
    
    def _get_recent_fixtures(self, count: int, venue_filter: Optional[bool] = None) -> list:
        """
        Get most recent fixtures
        
        Args:
            count: Number of fixtures to return
            venue_filter: True for home only, False for away only, None for all
        """
        fixtures = self.fixtures
        
        if venue_filter is not None:
            fixtures = [f for f in fixtures if is_home_team(f, self.team_id) == venue_filter]
        
        return fixtures[-count:] if len(fixtures) >= count else fixtures
    
    def get_form_string(self, count: int = 6) -> str:
        """Get form string (e.g., 'W-W-L-D-W-L')"""
        recent = self._get_recent_fixtures(count)
        results = [get_match_result(m, self.team_id) for m in recent]
        return "-".join(results) if results else "No data"
    
    def get_quality_breakdown(self, is_home: bool = True) -> dict:
        """Get breakdown of quality components"""
        return {
            'overall': self.calculate_quality_rating(is_home),
            'position': self._calculate_position_rating(),
            'form': self._calculate_form_rating(is_home),
            'venue': self._calculate_venue_rating(is_home),
            'momentum': self._calculate_momentum_rating(),
            'opposition': self._calculate_opposition_quality_rating()
        }