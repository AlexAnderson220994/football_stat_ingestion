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
    # England
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
    "england_league_one": {
        "name": "England EFL League One",
        "country": "England",
        "key": "england_league_one"
    },
    "england_league_two": {
        "name": "England EFL League Two",
        "country": "England",
        "key": "england_league_two"
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

    # Spain
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

    # Italy
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

    # Germany
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

    # France
    "france_ligue_1": {
        "name": "France Ligue 1",
        "country": "France",
        "key": "france_ligue_1"
    },

    # Other
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
    "scotland_premiership": {
        "name": "Scotland Premiership",
        "country": "Scotland",
        "key": "scotland_premiership"
    },
    "belgium_pro_league": {
        "name": "Belgium Pro League",
        "country": "Belgium",
        "key": "belgium_pro_league"
    },
    "turkey_süper_lig": {
        "name": "Turkey Süper Lig",
        "country": "Turkey",
        "key": "turkey_süper_lig"
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
    "brazil_serie_a": {
        "name": "Brazil Serie A",
        "country": "Brazil",
        "key": "brazil_serie_a"
    },
    "argentina_primera_division": {
        "name": "Argentina Primera División",
        "country": "Argentina",
        "key": "argentina_primera_division"
    },

    # Rest of World
    "australia_a_league": {
        "name": "Australia A-League",
        "country": "Australia",
        "key": "australia_a_league"
    },
    "austria_bundesliga": {
        "name": "Austria Bundesliga",
        "country": "Austria",
        "key": "austria_bundesliga"
    },
    "azerbaijan_premyer_liqasi": {
        "name": "Azerbaijan Premyer Liqası",
        "country": "Azerbaijan",
        "key": "azerbaijan_premyer_liqasi"
    },
    "bulgaria_first_league": {
        "name": "Bulgaria First League",
        "country": "Bulgaria",
        "key": "bulgaria_first_league"
    },
    "china_chinese_super_league": {
        "name": "China Chinese Super League",
        "country": "China",
        "key": "china_chinese_super_league"
    },
    "croatia_prva_hnl": {
        "name": "Croatia Prva HNL",
        "country": "Croatia",
        "key": "croatia_prva_hnl"
    },
    "cyprus_first_division": {
        "name": "Cyprus First Division",
        "country": "Cyprus",
        "key": "cyprus_first_division"
    },
    "czech_republic_first_league": {
        "name": "Czech Republic First League",
        "country": "Czech Republic",
        "key": "czech_republic_first_league"
    },
    "greece_super_league": {
        "name": "Greece Super League",
        "country": "Greece",
        "key": "greece_super_league"
    },
    "hungary_nb_i": {
        "name": "Hungary NB I",
        "country": "Hungary",
        "key": "hungary_nb_i"
    },
    "israel_israeli_premier_league": {
        "name": "Israel Israeli Premier League",
        "country": "Israel",
        "key": "israel_israeli_premier_league"
    },
    "japan_j1_league": {
        "name": "Japan J1 League",
        "country": "Japan",
        "key": "japan_j1_league"
    },
    "kazakhstan_premier_league": {
        "name": "Kazakhstan Kazakhstan Premier League",
        "country": "Kazakhstan",
        "key": "kazakhstan_premier_league"
    },
    "latvia_virsliga": {
        "name": "Latvia Virsliga",
        "country": "Latvia",
        "key": "latvia_virsliga"
    },
    "poland_ekstraklasa": {
        "name": "Poland Ekstraklasa",
        "country": "Poland",
        "key": "poland_ekstraklasa"
    },
    "romania_liga_i": {
        "name": "Romania Liga I",
        "country": "Romania",
        "key": "romania_liga_i"
    },
    "saudi_arabia_professional_league": {
        "name": "Saudi Arabia Professional League",
        "country": "Saudi Arabia",
        "key": "saudi_arabia_professional_league"
    },
    "serbia_superliga": {
        "name": "Serbia SuperLiga",
        "country": "Serbia",
        "key": "serbia_superliga"
    },
    "slovakia_super_liga": {
        "name": "Slovakia Super Liga",
        "country": "Slovakia",
        "key": "slovakia_super_liga"
    },
    "sweden_allsvenskan": {
        "name": "Sweden Allsvenskan",
        "country": "Sweden",
        "key": "sweden_allsvenskan"
    },
    "switzerland_super_league": {
        "name": "Switzerland Super League",
        "country": "Switzerland",
        "key": "switzerland_super_league"
    },
    "ukraine_ukrainian_premier_league": {
        "name": "Ukraine Ukrainian Premier League",
        "country": "Ukraine",
        "key": "ukraine_ukrainian_premier_league"
    },
    "usa_mls": {
        "name": "USA MLS",
        "country": "USA",
        "key": "usa_mls"
    },

    # Europe
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

    # Esports
    # "esports_esoccer_liga_pro": {
    #     "name": "Esports Esoccer Liga Pro",
    #     "country": "Esports",
    #     "key": "esports_esoccer_liga_pro"
    # },
    # "esports_esoccer_battle": {
    #     "name": "Esports Esoccer Battle",
    #     "country": "Esports",
    #     "key": "esports_esoccer_battle"
    # },
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