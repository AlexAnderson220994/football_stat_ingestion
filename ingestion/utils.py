"""
Utility functions for the ingestion system
"""

from typing import Dict, List, Optional
from datetime import datetime


def format_timestamp(timestamp: Optional[int]) -> str:
    """
    Format UNIX timestamp to readable string
    
    Args:
        timestamp: UNIX timestamp
        
    Returns:
        Formatted datetime string
    """
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Invalid timestamp"


def calculate_h2h_stats(matches: List[Dict], team_a_id: int, team_b_id: int) -> Dict:
    """
    Calculate head-to-head statistics from match data
    
    Args:
        matches: List of match dicts
        team_a_id: ID of first team
        team_b_id: ID of second team
        
    Returns:
        Dict with H2H statistics
    """
    if not matches:
        return {
            'total_matches': 0,
            'team_a_wins': 0,
            'team_b_wins': 0,
            'draws': 0,
            'team_a_goals': 0,
            'team_b_goals': 0,
            'btts_count': 0,
            'btts_percentage': 0,
            'over25_count': 0,
            'over25_percentage': 0,
            'over15_count': 0,
            'over15_percentage': 0,
            'over35_count': 0,
            'over35_percentage': 0,
        }
    
    total = len(matches)
    team_a_wins = 0
    team_b_wins = 0
    draws = 0
    team_a_goals = 0
    team_b_goals = 0
    btts = 0
    over15 = 0
    over25 = 0
    over35 = 0
    
    for match in matches:
        # Determine which team is home/away
        if match.get('homeID') == team_a_id:
            team_a_scored = match.get('homeGoalCount', 0)
            team_b_scored = match.get('awayGoalCount', 0)
        else:
            team_a_scored = match.get('awayGoalCount', 0)
            team_b_scored = match.get('homeGoalCount', 0)
        
        team_a_goals += team_a_scored
        team_b_goals += team_b_scored
        total_goals = team_a_scored + team_b_scored
        
        # Wins/draws
        if team_a_scored > team_b_scored:
            team_a_wins += 1
        elif team_b_scored > team_a_scored:
            team_b_wins += 1
        else:
            draws += 1
        
        # BTTS
        if team_a_scored > 0 and team_b_scored > 0:
            btts += 1
        
        # Over/Under
        if total_goals > 1.5:
            over15 += 1
        if total_goals > 2.5:
            over25 += 1
        if total_goals > 3.5:
            over35 += 1
    
    return {
        'total_matches': total,
        'team_a_wins': team_a_wins,
        'team_b_wins': team_b_wins,
        'draws': draws,
        'team_a_win_percentage': round((team_a_wins / total) * 100, 2) if total > 0 else 0,
        'team_b_win_percentage': round((team_b_wins / total) * 100, 2) if total > 0 else 0,
        'draw_percentage': round((draws / total) * 100, 2) if total > 0 else 0,
        'team_a_goals': team_a_goals,
        'team_b_goals': team_b_goals,
        'team_a_avg_goals': round(team_a_goals / total, 2) if total > 0 else 0,
        'team_b_avg_goals': round(team_b_goals / total, 2) if total > 0 else 0,
        'btts_count': btts,
        'btts_percentage': round((btts / total) * 100, 2) if total > 0 else 0,
        'over15_count': over15,
        'over15_percentage': round((over15 / total) * 100, 2) if total > 0 else 0,
        'over25_count': over25,
        'over25_percentage': round((over25 / total) * 100, 2) if total > 0 else 0,
        'over35_count': over35,
        'over35_percentage': round((over35 / total) * 100, 2) if total > 0 else 0,
    }


def get_team_name_from_data(team_data: Dict) -> str:
    """
    Extract team name from team data dict
    
    Args:
        team_data: Team data dict from API
        
    Returns:
        Team name string
    """
    # Try different possible name fields
    for field in ['name', 'cleanName', 'full_name', 'english_name']:
        if field in team_data and team_data[field]:
            return team_data[field]
    
    return f"Team_{team_data.get('id', 'Unknown')}"


def get_player_name_from_data(player_data: Dict) -> str:
    """
    Extract player name from player data dict
    
    Args:
        player_data: Player data dict from API
        
    Returns:
        Player name string
    """
    # Try different possible name fields
    for field in ['known_as', 'full_name', 'first_name']:
        if field in player_data and player_data[field]:
            return player_data[field]
    
    return f"Player_{player_data.get('id', 'Unknown')}"


def get_referee_name_from_data(referee_data: Dict) -> str:
    """
    Extract referee name from referee data dict
    
    Args:
        referee_data: Referee data dict from API
        
    Returns:
        Referee name string
    """
    # Try different possible name fields
    for field in ['known_as', 'full_name', 'first_name']:
        if field in referee_data and referee_data[field]:
            return referee_data[field]
    
    return f"Referee_{referee_data.get('id', 'Unknown')}"


def estimate_api_calls_for_league(season_id: int, existing_state: Optional[Dict] = None) -> Dict:
    """
    Estimate number of API calls needed for a league ingestion
    
    Args:
        season_id: Season ID
        existing_state: Existing ingestion state if resuming
        
    Returns:
        Dict with estimated call counts
    """
    # Default estimates for a full ingestion
    estimates = {
        'league_stats': 1,
        'league_table': 1,
        'league_teams': 1,  # Usually 20 teams fit in one call
        'league_matches': 2,  # Estimate 2 pages for ~380 matches at 500/page
        'league_players': 3,  # Estimate 3 pages at 200/page
        'league_referees': 1,
        'team_lastx': 20,  # One call per team
        'btts_stats': 1,
        'over25_stats': 1,
    }
    
    # Adjust based on existing state
    if existing_state:
        collections = existing_state.get('collections', {})
        
        # Subtract completed collections
        if collections.get('league_stats', {}).get('status') == 'complete':
            estimates['league_stats'] = 0
        
        if collections.get('league_table', {}).get('status') == 'complete':
            estimates['league_table'] = 0
        
        teams_status = collections.get('teams', {})
        if teams_status.get('status') == 'complete':
            estimates['league_teams'] = 0
            estimates['team_lastx'] = 0
        else:
            fetched = teams_status.get('fetched', 0)
            total = teams_status.get('total', 20)
            remaining_teams = max(0, total - fetched)
            estimates['team_lastx'] = remaining_teams
        
        matches_status = collections.get('matches', {})
        if matches_status.get('status') == 'complete':
            estimates['league_matches'] = 0
        else:
            fetched = matches_status.get('fetched', 0)
            # Rough estimate: 1 call per 500 matches
            estimates['league_matches'] = max(1, (matches_status.get('total', 380) - fetched) // 500 + 1)
        
        players_status = collections.get('players', {})
        if players_status.get('status') == 'complete':
            estimates['league_players'] = 0
        
        referees_status = collections.get('referees', {})
        if referees_status.get('status') == 'complete':
            estimates['league_referees'] = 0
    
    # Calculate total
    estimates['total'] = sum(estimates.values())
    
    return estimates


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2h 15m 30s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]