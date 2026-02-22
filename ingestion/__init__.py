"""
Football Stats Ingestion System

A modular system for ingesting football statistics from the Football Data API.
Handles rate limiting, state management, and data organization.
"""

from .api_client import APIClient
from .rate_limiter import RateLimiter
from .league_mapper import LeagueMapper
from .data_manager import DataManager, GlobalDataManager
from .state_manager import IngestionState, get_all_ingestion_states
from .team_aggregator import TeamAggregator, aggregate_teams

__version__ = '1.0.0'

__all__ = [
    'APIClient',
    'RateLimiter',
    'LeagueMapper',
    'DataManager',
    'GlobalDataManager',
    'IngestionState',
    'get_all_ingestion_states',
    'TeamAggregator',
    'aggregate_teams',
]