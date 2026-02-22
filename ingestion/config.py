"""
Configuration for the ingestion system
Includes league definitions and API settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("FOOTYSTATS_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.football-data-api.com")
REQUESTS_PER_HOUR = int(os.getenv("REQUESTS_PER_HOUR", 1800))

# Data directories
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RAW_DATA_DIR = DATA_DIR / "raw"
LEAGUES_DIR = DATA_DIR / "leagues"
STATS_DIR = DATA_DIR / "stats"
STATE_DIR = DATA_DIR / "ingestion_state"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, LEAGUES_DIR, STATS_DIR, STATE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Target leagues - hardcoded (what we want to track)
# The system will dynamically fetch season IDs from the API
TARGET_LEAGUES = {
    "england_premier_league": {
        "name": "England Premier League",
        "country": "England",
        "key": "england_premier_league"
    },
    "england_championship": {
        "name": "England Championship",
        "country": "England",
        "key": "england_championship"
    },
    # "england_fa_cup": {
    #     "name": "England FA Cup",
    #     "country": "England",
    #     "key": "england_fa_cup"
    # },
    # "england_league_cup": {
    #     "name": "England League Cup",
    #     "country": "England",
    #     "key": "england_league_cup"
    # },
    "spain_la_liga": {
        "name": "Spain La Liga",
        "country": "Spain",
        "key": "spain_la_liga"
    },
    # "spain_copa_del_rey": {
    #     "name": "Spain Copa del Rey",
    #     "country": "Spain",
    #     "key": "spain_copa_del_rey"
    # },
    "italy_serie_a": {
        "name": "Italy Serie A",
        "country": "Italy",
        "key": "italy_serie_a"
    },
    # "italy_coppa_italia": {
    #     "name": "Italy Coppa Italia",
    #     "country": "Italy",
    #     "key": "italy_coppa_italia"
    # },
    "germany_bundesliga": {
        "name": "Germany Bundesliga",
        "country": "Germany",
        "key": "germany_bundesliga"
    },
    # "germany_dfb_pokal": {
    #     "name": "Germany DFB Pokal",
    #     "country": "Germany",
    #     "key": "germany_dfb_pokal"
    # },
    "france_ligue_1": {
        "name": "France Ligue 1",
        "country": "France",
        "key": "france_ligue_1"
    },
    # "france_coupe_de_france": {
    #     "name": "France Coupe de France",
    #     "country": "France",
    #     "key": "france_coupe_de_france"
    # },
    "portugal_liga_nos": {
        "name": "Portugal Liga NOS",
        "country": "Portugal",
        "key": "portugal_liga_nos"
    },
    "netherlands_eredivisie": {
        "name": "Netherlands Eredivisie",
        "country": "Netherlands",
        "key": "netherlands_eredivisie"
    },
    "champions_league": {
        "name": "Europe UEFA Champions League",
        "country": "Europe",
        "key": "champions_league"
    },
    "europa_league": {
        "name": "Europe UEFA Europa League",
        "country": "Europe",
        "key": "europa_league"
    },
    "europa_conference_league": {
        "name": "Europe UEFA Europa Conference League",
        "country": "Europe",
        "key": "europa_conference_league"
    },
    "denmark_superliga": {
        "name": "Denmark Superliga",
        "country": "Denmark",
        "key": "denmark_superliga"
    },
    "norway_eliteserien": {
        "name": "Norway Eliteserien",
        "country": "Norway",
        "key": "norway_eliteserien"
    },
    "belgium_pro_league": {
        "name": "Belgium Pro League",
        "country": "Belgium",
        "key": "belgium_pro_league"
    },
}

# API Endpoints
ENDPOINTS = {
    "league_list": "/league-list",
    "league_stats": "/league-season",
    "league_table": "/league-tables",
    "league_teams": "/league-teams",
    "league_matches": "/league-matches",
    "league_players": "/league-players",
    "league_referees": "/league-referees",
    "team": "/team",
    "team_lastx": "/lastx",
    "match": "/match",
    "player": "/player-stats",
    "referee": "/referee",
    "btts_stats": "/stats-data-btts",
    "over25_stats": "/stats-data-over25",
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")