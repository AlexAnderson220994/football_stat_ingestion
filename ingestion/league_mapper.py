"""
Dynamic league mapping - fetches league IDs from API and matches to our target leagues
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from .config import TARGET_LEAGUES, DATA_DIR
from .api_client import APIClient


class LeagueMapper:
    """
    Fetches league list from API and maps to our target leagues
    Caches results to avoid unnecessary API calls
    """
    
    CACHE_FILE = DATA_DIR / "league_cache.json"
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.leagues_data = None
    
    def fetch_and_map_leagues(self, force_refresh: bool = False) -> Dict:
        """
        Fetch league list from API and map to target leagues
        
        Args:
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            Dict mapping league keys to their full data including seasons
        """
        # Try to load from cache first
        if not force_refresh and self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    cached_data = json.load(f)
                    # Check if cache is recent (less than 24 hours old)
                    cache_age = time.time() - cached_data.get('timestamp', 0)
                    if cache_age < 86400:  # 24 hours
                        print("✓ Using cached league data")
                        return cached_data['leagues']
            except Exception as e:
                print(f"⚠ Could not load cache: {e}")
        
        print("Fetching league list from API...")
        response = self.api_client.get("league-list")
        
        if not response or not response.get('success'):
            raise Exception("Failed to fetch league list from API")
        
        api_leagues = response.get('data', [])
        mapped_leagues = {}
        
        # Map each target league to its API data using exact name match
        for key, target in TARGET_LEAGUES.items():
            matched = self._find_league_by_name(target['name'], api_leagues)
            if matched:
                # Format seasons with proper year display
                formatted_seasons = []
                for season in matched['season']:
                    formatted_seasons.append({
                        'id': season['id'],
                        'year': self._format_year(season['year'])
                    })
                
                mapped_leagues[key] = {
                    **target,
                    'seasons': formatted_seasons,
                    'api_name': matched['name']
                }
                print(f"✓ Mapped {target['name']}: {len(formatted_seasons)} seasons found")
            else:
                print(f"✗ WARNING: Could not find '{target['name']}' in API data")
                mapped_leagues[key] = {
                    **target,
                    'seasons': [],
                    'api_name': None
                }
        
        # Cache the results
        cache_data = {
            'timestamp': time.time(),
            'leagues': mapped_leagues
        }
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"\n✓ Cached league data to {self.CACHE_FILE}")
        return mapped_leagues
    
    def _find_league_by_name(self, target_name: str, api_leagues: List[Dict]) -> Optional[Dict]:
        """
        Find league in API data by exact name match
        
        Args:
            target_name: The exact league name we're looking for
            api_leagues: List of leagues from API
            
        Returns:
            The matching league dict with 'name' and 'season' keys, or None
        """
        for league in api_leagues:
            if league.get('name') == target_name:
                return league
        return None
    
    def _format_year(self, year: int) -> str:
        """
        Format year integer to readable string
        
        Args:
            year: Year as integer (e.g., 20162017 or 2016)
            
        Returns:
            Formatted year string (e.g., "2016/2017" or "2016")
        """
        year_str = str(year)
        
        # If year is 8 digits, it's a season range (e.g., 20162017)
        if len(year_str) == 8:
            return f"{year_str[:4]}/{year_str[4:]}"
        
        # Otherwise it's a single year
        return year_str
    
    def get_league_seasons(self, league_key: str) -> List[Dict]:
        """
        Get all available seasons for a specific league
        
        Returns:
            List of dicts with 'id' and 'year' keys, sorted newest first
        """
        if not self.leagues_data:
            self.leagues_data = self.fetch_and_map_leagues()
        
        league = self.leagues_data.get(league_key)
        if not league:
            return []
        
        seasons = league.get('seasons', [])
        # Sort by ID descending (newest first)
        return sorted(seasons, key=lambda x: x['id'], reverse=True)
    
    def get_latest_season(self, league_key: str) -> Optional[Dict]:
        """
        Get the most recent season for a league
        
        Returns:
            Dict with 'id' and 'year' keys, or None if not found
        """
        seasons = self.get_league_seasons(league_key)
        if not seasons:
            return None
        
        # Already sorted newest first
        return seasons[0]
    
    def get_second_latest_season(self, league_key: str) -> Optional[Dict]:
        """
        Get the second most recent season for a league (for status display)
        
        Returns:
            Dict with 'id' and 'year' keys, or None if not found
        """
        seasons = self.get_league_seasons(league_key)
        if len(seasons) < 2:
            return None
        
        return seasons[1]
    
    def refresh_cache(self):
        """Force refresh the league cache"""
        print("Forcing cache refresh...")
        return self.fetch_and_map_leagues(force_refresh=True)


# Convenience function
def get_league_mapper(api_client: APIClient) -> LeagueMapper:
    """Get or create a LeagueMapper instance"""
    return LeagueMapper(api_client)