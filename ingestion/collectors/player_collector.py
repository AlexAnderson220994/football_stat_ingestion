"""
Collector for player data
"""

from typing import List, Set
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState
from ..utils import get_player_name_from_data


class PlayerCollector:
    """
    Collects player data
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_league_players(self) -> bool:
        """
        Collect all players in the league
        
        Returns:
            True if successful, False otherwise
        """
        # Always check for updates to player stats (even if previously complete)
        if self.state.is_collection_complete('players'):
            print("  Refreshing player stats...")
        else:
            print("  Fetching players...")
        
        self.state.mark_collection_in_progress('players')
        
        all_player_ids = set()
        page = 1
        api_calls = 0
        new_count = 0
        updated_count = 0
        
        # Get already fetched player IDs from disk
        existing_from_disk = set(self.data_manager.get_all_player_ids())
        
        while True:
            response = self.api_client.get_league_players(
                self.state.season_id,
                page=page
            )
            api_calls += 1
            
            if not response or not response.get('success'):
                print(f"  ✗ Failed to fetch players (page {page})")
                break
            
            data = response.get('data', [])
            if not data:
                break
            
            # Save ALL players (new and existing) to capture stats updates
            for player in data:
                player_id = player.get('id')
                player_name = get_player_name_from_data(player)
                
                # Determine if this is new or an update
                if player_id in existing_from_disk:
                    updated_count += 1
                else:
                    new_count += 1
                
                # Always save to capture stat updates (goals, assists, cards, etc.)
                self.data_manager.save_player(player_id, player_name, player)
                all_player_ids.add(player_id)
            
            # Progress update
            if data:
                print(f"    ✓ Page {page}: {len(data)} players processed")
            
            # Update state
            self.state.update_collection_progress(
                'players',
                fetched=len(all_player_ids.union(existing_from_disk)),
                total=len(all_player_ids.union(existing_from_disk)),
                ids=list(all_player_ids),
                api_calls=api_calls
            )
            
            # Check if there are more pages
            pager = response.get('pager', {})
            if page >= pager.get('max_page', 1):
                break
            
            page += 1
        
        total_players = len(all_player_ids.union(existing_from_disk))
        
        if new_count > 0 or updated_count > 0:
            print(f"  ✓ Players: {total_players} total ({new_count} new, {updated_count} updated)")
            self.state.mark_collection_complete('players')
            return True
        elif total_players > 0:
            print(f"  ✓ Players: {total_players} total (no changes)")
            self.state.mark_collection_complete('players')
            return True
        else:
            print("  ⚠ No players data returned")
            return False
    
    def collect_all(self) -> bool:
        """
        Collect all player data
        
        Returns:
            True if successful, False otherwise
        """
        print("\n🏃 Collecting player data...")
        
        return self.collect_league_players()