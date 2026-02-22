"""
Stat Calculator
Calculates team and player statistics with proper filtering for backtesting
"""

from typing import Dict, List, Optional, Tuple
from .utils import (
    get_team_stats, get_opponent_stats, is_home_team, 
    filter_matches_before_gameweek, is_completed_match,
    get_team_goals, safe_divide
)


class StatCalculator:
    """
    Calculates statistics from match data
    Handles backtesting by excluding future gameweeks
    """
    
    def __init__(self, max_gameweek: Optional[int] = None):
        """
        Args:
            max_gameweek: Maximum gameweek to include (for backtesting)
                         If None, includes all data (live mode)
        """
        self.max_gameweek = max_gameweek
    
    def filter_matches(self, matches: List[Dict]) -> List[Dict]:
        """Filter matches based on gameweek limit and completion status"""
        matches = [m for m in matches if is_completed_match(m)]
        
        if self.max_gameweek:
            matches = filter_matches_before_gameweek(matches, self.max_gameweek)
        
        return matches
    
    def calculate_team_averages(self, team_id: int, fixtures: List[Dict], 
                                is_home: Optional[bool] = None) -> Dict:
        """
        Calculate team averages for various stats
        
        Args:
            team_id: Team ID
            fixtures: List of team fixtures
            is_home: If True, only home matches. If False, only away. If None, all matches.
        
        Returns:
            Dict with averages for corners, shots, cards, goals, etc.
        """
        # Filter matches
        fixtures = self.filter_matches(fixtures)
        
        # Filter by venue if specified
        if is_home is not None:
            fixtures = [f for f in fixtures if is_home_team(f, team_id) == is_home]
        
        if not fixtures:
            return self._empty_averages()
        
        total_matches = len(fixtures)
        
        # Accumulate stats
        stats = {
            'corners': 0,
            'corners_1h': 0,
            'corners_2h': 0,
            'shots': 0,
            'shots_on_target': 0,
            'shots_off_target': 0,
            'cards': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'fouls': 0,
            'possession': 0,
            'goals_scored': 0,
            'goals_conceded': 0,
            'goals_1h_scored': 0,
            'goals_1h_conceded': 0,
            'xg': 0.0,
            'attacks': 0,
            'dangerous_attacks': 0,
            'offsides': 0,
        }
        
        # Count betting outcomes
        over_05 = 0
        over_15 = 0
        over_25 = 0
        btts = 0
        clean_sheets = 0
        failed_to_score = 0
        
        for match in fixtures:
            # Corners
            stats['corners'] += get_team_stats(match, team_id, 'corners')
            stats['corners_1h'] += get_team_stats(match, team_id, 'fh_corners')
            stats['corners_2h'] += get_team_stats(match, team_id, '2h_corners')
            
            # Shots
            stats['shots'] += get_team_stats(match, team_id, 'shots')
            stats['shots_on_target'] += get_team_stats(match, team_id, 'shotsOnTarget')
            stats['shots_off_target'] += get_team_stats(match, team_id, 'shotsOffTarget')
            
            # Cards
            stats['cards'] += get_team_stats(match, team_id, 'cards_num')
            stats['yellow_cards'] += get_team_stats(match, team_id, 'yellow_cards')
            stats['red_cards'] += get_team_stats(match, team_id, 'red_cards')
            
            # Other stats
            stats['fouls'] += get_team_stats(match, team_id, 'fouls')
            stats['possession'] += get_team_stats(match, team_id, 'possession')
            stats['offsides'] += get_team_stats(match, team_id, 'offsides')
            
            # xG (if available)
            xg = get_team_stats(match, team_id, 'xg')
            if xg and xg > 0:
                stats['xg'] += xg
            
            # Attacks (if available)
            attacks = get_team_stats(match, team_id, 'attacks')
            if attacks and attacks > 0:
                stats['attacks'] += attacks
            
            dangerous = get_team_stats(match, team_id, 'dangerous_attacks')
            if dangerous and dangerous > 0:
                stats['dangerous_attacks'] += dangerous
            
            # Goals
            goals_scored, goals_conceded = get_team_goals(match, team_id)
            stats['goals_scored'] += goals_scored
            stats['goals_conceded'] += goals_conceded
            
            # Half-time goals
            if is_home_team(match, team_id):
                stats['goals_1h_scored'] += match.get('ht_goals_team_a', 0)
                stats['goals_1h_conceded'] += match.get('ht_goals_team_b', 0)
            else:
                stats['goals_1h_scored'] += match.get('ht_goals_team_b', 0)
                stats['goals_1h_conceded'] += match.get('ht_goals_team_a', 0)
            
            # Betting outcomes
            total_goals = goals_scored + goals_conceded
            if total_goals > 0.5:
                over_05 += 1
            if total_goals > 1.5:
                over_15 += 1
            if total_goals > 2.5:
                over_25 += 1
            
            if goals_scored > 0 and goals_conceded > 0:
                btts += 1
            
            if goals_conceded == 0:
                clean_sheets += 1
            
            if goals_scored == 0:
                failed_to_score += 1
        
        # Calculate averages
        averages = {
            'matches': total_matches,
            'corners_avg': safe_divide(stats['corners'], total_matches),
            'corners_1h_avg': safe_divide(stats['corners_1h'], total_matches),
            'corners_2h_avg': safe_divide(stats['corners_2h'], total_matches),
            'shots_avg': safe_divide(stats['shots'], total_matches),
            'shots_on_target_avg': safe_divide(stats['shots_on_target'], total_matches),
            'shots_off_target_avg': safe_divide(stats['shots_off_target'], total_matches),
            'cards_avg': safe_divide(stats['cards'], total_matches),
            'yellow_cards_avg': safe_divide(stats['yellow_cards'], total_matches),
            'red_cards_avg': safe_divide(stats['red_cards'], total_matches),
            'fouls_avg': safe_divide(stats['fouls'], total_matches),
            'possession_avg': safe_divide(stats['possession'], total_matches),
            'goals_scored_avg': safe_divide(stats['goals_scored'], total_matches),
            'goals_conceded_avg': safe_divide(stats['goals_conceded'], total_matches),
            'goals_1h_scored_avg': safe_divide(stats['goals_1h_scored'], total_matches),
            'goals_1h_conceded_avg': safe_divide(stats['goals_1h_conceded'], total_matches),
            'xg_avg': safe_divide(stats['xg'], total_matches),
            'attacks_avg': safe_divide(stats['attacks'], total_matches),
            'dangerous_attacks_avg': safe_divide(stats['dangerous_attacks'], total_matches),
            'offsides_avg': safe_divide(stats['offsides'], total_matches),
            
            # Betting percentages
            'over_05_pct': safe_divide(over_05 * 100, total_matches),
            'over_15_pct': safe_divide(over_15 * 100, total_matches),
            'over_25_pct': safe_divide(over_25 * 100, total_matches),
            'btts_pct': safe_divide(btts * 100, total_matches),
            'clean_sheet_pct': safe_divide(clean_sheets * 100, total_matches),
            'failed_to_score_pct': safe_divide(failed_to_score * 100, total_matches),
        }
        
        return averages
    
    def _empty_averages(self) -> Dict:
        """Return empty averages dict"""
        return {
            'matches': 0,
            'corners_avg': 0.0,
            'corners_1h_avg': 0.0,
            'corners_2h_avg': 0.0,
            'shots_avg': 0.0,
            'shots_on_target_avg': 0.0,
            'shots_off_target_avg': 0.0,
            'cards_avg': 0.0,
            'yellow_cards_avg': 0.0,
            'red_cards_avg': 0.0,
            'fouls_avg': 0.0,
            'possession_avg': 0.0,
            'goals_scored_avg': 0.0,
            'goals_conceded_avg': 0.0,
            'goals_1h_scored_avg': 0.0,
            'goals_1h_conceded_avg': 0.0,
            'xg_avg': 0.0,
            'attacks_avg': 0.0,
            'dangerous_attacks_avg': 0.0,
            'offsides_avg': 0.0,
            'over_05_pct': 0.0,
            'over_15_pct': 0.0,
            'over_25_pct': 0.0,
            'btts_pct': 0.0,
            'clean_sheet_pct': 0.0,
            'failed_to_score_pct': 0.0,
        }
    
    def calculate_player_stats(self, player: Dict, min_minutes: int = 450) -> Optional[Dict]:
        """
        Calculate player betting-relevant stats
        
        Args:
            player: Player data from API
            min_minutes: Minimum minutes threshold (default 450 = ~5 full games)
        
        Returns:
            Player stats dict or None if below threshold
        """
        minutes_played = player.get('minutes_played_overall', 0)
        
        # Filter by minimum minutes
        if minutes_played < min_minutes:
            return None
        
        # Convert to per-90 stats
        mins_per_90 = minutes_played / 90.0
        
        goals = player.get('goals_overall', 0)
        assists = player.get('assists_overall', 0)
        cards = player.get('cards_overall', 0)
        yellow_cards = player.get('yellow_cards_overall', 0)
        red_cards = player.get('red_cards_overall', 0)
        
        return {
            'player_id': player.get('id'),
            'name': player.get('known_as', player.get('full_name', 'Unknown')),
            'position': player.get('position', 'Unknown'),
            'minutes_played': minutes_played,
            'appearances': player.get('appearances_overall', 0),
            'goals': goals,
            'assists': assists,
            'cards': cards,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'goals_per_90': safe_divide(goals * 90, minutes_played),
            'assists_per_90': safe_divide(assists * 90, minutes_played),
            'cards_per_90': safe_divide(cards * 90, minutes_played),
            'min_per_goal': safe_divide(minutes_played, goals) if goals > 0 else 0,
            'min_per_card': safe_divide(minutes_played, cards) if cards > 0 else 0,
        }
    
    def get_h2h_stats(self, team_a_id: int, team_b_id: int, all_matches: List[Dict]) -> Optional[Dict]:
        """
        Get head-to-head stats between two teams (this season only - reverse fixture)
        
        Returns:
            H2H stats dict or None if no previous meeting
        """
        # Filter matches
        matches = self.filter_matches(all_matches)
        
        # Find reverse fixture (both teams involved)
        h2h_matches = []
        for match in matches:
            home_id = match.get('homeID')
            away_id = match.get('awayID')
            
            if (home_id == team_a_id and away_id == team_b_id) or \
               (home_id == team_b_id and away_id == team_a_id):
                h2h_matches.append(match)
        
        if not h2h_matches:
            return None
        
        # Use most recent match only (this season's reverse fixture)
        recent_match = h2h_matches[-1]
        
        # Determine which team was home in that match
        team_a_was_home = recent_match.get('homeID') == team_a_id
        
        if team_a_was_home:
            team_a_corners = recent_match.get('team_a_corners', 0)
            team_b_corners = recent_match.get('team_b_corners', 0)
            team_a_shots = recent_match.get('team_a_shots', 0)
            team_b_shots = recent_match.get('team_b_shots', 0)
            team_a_goals, team_b_goals = get_team_goals(recent_match, team_a_id)
        else:
            team_a_corners = recent_match.get('team_b_corners', 0)
            team_b_corners = recent_match.get('team_a_corners', 0)
            team_a_shots = recent_match.get('team_b_shots', 0)
            team_b_shots = recent_match.get('team_a_shots', 0)
            team_b_goals, team_a_goals = get_team_goals(recent_match, team_b_id)
        
        return {
            'date': recent_match.get('date_unix'),
            'gameweek': recent_match.get('game_week'),
            'venue': 'team_a_home' if team_a_was_home else 'team_b_home',
            'team_a_corners': team_a_corners,
            'team_b_corners': team_b_corners,
            'total_corners': team_a_corners + team_b_corners,
            'team_a_shots': team_a_shots,
            'team_b_shots': team_b_shots,
            'total_shots': team_a_shots + team_b_shots,
            'team_a_goals': team_a_goals,
            'team_b_goals': team_b_goals,
            'total_goals': team_a_goals + team_b_goals,
        }
    
    def get_player_name_from_id(self, player_id: int, all_players: List[Dict]) -> Optional[str]:
        """
        Get player name from player ID
        
        Args:
            player_id: Player ID to lookup
            all_players: List of all player dictionaries
        
        Returns:
            Player name or None if not found
        """
        for player in all_players:
            if player.get('id') == player_id:
                return player.get('known_as') or player.get('full_name') or 'Unknown'
        
        return None