"""
Data Loader
Loads match details, league tables, team fixtures, and player data
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class DataLoader:
    """Loads football data from ingested files"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.leagues_dir = self.data_dir / "leagues"
        self.teams_dir = self.data_dir / "teams"
    
    def get_available_leagues(self) -> List[Dict]:
        """
        Get list of available leagues with their data
        
        Returns:
            List of dicts with league info: {name, key, season_id, path, gameweeks}
        """
        leagues = []
        
        for league_dir in self.leagues_dir.iterdir():
            if not league_dir.is_dir():
                continue
            
            dir_name = league_dir.name
            parts = dir_name.rsplit('_', 1)
            
            if len(parts) != 2:
                continue
            
            league_key = parts[0]
            try:
                season_id = int(parts[1])
            except ValueError:
                continue
            
            metadata_file = league_dir / "metadata.json"
            league_name = league_key.replace('_', ' ').title()
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        league_name = metadata.get('league_name', league_name)
                except:
                    pass
            
            matches_dir = league_dir / "matches"
            max_gameweek = 0
            completed_gameweeks = 0
            next_gameweek = None
            
            if matches_dir.exists():
                gameweeks_with_incomplete = set()
                
                for match_file in matches_dir.glob("*.json"):
                    try:
                        with open(match_file, 'r') as f:
                            match = json.load(f)
                            gw = match.get('game_week', 0)
                            status = match.get('status', '')
                            
                            if gw > max_gameweek:
                                max_gameweek = gw
                            
                            if status == 'complete':
                                completed_gameweeks = max(completed_gameweeks, gw)
                            
                            if status in ['incomplete', 'fixture']:
                                gameweeks_with_incomplete.add(gw)
                    except:
                        continue
                
                if gameweeks_with_incomplete:
                    next_gameweek = min(gameweeks_with_incomplete)
                else:
                    next_gameweek = completed_gameweeks + 1
            
            leagues.append({
                'name': league_name,
                'key': league_key,
                'season_id': season_id,
                'path': str(league_dir),
                'max_gameweek': max_gameweek,
                'completed_gameweeks': completed_gameweeks,
                'next_gameweek': next_gameweek if next_gameweek else max_gameweek
            })
        
        return sorted(leagues, key=lambda x: x['name'])
    
    def get_next_gameweek(self, league_key: str, season_id: int) -> int:
        """
        Get the next upcoming gameweek (first gameweek with incomplete matches)
        
        Returns:
            Next gameweek number
        """
        all_matches = self.load_all_matches(league_key, season_id)
        
        if not all_matches:
            return 1
        
        incomplete_gameweeks = set()
        completed_gameweeks = set()
        
        for match in all_matches:
            gw = match.get('game_week', 0)
            status = match.get('status', '')
            
            if status == 'complete':
                completed_gameweeks.add(gw)
            elif status in ['incomplete', 'fixture']:
                incomplete_gameweeks.add(gw)
        
        if incomplete_gameweeks:
            return min(incomplete_gameweeks)
        
        if completed_gameweeks:
            return max(completed_gameweeks) + 1
        
        return 1
    
    def load_league_table(self, league_key: str, season_id: int) -> Optional[Dict]:
        """Load league table"""
        league_dir = self.leagues_dir / f"{league_key}_{season_id}"
        table_file = league_dir / "league_table.json"
        
        if not table_file.exists():
            return None
        
        try:
            with open(table_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading league table: {e}")
            return None
    
    def load_all_matches(self, league_key: str, season_id: int) -> List[Dict]:
        """Load all matches for a league/season"""
        league_dir = self.leagues_dir / f"{league_key}_{season_id}"
        matches_dir = league_dir / "matches"
        
        if not matches_dir.exists():
            return []
        
        matches = []
        for match_file in matches_dir.glob("*.json"):
            try:
                with open(match_file, 'r') as f:
                    match = json.load(f)
                    matches.append(match)
            except Exception as e:
                print(f"Error loading match {match_file}: {e}")
                continue
        
        matches.sort(key=lambda x: x.get('date_unix', 0))
        
        return matches
    
    def load_match_details(self, league_key: str, season_id: int, match_id: int) -> Optional[Dict]:
        """Load detailed match data"""
        league_dir = self.leagues_dir / f"{league_key}_{season_id}"
        details_file = league_dir / "match_details" / f"{match_id}.json"
        
        if not details_file.exists():
            return None
        
        try:
            with open(details_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading match details: {e}")
            return None
    
    def load_all_match_details(self, league_key: str, season_id: int) -> Dict[int, Dict]:
        """
        Load all match details for a league/season
        
        Returns:
            Dict mapping match_id to match details
        """
        league_dir = self.leagues_dir / f"{league_key}_{season_id}"
        details_dir = league_dir / "match_details"
        
        if not details_dir.exists():
            return {}
        
        match_details = {}
        for details_file in details_dir.glob("*.json"):
            try:
                match_id = int(details_file.stem)
                with open(details_file, 'r') as f:
                    match_details[match_id] = json.load(f)
            except Exception as e:
                print(f"Error loading match details {details_file}: {e}")
                continue
        
        return match_details
    
    def load_team_fixtures(self, team_id: int) -> Optional[Dict]:
        """
        Load aggregated team fixtures from data/teams/
        
        Returns:
            Dict with all_fixtures data or None if not found
        """
        if not self.teams_dir.exists():
            return None
        
        for team_dir in self.teams_dir.iterdir():
            if not team_dir.is_dir():
                continue
            
            team_info_file = team_dir / "team_info.json"
            if team_info_file.exists():
                try:
                    with open(team_info_file, 'r') as f:
                        info = json.load(f)
                        if info.get('team_id') == team_id:
                            fixtures_file = team_dir / "all_fixtures.json"
                            if fixtures_file.exists():
                                with open(fixtures_file, 'r') as f:
                                    return json.load(f)
                except:
                    continue
        
        return None
    
    def load_team_players(self, league_key: str, season_id: int, team_id: int) -> List[Dict]:
        """
        Load all players for a specific team.
        Tries players_detailed first, falls back to players if not found.
        """
        league_dir = self.leagues_dir / f"{league_key}_{season_id}"
        
        for folder in ['players_detailed', 'players']:
            players_dir = league_dir / folder
            if not players_dir.exists():
                continue
            
            players = []
            for player_file in players_dir.glob("*.json"):
                try:
                    with open(player_file, 'r') as f:
                        player = json.load(f)
                        if player.get('club_team_id') == team_id:
                            players.append(player)
                except Exception as e:
                    print(f"Error loading player {player_file}: {e}")
                    continue
            
            if players:
                return players
        
        return []
    
    def get_matches_for_gameweek(self, league_key: str, season_id: int, gameweek: int) -> List[Dict]:
        """Get all matches for a specific gameweek"""
        all_matches = self.load_all_matches(league_key, season_id)
        return [m for m in all_matches if m.get('game_week') == gameweek]