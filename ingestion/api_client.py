"""
API client with rate limiting and retry logic
"""

import requests
import time
from typing import Optional, Dict, Any
from .config import API_KEY, API_BASE_URL, ENDPOINTS
from .rate_limiter import RateLimiter


class APIClient:
    """
    Handles all API requests with rate limiting and error handling
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self.base_url = API_BASE_URL
        self.api_key = API_KEY
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = requests.Session()
        
        # Validate API key exists
        if not self.api_key:
            raise ValueError("API key not found. Please set FOOTYSTATS_API_KEY in .env file")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[Dict]:
        """
        Make a GET request to the API
        
        Args:
            endpoint: API endpoint (can be key from ENDPOINTS or full path)
            params: Additional query parameters
            max_retries: Number of retry attempts on failure
            
        Returns:
            JSON response as dict, or None on failure
        """
        # Get full endpoint path if key was provided
        if endpoint in ENDPOINTS:
            endpoint_path = ENDPOINTS[endpoint]
        else:
            endpoint_path = endpoint if endpoint.startswith('/') else f'/{endpoint}'
        
        # Build URL - ensure proper formatting
        base = self.base_url.rstrip('/')
        path = endpoint_path.lstrip('/')
        url = f"{base}/{path}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        # Wait if rate limit reached
        self.rate_limiter.wait_if_needed()
        
        # Make request with retries
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                # Record the request
                self.rate_limiter.record_request()
                
                # Check for successful response
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:
                    # Rate limit hit on server side
                    print(f"⚠ Server rate limit hit (429). Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                elif response.status_code == 403:
                    print(f"✗ API key invalid or expired (403)")
                    return None
                
                else:
                    print(f"⚠ Unexpected status code {response.status_code}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"  Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    return None
            
            except requests.exceptions.Timeout:
                print(f"⚠ Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            
            except requests.exceptions.RequestException as e:
                print(f"✗ Request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def get_league_list(self) -> Optional[Dict]:
        """Convenience method to get league list"""
        return self.get("league-list")
    
    def get_league_stats(self, season_id: int, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get league stats for a season"""
        params = {"season_id": season_id}
        if max_time:
            params["max_time"] = max_time
        return self.get("league_stats", params)
    
    def get_league_table(self, season_id: int, include_stats: bool = True, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get league table"""
        params = {"season_id": season_id}
        if include_stats:
            params["include"] = "stats"
        if max_time:
            params["max_time"] = max_time
        return self.get("league_table", params)
    
    def get_league_teams(self, season_id: int, include_stats: bool = True, page: int = 1, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get teams in a league"""
        params = {"season_id": season_id, "page": page}
        if include_stats:
            params["include"] = "stats"
        if max_time:
            params["max_time"] = max_time
        return self.get("league_teams", params)
    
    def get_league_matches(self, season_id: int, page: int = 1, max_per_page: int = 500, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get matches in a league"""
        params = {
            "season_id": season_id,
            "page": page,
            "max_per_page": max_per_page
        }
        if max_time:
            params["max_time"] = max_time
        return self.get("league_matches", params)
    
    def get_league_players(self, season_id: int, page: int = 1, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get players in a league"""
        params = {"season_id": season_id, "page": page}
        if max_time:
            params["max_time"] = max_time
        return self.get("league_players", params)
    
    def get_league_referees(self, season_id: int, max_time: Optional[int] = None) -> Optional[Dict]:
        """Get referees in a league"""
        params = {"season_id": season_id}
        if max_time:
            params["max_time"] = max_time
        return self.get("league_referees", params)
    
    def get_team(self, team_id: int, include_stats: bool = True) -> Optional[Dict]:
        """Get individual team data"""
        params = {"team_id": team_id}
        if include_stats:
            params["include"] = "stats"
        return self.get("team", params)
    
    def get_team_lastx(self, team_id: int) -> Optional[Dict]:
        """Get last 5/6/10 stats for a team"""
        params = {"team_id": team_id}
        return self.get("team_lastx", params)
    
    def get_match(self, match_id: int) -> Optional[Dict]:
        """Get individual match details"""
        params = {"match_id": match_id}
        return self.get("match", params)
    
    def get_player(self, player_id: int) -> Optional[Dict]:
        """Get individual player stats"""
        params = {"player_id": player_id}
        return self.get("player", params)
    
    def get_referee(self, referee_id: int) -> Optional[Dict]:
        """Get individual referee stats"""
        params = {"referee_id": referee_id}
        return self.get("referee", params)
    
    def get_btts_stats(self) -> Optional[Dict]:
        """Get BTTS statistics"""
        return self.get("btts_stats")
    
    def get_over25_stats(self) -> Optional[Dict]:
        """Get Over 2.5 statistics"""
        return self.get("over25_stats")
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status"""
        return self.rate_limiter.get_status()
    
    def print_rate_limit_status(self):
        """Print current rate limit status"""
        self.rate_limiter.print_status()