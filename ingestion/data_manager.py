"""
Data manager for storing and retrieving ingested data
Handles JSON file I/O, deduplication, and data organization
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from .config import LEAGUES_DIR, STATS_DIR, STATE_DIR


class DataManager:
    """
    Manages data storage and retrieval
    """
    
    def __init__(self, league_key: str, season_id: int, season_year: str):
        self.league_key = league_key
        self.season_id = season_id
        self.season_year = season_year
        
        # Create league-specific directory
        self.league_dir = LEAGUES_DIR / f"{league_key}_{season_id}"
        self.league_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.teams_dir = self.league_dir / "teams"
        self.matches_dir = self.league_dir / "matches"
        self.match_details_dir = self.league_dir / "match_details"
        self.players_dir = self.league_dir / "players"
        self.referees_dir = self.league_dir / "referees"
        self.h2h_dir = self.league_dir / "h2h"
        
        for directory in [self.teams_dir, self.matches_dir, self.match_details_dir,
                         self.players_dir, self.referees_dir, self.h2h_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_metadata(self, metadata: Dict):
        """Save league metadata"""
        metadata_file = self.league_dir / "metadata.json"
        metadata['_saved_at'] = datetime.now().isoformat()
        self._save_json(metadata_file, metadata)
    
    def load_metadata(self) -> Optional[Dict]:
        """Load league metadata"""
        metadata_file = self.league_dir / "metadata.json"
        return self._load_json(metadata_file)
    
    def save_league_stats(self, data: Dict):
        """Save league season stats"""
        stats_file = self.league_dir / "league_stats.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(stats_file, data)
    
    def load_league_stats(self) -> Optional[Dict]:
        """Load league season stats"""
        stats_file = self.league_dir / "league_stats.json"
        return self._load_json(stats_file)
    
    def save_league_table(self, data: Dict):
        """Save league table"""
        table_file = self.league_dir / "league_table.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(table_file, data)
    
    def load_league_table(self) -> Optional[Dict]:
        """Load league table"""
        table_file = self.league_dir / "league_table.json"
        return self._load_json(table_file)
    
    def save_team(self, team_id: int, team_name: str, data: Dict):
        """Save team data"""
        # Sanitize team name for filename
        safe_name = self._sanitize_filename(team_name)
        team_file = self.teams_dir / f"{team_id}_{safe_name}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(team_file, data)
    
    def load_team(self, team_id: int) -> Optional[Dict]:
        """Load team data by ID"""
        # Find file that starts with team_id
        for file in self.teams_dir.glob(f"{team_id}_*.json"):
            if not file.name.endswith("_lastx.json"):
                return self._load_json(file)
        return None
    
    def get_all_team_ids(self) -> List[int]:
        """Get list of all saved team IDs"""
        team_ids = []
        for file in self.teams_dir.glob("*_*.json"):
            if not file.name.endswith("_lastx.json"):
                try:
                    team_id = int(file.stem.split('_')[0])
                    team_ids.append(team_id)
                except ValueError:
                    continue
        return sorted(team_ids)
    
    def save_team_lastx(self, team_id: int, team_name: str, data: Any):
        """Save team last X stats"""
        safe_name = self._sanitize_filename(team_name)
        lastx_file = self.teams_dir / f"{team_id}_{safe_name}_lastx.json"
        
        # Wrap data in an object with metadata
        # data is typically a list from the API
        wrapped_data = {
            'team_id': team_id,
            'team_name': team_name,
            'data': data,  # This could be a list or dict from API
            '_saved_at': datetime.now().isoformat()
        }
        self._save_json(lastx_file, wrapped_data)
    
    def load_team_lastx(self, team_id: int) -> Optional[Dict]:
        """Load team last X stats"""
        for file in self.teams_dir.glob(f"{team_id}_*_lastx.json"):
            return self._load_json(file)
        return None
    
    def save_match(self, match_id: int, data: Dict):
        """Save match data"""
        match_file = self.matches_dir / f"{match_id}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(match_file, data)
    
    def load_match(self, match_id: int) -> Optional[Dict]:
        """Load match data"""
        match_file = self.matches_dir / f"{match_id}.json"
        return self._load_json(match_file)
    
    def get_all_match_ids(self) -> List[int]:
        """Get list of all saved match IDs"""
        match_ids = []
        for file in self.matches_dir.glob("*.json"):
            try:
                match_id = int(file.stem)
                match_ids.append(match_id)
            except ValueError:
                continue
        return sorted(match_ids)
    
    def save_match_details(self, match_id: int, data: Dict):
        """Save detailed match data"""
        match_file = self.match_details_dir / f"{match_id}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(match_file, data)
    
    def load_match_details(self, match_id: int) -> Optional[Dict]:
        """Load detailed match data"""
        match_file = self.match_details_dir / f"{match_id}.json"
        return self._load_json(match_file)
    
    def get_all_match_detail_ids(self) -> List[int]:
        """Get list of all saved match detail IDs"""
        if not self.match_details_dir.exists():
            return []
        
        match_ids = []
        for file in self.match_details_dir.glob("*.json"):
            try:
                match_id = int(file.stem)
                match_ids.append(match_id)
            except ValueError:
                continue
        return sorted(match_ids)
    
    def save_player(self, player_id: int, player_name: str, data: Dict):
        """Save player data"""
        safe_name = self._sanitize_filename(player_name)
        player_file = self.players_dir / f"{player_id}_{safe_name}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(player_file, data)
    
    def load_player(self, player_id: int) -> Optional[Dict]:
        """Load player data"""
        for file in self.players_dir.glob(f"{player_id}_*.json"):
            return self._load_json(file)
        return None
    
    def get_all_player_ids(self) -> List[int]:
        """Get list of all saved player IDs"""
        player_ids = []
        for file in self.players_dir.glob("*.json"):
            try:
                player_id = int(file.stem.split('_')[0])
                player_ids.append(player_id)
            except ValueError:
                continue
        return sorted(player_ids)
    
    def save_referee(self, referee_id: int, referee_name: str, data: Dict):
        """Save referee data"""
        safe_name = self._sanitize_filename(referee_name)
        referee_file = self.referees_dir / f"{referee_id}_{safe_name}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(referee_file, data)
    
    def load_referee(self, referee_id: int) -> Optional[Dict]:
        """Load referee data"""
        for file in self.referees_dir.glob(f"{referee_id}_*.json"):
            return self._load_json(file)
        return None
    
    def get_all_referee_ids(self) -> List[int]:
        """Get list of all saved referee IDs"""
        referee_ids = []
        for file in self.referees_dir.glob("*.json"):
            try:
                referee_id = int(file.stem.split('_')[0])
                referee_ids.append(referee_id)
            except ValueError:
                continue
        return sorted(referee_ids)
    
    def save_h2h(self, team_a_id: int, team_b_id: int, data: Dict):
        """Save head-to-head data"""
        # Always use lower ID first for consistency
        if team_a_id > team_b_id:
            team_a_id, team_b_id = team_b_id, team_a_id
        
        h2h_file = self.h2h_dir / f"{team_a_id}_vs_{team_b_id}.json"
        data['_saved_at'] = datetime.now().isoformat()
        self._save_json(h2h_file, data)
    
    def load_h2h(self, team_a_id: int, team_b_id: int) -> Optional[Dict]:
        """Load head-to-head data"""
        # Always use lower ID first for consistency
        if team_a_id > team_b_id:
            team_a_id, team_b_id = team_b_id, team_a_id
        
        h2h_file = self.h2h_dir / f"{team_a_id}_vs_{team_b_id}.json"
        return self._load_json(h2h_file)
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use in filename
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name safe for filesystem
        """
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Remove special characters
        safe_chars = []
        for char in name:
            if char.isalnum() or char in ['_', '-']:
                safe_chars.append(char)
        
        result = ''.join(safe_chars).lower()
        
        # Limit length
        return result[:50]
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data as JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"✗ Error saving {filepath}: {e}")
    
    def _load_json(self, filepath: Path) -> Optional[Dict]:
        """Load JSON data"""
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"✗ Error loading {filepath}: {e}")
            return None


class GlobalDataManager:
    """
    Manages global data (BTTS stats, Over 2.5 stats, etc.)
    """
    
    @staticmethod
    def save_btts_stats(data: Dict):
        """Save BTTS stats"""
        stats_file = STATS_DIR / "btts_stats.json"
        data['_saved_at'] = datetime.now().isoformat()
        GlobalDataManager._save_json(stats_file, data)
    
    @staticmethod
    def load_btts_stats() -> Optional[Dict]:
        """Load BTTS stats"""
        stats_file = STATS_DIR / "btts_stats.json"
        return GlobalDataManager._load_json(stats_file)
    
    @staticmethod
    def save_over25_stats(data: Dict):
        """Save Over 2.5 stats"""
        stats_file = STATS_DIR / "over25_stats.json"
        data['_saved_at'] = datetime.now().isoformat()
        GlobalDataManager._save_json(stats_file, data)
    
    @staticmethod
    def load_over25_stats() -> Optional[Dict]:
        """Load Over 2.5 stats"""
        stats_file = STATS_DIR / "over25_stats.json"
        return GlobalDataManager._load_json(stats_file)
    
    @staticmethod
    def _save_json(filepath: Path, data: Any):
        """Save data as JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"✗ Error saving {filepath}: {e}")
    
    @staticmethod
    def _load_json(filepath: Path) -> Optional[Dict]:
        """Load JSON data"""
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"✗ Error loading {filepath}: {e}")
            return None