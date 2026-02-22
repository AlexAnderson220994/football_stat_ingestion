"""
Collector for league-level data (stats, table)
"""

from typing import Optional, Dict
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState


class LeagueCollector:
    """
    Collects league-level data
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_league_stats(self) -> bool:
        """
        Collect league season stats
        
        Returns:
            True if successful, False otherwise
        """
        # Always fetch to get latest data (even if previously complete)
        if self.state.is_collection_complete('league_stats'):
            print("  Refreshing league stats...")
        else:
            print("  Fetching league stats...")
        
        self.state.mark_collection_in_progress('league_stats')
        
        # Fetch from API
        response = self.api_client.get_league_stats(self.state.season_id)
        
        if not response or not response.get('success'):
            print("  ✗ Failed to fetch league stats")
            return False
        
        # Save data
        data = response.get('data', [])
        if data:
            # Usually returns a single league object
            league_data = data[0] if isinstance(data, list) else data
            self.data_manager.save_league_stats(league_data)
            
            print(f"  ✓ League stats saved")
            self.state.mark_collection_complete('league_stats')
            self.state.update_collection_progress('league_stats', fetched=1, total=1, api_calls=1)
            return True
        else:
            print("  ⚠ No league stats data returned")
            return False
    
    def collect_league_table(self) -> bool:
        """
        Collect league table/standings
        
        Returns:
            True if successful, False otherwise
        """
        # Always fetch to get latest data (even if previously complete)
        if self.state.is_collection_complete('league_table'):
            print("  Refreshing league table...")
        else:
            print("  Fetching league table...")
        
        self.state.mark_collection_in_progress('league_table')
        
        # Fetch from API
        response = self.api_client.get_league_table(self.state.season_id, include_stats=True)
        
        if not response or not response.get('success'):
            print("  ✗ Failed to fetch league table")
            return False
        
        # Save data
        data = response.get('data', [])
        if data:
            self.data_manager.save_league_table(response)
            
            print(f"  ✓ League table saved ({len(data)} teams)")
            self.state.mark_collection_complete('league_table')
            self.state.update_collection_progress('league_table', fetched=1, total=1, api_calls=1)
            return True
        else:
            print("  ⚠ No league table data returned")
            return False
    
    def collect_all(self) -> bool:
        """
        Collect all league-level data
        
        Returns:
            True if all successful, False otherwise
        """
        print("\n📊 Collecting league data...")
        
        stats_ok = self.collect_league_stats()
        table_ok = self.collect_league_table()
        
        return stats_ok and table_ok