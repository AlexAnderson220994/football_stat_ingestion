"""
Player Mapper
Maps player IDs to player names for validation
"""

from typing import Dict, Optional, List


class PlayerMapper:
    """Maps player IDs to names for lineup validation"""
    
    def __init__(self, home_players: List[Dict], away_players: List[Dict]):
        """
        Initialize mapper with player data
        
        Args:
            home_players: List of home team player dicts from API
            away_players: List of away team player dicts from API
        """
        self.player_map = {}
        
        # Build ID -> Name mapping
        for player in home_players + away_players:
            player_id = player.get('id')
            name = player.get('known_as') or player.get('full_name', '')
            
            if player_id and name:
                self.player_map[player_id] = name
    
    def get_name(self, player_id: int) -> Optional[str]:
        """Get player name from ID"""
        return self.player_map.get(player_id)
    
    def matches_name(self, player_id: int, target_name: str) -> bool:
        """
        Check if player ID matches target name
        
        Uses fuzzy matching since names might differ slightly
        (e.g., "Mohamed Salah" vs "M. Salah" vs "Salah")
        """
        actual_name = self.get_name(player_id)
        
        if not actual_name:
            return False
        
        # Normalize both names
        actual_lower = actual_name.lower()
        target_lower = target_name.lower()
        
        # Exact match
        if actual_lower == target_lower:
            return True
        
        # Check if target is contained in actual or vice versa
        # This handles "Salah" matching "Mohamed Salah"
        if target_lower in actual_lower or actual_lower in target_lower:
            return True
        
        # Check last name matching
        actual_parts = actual_lower.split()
        target_parts = target_lower.split()
        
        if actual_parts and target_parts:
            # If last names match, consider it a match
            if actual_parts[-1] == target_parts[-1]:
                return True
        
        return False
    
    def find_player_id(self, player_name: str) -> Optional[int]:
        """
        Find player ID by name (reverse lookup)
        """
        for player_id, name in self.player_map.items():
            if self.matches_name(player_id, player_name):
                return player_id
        
        return None