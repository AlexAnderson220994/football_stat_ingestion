"""
Utility functions for the betting analysis system
"""

from datetime import datetime
from typing import Optional


def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage, handling division by zero"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return round(numerator / denominator, 2)


def get_quality_tier_emoji(rating: int) -> str:
    """Get emoji representation for quality tier"""
    if rating >= 85:
        return "⭐⭐⭐⭐⭐ Elite"
    elif rating >= 70:
        return "⭐⭐⭐⭐ Strong"
    elif rating >= 55:
        return "⭐⭐⭐ Mid-Table"
    elif rating >= 40:
        return "⭐⭐ Lower-Mid"
    else:
        return "⭐ Relegation"


def format_form_string(results: list) -> str:
    """
    Format match results into W-W-L-D format
    
    Args:
        results: List of match results (e.g., ['W', 'W', 'L', 'D', 'W', 'L'])
    
    Returns:
        Formatted string (e.g., "W-W-L-D-W-L")
    """
    return "-".join(results)


def calculate_win_rate(wins: int, total_matches: int) -> int:
    """Calculate win rate as percentage"""
    return int(calculate_percentage(wins, total_matches))


def is_home_team(match: dict, team_id: int) -> bool:
    """Check if team is home team in match"""
    return match.get('homeID') == team_id


def get_team_goals(match: dict, team_id: int) -> tuple[int, int]:
    """
    Get goals scored and conceded for a team in a match
    
    Returns:
        (goals_scored, goals_conceded)
    """
    if is_home_team(match, team_id):
        return match.get('homeGoalCount', 0), match.get('awayGoalCount', 0)
    else:
        return match.get('awayGoalCount', 0), match.get('homeGoalCount', 0)


def get_team_stats(match: dict, team_id: int, stat_prefix: str) -> int:
    """
    Get team-specific stat from match
    
    Args:
        match: Match dictionary
        team_id: Team ID
        stat_prefix: Stat name without team prefix (e.g., 'corners', 'shots')
    
    Returns:
        Stat value for the team
    """
    if is_home_team(match, team_id):
        return match.get(f'team_a_{stat_prefix}', 0)
    else:
        return match.get(f'team_b_{stat_prefix}', 0)


def get_opponent_stats(match: dict, team_id: int, stat_prefix: str) -> int:
    """Get opponent's stat from match"""
    if is_home_team(match, team_id):
        return match.get(f'team_b_{stat_prefix}', 0)
    else:
        return match.get(f'team_a_{stat_prefix}', 0)


def get_match_result(match: dict, team_id: int) -> str:
    """
    Get match result from team's perspective
    
    Returns:
        'W', 'D', or 'L'
    """
    goals_for, goals_against = get_team_goals(match, team_id)
    
    if goals_for > goals_against:
        return 'W'
    elif goals_for == goals_against:
        return 'D'
    else:
        return 'L'


def is_completed_match(match: dict) -> bool:
    """Check if match is completed"""
    return match.get('status') == 'complete'


def filter_completed_matches(matches: list) -> list:
    """Filter list to only completed matches"""
    return [m for m in matches if is_completed_match(m)]


def get_gameweek(match: dict) -> int:
    """Get gameweek number from match"""
    return match.get('game_week', 0)


def filter_matches_before_gameweek(matches: list, max_gameweek: int) -> list:
    """
    Filter matches to only those before a specific gameweek
    Used for backtesting - exclude data from target GW onwards
    """
    return [m for m in matches if get_gameweek(m) < max_gameweek]


def get_competition_from_match(match: dict) -> str:
    """Extract competition key from match data"""
    return match.get('_league_key', 'unknown')


def format_odds(odds: float) -> str:
    """Format odds for display"""
    return f"@{odds:.2f}"


def seconds_to_minutes(seconds: int) -> int:
    """Convert seconds to minutes"""
    return seconds // 60


def unix_to_datetime(unix_timestamp: int) -> datetime:
    """Convert unix timestamp to datetime"""
    return datetime.fromtimestamp(unix_timestamp)


def format_date(unix_timestamp: int, format_str: str = "%d/%m/%Y") -> str:
    """Format unix timestamp as date string"""
    return unix_to_datetime(unix_timestamp).strftime(format_str)


def get_home_away_label(is_home: bool) -> str:
    """Get (H) or (A) label"""
    return "(H)" if is_home else "(A)"