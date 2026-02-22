"""
Data collectors for different API endpoints
"""

from .league_collector import LeagueCollector
from .team_collector import TeamCollector
from .match_collector import MatchCollector
from .player_collector import PlayerCollector
from .referee_collector import RefereeCollector
from .stats_collector import StatsCollector
from .h2h_collector import H2HCollector
from .match_details_collector import MatchDetailsCollector

__all__ = [
    'LeagueCollector',
    'TeamCollector',
    'MatchCollector',
    'PlayerCollector',
    'RefereeCollector',
    'StatsCollector',
    'H2HCollector',
    'MatchDetailsCollector',
]