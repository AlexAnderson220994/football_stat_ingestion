"""
Collector for referee data
"""

from typing import List, Set
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState
from ..utils import get_referee_name_from_data


class RefereeCollector:
    """
    Collects referee data
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_league_referees(self) -> bool:
        """
        Collect all referees in the league
        
        Returns:
            True if successful, False otherwise
        """
        # Check if already complete
        if self.state.is_collection_complete('referees'):
            print("  ✓ Referees already collected")
            return True
        
        print("  Fetching referees...")
        self.state.mark_collection_in_progress('referees')
        
        # Get already fetched referee IDs
        existing_referee_ids = set(self.state.get_fetched_referee_ids())
        existing_from_disk = set(self.data_manager.get_all_referee_ids())
        already_fetched = existing_referee_ids.union(existing_from_disk)
        
        # Fetch from API (usually single page)
        response = self.api_client.get_league_referees(self.state.season_id)
        api_calls = 1
        
        if not response or not response.get('success'):
            print("  ✗ Failed to fetch referees")
            return False
        
        data = response.get('data', [])
        
        if not data:
            print("  ⚠ No referees data returned")
            return False
        
        # Filter out already fetched referees
        new_referees = [ref for ref in data if ref.get('id') not in already_fetched]
        
        # Save each referee
        for referee in new_referees:
            referee_id = referee.get('id')
            referee_name = get_referee_name_from_data(referee)
            
            self.data_manager.save_referee(referee_id, referee_name, referee)
            already_fetched.add(referee_id)
            
            print(f"    ✓ Saved {referee_name}")
        
        # Update state
        referee_ids = list(already_fetched)
        self.state.update_collection_progress(
            'referees',
            fetched=len(already_fetched),
            total=len(already_fetched),
            ids=referee_ids,
            api_calls=api_calls
        )
        
        print(f"  ✓ Referees collected: {len(already_fetched)} total")
        self.state.mark_collection_complete('referees')
        return True
    
    def collect_all(self) -> bool:
        """
        Collect all referee data
        
        Returns:
            True if successful, False otherwise
        """
        print("\n👨‍⚖️ Collecting referee data...")
        
        return self.collect_league_referees()